# ANTI-PATTERNS: Event-Driven & Kafka Architecture
## Lab 11 | Production Engineering Academy

---

## Anti-Pattern 1: Dual-Writing (Writing to DB, then Calling Kafka Producer)

### The Mistake
```java
@Transactional
public void createOrder(OrderRequest req) {
    orderRepository.save(new Order(req)); // DB Write
    kafkaTemplate.send("orders", req.toJson()); // External Network Write
}
```

### Why It Fails
1. **Network Crash Scenario**: The database transaction commits successfully, but the network to Kafka drops or Kafka broker rejects the write. The order exists in DB, but the event is never published! Downstream billing and inventory never fulfill the order.
2. **Crash Before Commit**: `kafkaTemplate.send()` succeeds, but the database rolls back on constraint violation or power failure. Downstream consumers charge the customer for an order that does not exist in the database!

### The Correct Production Fix
Use the **Transactional Outbox Pattern**:
Write both the order entity and an `OutboxEvent` entity within the same single ACID database transaction. Read the outbox via Change Data Capture (Debezium) or an async forwarder.

---

## Anti-Pattern 2: Hot Partition Keys (Severe Data Skew)

### The Mistake
Using a coarse or non-uniform partition key, such as `country_code` or `tenant_type`:
```java
// BAD: 90% of customers are in "US"
kafkaTemplate.send("orders", order.getCountryCode(), orderPayload);
```

### Why It Fails
All US transactions hash to the exact same partition (e.g. Partition 3).
- Partition 3 receives 90,000 req/s while Partitions 0, 1, 2 receive 500 req/s.
- The single consumer assigned to Partition 3 experiences massive lag and CPU starvation, while other consumer pods sit idle.

### The Correct Production Fix
Use fine-grained composite partition keys with high entropy, such as `customerId` or `orderId`.
