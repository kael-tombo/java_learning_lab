# ANTI-PATTERNS: Distributed Systems Resilience
## Lab 04 | Production Engineering Academy

---

## Anti-Pattern 1: Unjittered Retries (Synchronized Spike Storm)

### The Mistake
Retrying on a fixed schedule (e.g. retry after exactly 1,000ms).

```java
// FATAL: Causes all failed callers to retry at the exact same millisecond
public void retryFixed(Runnable action) {
    for (int attempt = 0; attempt < 3; attempt++) {
        try {
            action.run();
            return;
        } catch (Exception e) {
            Thread.sleep(1000); // Constant delay: locks callers into synchronized waves!
        }
    }
}
```

### Why It Fails
If 5,000 requests fail simultaneously due to a brief GC pause or network hiccup, all 5,000 threads wake up exactly 1,000ms later and slam the recovering dependency simultaneously. This creates massive periodic traffic pulses, preventing the server from ever recovering.

### The Correct Production Fix
Use **Decorrelated Full Jitter**:
$$\text{sleep} = \text{random}(0, \min(M, B \times 2^{\text{attempt}}))$$
This spreads out the retry load uniformly across time.

---

## Anti-Pattern 2: Retrying Non-Idempotent Operations

### The Mistake
Automatically retrying HTTP POST operations or non-idempotent business calls when a network socket timeout occurs.

### Why It Fails
A timeout does NOT mean the remote server failed to execute the request; it only means the client did not receive the response in time. The request may have been committed in the database! Retrying the POST results in:
- Double charging customer credit cards
- Duplicate order creation
- Inventory discrepancies

### The Production Rule
1. Only retry **idempotent** HTTP methods (GET, PUT, DELETE) or requests carrying a unique **Idempotency-Key** header verified by the receiver.
2. If non-idempotent and timeout occurs, transition to an uncertain state (`PENDING_RECONCILIATION`) and trigger asynchronous out-of-band verification.

---

## Anti-Pattern 3: Nested Retries Across Multi-Tier Microservices

### The Mistake
Service A calls Service B with 3 retries. Service B calls Service C with 3 retries. Service C calls Service D with 3 retries.

### Why It Fails
The total number of requests scales exponentially:
$$3 \times 3 \times 3 = 27\text{ requests per customer click!}$$
A transient failure in Service D causes upstream services to amplify traffic by 2,700%, guaranteeing the permanent collapse of the entire architecture.

### The Production Rule
Implement retries **only at the outermost boundary** or **only at the direct caller**, never at every layer in the call chain.
