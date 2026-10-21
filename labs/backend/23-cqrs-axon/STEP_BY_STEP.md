# Step by Step: CQRS Axon

## Step 1: Define Command
`java
@TargetAggregateIdentifier
public record CreateOrderCommand(String orderId, String customerId, List<OrderItem> items) {}
`

## Step 2: Define Event
`java
public record OrderCreatedEvent(String orderId, String customerId, List<OrderItem> items, Instant createdAt) {}
`

## Step 3: Create Aggregate
`java
@Aggregate
public class OrderAggregate {
    @AggregateIdentifier
    private String orderId;
    private OrderStatus status;

    @CommandHandler
    public OrderAggregate(CreateOrderCommand cmd) {
        apply(new OrderCreatedEvent(cmd.orderId(), cmd.customerId(), cmd.items(), Instant.now()));
    }

    @EventSourcingHandler
    public void on(OrderCreatedEvent event) {
        this.orderId = event.orderId();
        this.status = OrderStatus.CREATED;
    }
}
`

## Step 4: Create Projection
`java
@Component
public class OrderProjection {
    @EventHandler
    public void on(OrderCreatedEvent event) {
        // Update read model in database
    }
}
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\23-cqrs-axon "CODE_DEEP_DIVE.md") @"
# Code Deep Dive: CQRS Axon

## Aggregate Lifecycle
1. Create command sent to CommandBus
2. CommandBus routes to @CommandHandler constructor
3. Constructor calls apply(event) which publishes to EventBus
4. EventStore persists the event
5. @EventSourcingHandler updates aggregate state
6. Aggregate is now initialized

## Event Sourcing Handler
@EventSourcingHandler methods are called in order of events during both:
- Regular event application (current aggregate creation)
- Aggregate reconstruction from event store (loading)

## Saga Execution
Saga instances are managed by SagaManager:
1. Saga is created when @StartSaga event handler fires
2. Association values link saga to events
3. @SagaEventHandler methods process related events
4. Saga ends when @EndSaga condition is met
