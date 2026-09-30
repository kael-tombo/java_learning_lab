# ANTI-PATTERNS: Data Architecture & Persistence
## Lab 17 | Production Engineering Academy

---

## Anti-Pattern 1: Two-Phase Commit (XA Transactions) Across Microservices

### The Mistake
Using Atomikos / Bitronix / Narayana distributed transaction managers to span JTA/XA 2PC transactions across multiple independent microservices and databases.

### Why It Fails
- XA transactions hold database row locks during the entire two-phase commit protocol across the network.
- If a network partition occurs during the prepare phase, locks remain held until human manual intervention.
- System availability degrades exponentially as microservices scale.

### The Correct Production Fix
Use the **Saga Pattern** with asynchronous compensating transactions and eventual consistency.

---

## Anti-Pattern 2: Non-Idempotent Compensating Actions

### The Mistake
Writing a compensating refund or restock action that blindly adds funds or inventory without checking idempotency:
```java
public void compensate(String orderId, double amount) {
    accountBalance += amount; // If retried 3 times on network timeout, credits 3x the money!
}
```

### Why It Fails
In distributed systems, networks time out. Compensating transactions will be retried automatically. If not idempotent, retries corrupt financial balances and inventory records.

### The Correct Production Fix
Always record compensation IDs and execute conditional atomic updates.
