# INTERVIEW QUESTIONS: Distributed Systems Resilience
## Lab 04 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: Explain the three states of a Circuit Breaker and how state transitions work.
**Answer**:
1. **CLOSED**: Normal operation. Requests flow directly to downstream service. Failure count or rate is tracked within a sliding window (e.g., last 100 calls).
2. **OPEN**: When failure or slow-call rate exceeds threshold (e.g. 50%), the breaker trips to OPEN. All subsequent requests fail fast immediately without making network calls, invoking the local fallback. This gives downstream services breathing room to recover.
3. **HALF-OPEN**: After a configured sleep window (e.g. 5 seconds), the breaker transitions to HALF-OPEN. It permits a limited number of trial probe requests (e.g. 10 calls). If the probe calls succeed, it resets to CLOSED. If any probe call fails, it trips back to OPEN.

### Q2: Why is "exponential backoff with jitter" superior to plain exponential backoff?
**Answer**:
Plain exponential backoff delays callers by $B \times 2^{\text{attempt}}$ (e.g. 100ms, 200ms, 400ms). If a large batch of concurrent requests fail at the same moment, plain backoff maintains lock-step synchronization: all clients retry at $t=100\text{ms}$, fail again, and retry together at $t=300\text{ms}$. Jitter adds a random offset ($\text{random}(0, \text{backoff})$), distributing retry arrivals uniformly across the timeline and eliminating destructive load resonance.

---

## Staff / Principal Level (8+ Years)

### Q3: How do you design an idempotent payment processing system that guarantees exactly-once business outcome despite unreliable networks?
**Answer**:
1. **Client-Generated Idempotency Key**: Client generates a cryptographic UUID before initiating the request and passes it via `Idempotency-Key` header.
2. **Atomic Lock / Reservation in Distributed Store**: Server checks Redis or SQL using atomic conditional insert (`INSERT INTO idempotency_records (key, status, created_at) VALUES (?, 'IN_PROGRESS', NOW()) ON CONFLICT DO NOTHING`).
   - If insert fails: return existing status (`IN_PROGRESS` returns 409 or polls; `COMPLETED` returns cached response).
3. **Transactional Execution**: Server processes payment against payment gateway, records the authorization code in the database, and updates idempotency record to `COMPLETED` with stored response payload in the same transactional boundary.
4. **Network Partition Handling**: If the caller times out, they safely retry with the identical `Idempotency-Key`. The server identifies the key, recognizes it has already completed, and returns the cached success response without charging the card again.

### Q4: What is "Request Hedging" and what are the trade-offs at massive scale?
**Answer**:
Request hedging reduces tail latency (p99/p99.9) by sending a duplicate speculative request to an alternate replica if the first request hasn't responded within a threshold (e.g. p90 latency).
- **Pros**: Drastically reduces tail latency spikes caused by GC, node contention, or disk stutter.
- **Cons & Risks**: Increases total cluster load by 10-15%. If the system is already overloaded (over-saturated CPU), sending duplicate speculative requests causes death-spiral saturation.
- **Mitigation**: Hedge only if cluster CPU is below 60% and limit the hedge rate via token bucket.
