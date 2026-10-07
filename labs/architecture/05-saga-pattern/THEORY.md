# Saga Pattern Theory

## Core Concepts

### Local Transaction
Each service performs its own database operation independently.
```java
@Transactional
public void reserveInventory(ReserveInventoryCommand cmd) {
    Product product = productRepository.findById(cmd.productId())
        .orElseThrow();
    product.reserve(cmd.quantity());
    productRepository.save(product);
}
```

### Compensating Transaction
An action that undoes a previous local transaction.
```java
@Transactional
public void compensateReservation(ReleaseInventoryCommand cmd) {
    Product product = productRepository.findById(cmd.productId())
        .orElseThrow();
    product.release(cmd.quantity()); // Undo the reservation
    productRepository.save(product);
}
```

## Saga Types

### Choreography-based Saga
```java
// Service 1: Order Service publishes event
public void createOrder(CreateOrderCommand cmd) {
    orderRepository.save(new Order(cmd.orderId(), cmd.customerId()));
    eventPublisher.publish(new OrderCreatedEvent(cmd.orderId(), cmd.productId(), cmd.quantity()));
}

// Service 2: Inventory Service responds
@EventListener
public void on(OrderCreatedEvent event) {
    try {
        inventoryService.reserve(event.productId(), event.quantity());
        eventPublisher.publish(new InventoryReservedEvent(event.orderId()));
    } catch (Exception e) {
        eventPublisher.publish(new InventoryReservationFailedEvent(event.orderId()));
    }
}

// Service 1: Handles failure
@EventListener
public void on(InventoryReservationFailedEvent event) {
    orderService.rejectOrder(event.orderId()); // Compensating action
}
```

### Orchestration-based Saga
```java
@Component
public class OrderSagaOrchestrator {

    @Autowired
    private CommandGateway commandGateway;

    @Saga
    public void handle(CreateOrderCommand cmd) {
        // Step 1: Reserve inventory
        commandGateway.send(new ReserveInventoryCommand(cmd.orderId(), cmd.productId()));
        // Saga waits for response
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void handle(InventoryReservedEvent event) {
        // Step 2: Process payment
        commandGateway.send(new ProcessPaymentCommand(event.orderId(), event.amount()));
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void handle(PaymentProcessedEvent event) {
        // Step 3: Confirm order
        commandGateway.send(new ConfirmOrderCommand(event.orderId()));
        // Saga ends successfully
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void handle(PaymentFailedEvent event) {
        // Compensate: Release inventory
        commandGateway.send(new ReleaseInventoryCommand(event.orderId()));
        // Saga ends with failure
    }
}
```

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Pattern: Saga — Microservices.io (undated living pattern reference; accessed Oct 2026) — (link removed)saga.html — Choreography (domain events trigger next step) vs orchestration (central orchestrator sends command/reply) maps directly onto this lab's two Java saga listings; choose choreography for simple flows, orchestration when the step graph branches.
- Pattern: Saga — Microservices.io (undated living pattern reference; accessed Oct 2026) — (link removed)saga.html — No automatic rollback: every step followed by a fallible step needs an explicit compensating transaction, which is exactly what the lab's `compensateReservation` / `rejectOrder` handlers model — audit that each forward step has its compensator.
- Pattern: Saga — Microservices.io (undated living pattern reference; accessed Oct 2026) — (link removed)saga.html — Each step must atomically update its DB *and* publish the event (Transactional Outbox or Event Sourcing); the lab's bare `eventPublisher.publish(...)` calls after `save(...)` need an outbox in production to avoid publish-after-commit gaps.
