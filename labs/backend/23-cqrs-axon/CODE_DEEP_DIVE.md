# Code Deep Dive: Axon Framework

## Aggregate root

```java
@Aggregate
public class OrderAggregate {
    @AggregateIdentifier private String orderId;
    private OrderStatus status;
    private int totalCents;
    private Long version;

    @CreationPolicy(REQUIRED)                       // exactly one factory per aggregate id
    @CommandHandler
    public OrderAggregate(PlaceOrderCommand cmd) {
        if (cmd.totalCents() < 0) throw new IllegalArgumentException("negative total");
        AggregateLifecycle.apply(new OrderPlacedEvent(cmd.orderId(), cmd.totalCents()));
    }

    @EventSourcingHandler
    void on(OrderPlacedEvent e) { this.orderId = e.orderId(); this.status = NEW; this.totalCents = e.totalCents(); }

    @CommandHandler
    public void handle(PayOrderCommand cmd) {
        if (status != NEW) throw new IllegalStateException("already settled");
        AggregateLifecycle.apply(new OrderPaidEvent(orderId, cmd.paymentId()));
    }

    @EventSourcingHandler
    void on(OrderPaidEvent e) { this.status = PAID; }
}
```

Pitfalls: doing work in `@CommandHandler` that belongs in `@EventSourcingHandler`
(side effects then don't replay), or throwing from the event handler after
apply (state already mutated).

## Command gateway

```java
@Service
public class OrderService {
    private final CommandGateway gateway;
    public CompletableFuture<String> place(PlaceOrderCommand cmd) {
        return gateway.send(cmd);                   // routed to aggregate by @TargetAggregateIdentifier
    }
}
```

Annotate the command id with `@TargetAggregateIdentifier` — without it Axon
cannot route and throws `NoHandlerForCommandException` at runtime.

## Projection with idempotency

```java
@Component
@ProcessingGroup("order-read-model")
@Transactional
public class OrderProjection {
    @EventHandler
    void on(OrderPlacedEvent e) {
        if (repo.existsById(e.orderId())) return;   // at-least-once → must dedupe
        repo.save(new OrderRow(e.orderId(), NEW, e.totalCents()));
    }

    @EventHandler
    void on(OrderPaidEvent e) {
        repo.findById(e.orderId()).ifPresent(o -> { o.status = PAID; });
    }
}
```

Pitfall: tracking processors checkpoint offsets; a handler that throws inside
the same transaction rolls the projection back *and* the checkpoint, but a
side-effecting one (email, Kafka) cannot roll back — put those on a separate
`@EventProcessingGroup` with its own idempotency key.

## Saga for cross-aggregate flow

```java
@Saga
public class OrderFulfillmentSaga {
    @StartSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void on(OrderPlacedEvent e) {
        SagaLifecycle.associateWith("orderId", e.orderId());
        commandGateway.send(new ReserveInventoryCommand(e.orderId(), e.items()));
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void on(InventoryReservedEvent e) {
        commandGateway.send(new ShipOrderCommand(e.orderId()));
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void on(InventoryUnavailableEvent e) {
        commandGateway.send(new CancelOrderCommand(e.orderId(), "no stock"));
        SagaLifecycle.end();
    }
}
```

Pitfall: association property missing → saga never starts; handlers that
mutate the saga state outside `@EndSaga` leave the saga open forever.

## Outbox for dual-write safety

```java
@EventHandler
@Transactional(propagation = REQUIRES_NEW)
void on(OrderPlacedEvent e) {
    outboxRepo.save(new OutboxRow(e.orderId(), JSON, "OrderPlaced")); // same TX as projection
}
```

A relay (Debezium, poller) publishes outbox rows to Kafka; crash-safe because
projection + outbox commit atomically.

## Upcaster for event evolution

```java
@Component
public class OrderEventUpcaster implements SingleEventUpcaster {
    @Override public boolean canUpcast(IntermediateEventRepresentation r) {
        return r.getType().getName().equals("OrderPlacedEvent") && r.getType().getRevision().equals("0");
    }
    @Override public IntermediateEventRepresentation doUpcast(IntermediateEventRepresentation r) {
        // v0 → v1: rename total -> totalCents
        JsonTree payload = r.getData();
        payload.get("totalCents"); // copy semantics …
        return r.upcastPayload(...);
    }
}
```

Pitfall: editing the event record's Java source breaks deserialization of
stored history. Add the upcaster instead; never rewrite stored events in
place on a production log.
