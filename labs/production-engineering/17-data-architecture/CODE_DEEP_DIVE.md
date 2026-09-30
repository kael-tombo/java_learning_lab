# CODE DEEP DIVE: Saga Orchestration & Distributed State Patterns
## Lab 17 | Production Engineering Academy

---

## Pattern 1: Idempotent Saga State Machine Orchestrator

```java
package com.learning.production.lab17;

import java.util.UUID;
import java.util.concurrent.CompletableFuture;

public class OrderSagaOrchestrator {
    private final InventoryServiceClient inventoryClient;
    private final PaymentServiceClient paymentClient;
    private final SagaLogRepository sagaRepository;

    public OrderSagaOrchestrator(
            InventoryServiceClient inventoryClient,
            PaymentServiceClient paymentClient,
            SagaLogRepository sagaRepository) {
        this.inventoryClient = inventoryClient;
        this.paymentClient = paymentClient;
        this.sagaRepository = sagaRepository;
    }

    public enum SagaState { STARTED, INVENTORY_RESERVED, PAYMENT_CHARGED, COMPLETED, COMPENSATING, FAILED }

    public record SagaLog(UUID sagaId, String orderId, SagaState state, String failureReason) {}

    public CompletableFuture<Boolean> executeOrderSaga(String orderId, double amount, String itemId, int quantity) {
        UUID sagaId = UUID.randomUUID();
        sagaRepository.save(new SagaLog(sagaId, orderId, SagaState.STARTED, null));

        // Step 1: Reserve Inventory
        return inventoryClient.reserveInventory(sagaId, itemId, quantity)
                .thenCompose(reserved -> {
                    if (!reserved) {
                        sagaRepository.updateState(sagaId, SagaState.FAILED, "Inventory Unavailable");
                        return CompletableFuture.completedFuture(false);
                    }
                    sagaRepository.updateState(sagaId, SagaState.INVENTORY_RESERVED, null);

                    // Step 2: Charge Payment
                    return paymentClient.chargePayment(sagaId, amount)
                            .thenCompose(paid -> {
                                if (paid) {
                                    sagaRepository.updateState(sagaId, SagaState.COMPLETED, null);
                                    return CompletableFuture.completedFuture(true);
                                } else {
                                    // Step 3 (Compensate): Payment failed -> Release Inventory
                                    sagaRepository.updateState(sagaId, SagaState.COMPENSATING, "Payment Declined");
                                    return compensateInventory(sagaId, itemId, quantity)
                                            .thenApply(v -> false);
                                }
                            });
                })
                .exceptionallyCompose(ex -> {
                    // Unhandled exception / timeout -> Compensate
                    sagaRepository.updateState(sagaId, SagaState.COMPENSATING, ex.getMessage());
                    return compensateInventory(sagaId, itemId, quantity).thenApply(v -> false);
                });
    }

    private CompletableFuture<Void> compensateInventory(UUID sagaId, String itemId, int quantity) {
        return inventoryClient.releaseInventory(sagaId, itemId, quantity)
                .thenAccept(v -> sagaRepository.updateState(sagaId, SagaState.FAILED, "Compensated"));
    }
}
```

---

## Pattern 2: Read-Your-Own-Writes Token Validator (CQRS Gateway)

```java
package com.learning.production.lab17;

import java.time.Instant;

public class ReadYourOwnWritesRouter {
    private static final long WRITE_REPLICATION_WINDOW_MS = 5000; // 5 seconds

    public record UserWriteSession(long userId, Instant lastWriteTimestamp) {}

    /**
     * Determines whether to route read query to read replica or primary database.
     */
    public boolean shouldRouteToPrimary(UserWriteSession session) {
        if (session == null || session.lastWriteTimestamp() == null) {
            return false; // Safe to read from eventual consistency read replica
        }

        long elapsed = Instant.now().toEpochMilli() - session.lastWriteTimestamp().toEpochMilli();
        // If user recently wrote data within replication window, read from primary to ensure consistency
        return elapsed < WRITE_REPLICATION_WINDOW_MS;
    }
}
```
