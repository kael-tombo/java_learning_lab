# Mock Interview: Circuit Breaker Pattern

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Designing resilient microservice communication

**Interviewer**: "Our payment service sometimes takes 30 seconds to respond, causing cascading timeouts across dependent services. How do you prevent this?"

**Candidate**: "I'd implement the circuit breaker pattern. When the payment service starts failing or becoming slow, the circuit breaker 'opens' and subsequent calls fail fast without waiting for the timeout."

**Interviewer**: "Walk me through the circuit breaker states."

**Candidate**: "Three states: CLOSED — normal operation, requests pass through. OPEN — failures exceed threshold, requests fail immediately. HALF-OPEN — after a timeout, a trial request checks if the service has recovered. Success → CLOSED. Failure → OPEN again. The thresholds and timeouts are configurable based on the service's SLOs."

**Interviewer**: "How do you configure the circuit breaker?"

**Candidate**: "Configuration is service-specific. For the payment service with a 10-second P99: sliding window of 100 calls, failure threshold of 50% (if 50 of 100 calls fail, open the circuit), wait duration in OPEN state of 30 seconds, and 5 trial calls in HALF-OPEN. I'd start conservative and tune based on production data."

**Interviewer**: "How does the circuit breaker interact with retry logic?"

**Candidate**: "Carefully. Retry should only happen when the circuit is CLOSED. If the circuit is OPEN, retrying would defeat the purpose — the circuit breaker is telling you the service is down, retrying will waste resources. I'd implement: if CLOSED → retry with exponential backoff up to 3 times. If OPEN → fail fast (don't retry). On transition to HALF-OPEN → allow trial requests (which are effectively retries)."

**Interviewer**: "What about the bulkhead pattern?"

**Candidate**: "Bulkhead isolates resources so a failure in one part doesn't consume all resources. For the payment service, I'd configure a bulkhead with a thread pool of 10 threads and a queue of 20. If all threads are busy serving payment calls, new calls are immediately rejected rather than queuing indefinitely. This prevents the payment service from consuming all application threads."

**Interviewer**: "How do you handle the fallback when the circuit is open?"

**Candidate**: "The fallback behavior depends on criticality. Options: (1) Return a cached response — serve stale data. (2) Return a default — 'payment status unknown, check later.' (3) Queue the request for later processing. (4) Route to an alternative provider. For payment processing, I'd queue the request and notify the user that there's a delay, rather than silently failing."

**Interviewer**: "How do you monitor circuit breaker effectiveness?"

**Candidate**: "Track: (1) Circuit state transitions — how often does each service's circuit open? (2) Time in OPEN state — how long does recovery take? (3) Request volume during OPEN — are we failing fast effectively? (4) Fallback rate — how often are fallbacks triggered? A dashboard showing circuit breaker states across all services helps identify systemic issues."

---

## Key Takeaways

- Circuit breaker prevents cascading failures by failing fast
- Three states: CLOSED (normal), OPEN (failing fast), HALF-OPEN (trial)
- Retry only when CLOSED; fail fast when OPEN
- Bulkhead isolates resources to prevent resource exhaustion
- Monitor circuit state transitions and fallback rates

---

## Evaluation Criteria

The interviewer assesses:
- **Architecture thinking**: Clear decomposition into meaningful boundaries
- **Trade-off awareness**: Understanding of when this pattern helps vs hurts
- **Failure handling**: Proactive identification of failure modes
- **Operational maturity**: Discussion of monitoring, deployment, and operations
- **Communication**: Ability to explain complex concepts clearly


## Staff+ Level Expectations

At the staff+ level, the interviewer expects you to:
- Challenge their assumptions and ask clarifying questions
- Discuss organizational implications (team boundaries, Conway's Law)
- Address data consistency challenges proactively
- Consider migration and evolution strategy
- Discuss cost and operational trade-offs
- Connect technical decisions to business outcomes

## Common Follow-Up Questions

1. ""How would this design change at 100x scale?"" — Discuss partitioning, caching, read replicas
2. ""How do you handle schema evolution?"" — Backward compatibility, versioning, migration strategies
3. ""Whats the biggest risk in this architecture?"" — Identify the weakest link and mitigation
4. ""How would you migrate from the current system?"" — Strangler Fig, feature toggles, parallel run
5. ""How do you test this system?"" — Unit, integration, contract, and end-to-end testing strategies

## Key Takeaways

This mock interview demonstrates the depth of discussion expected at staff+ level. The interviewer is not looking for a single ""correct"" answer but rather evaluating your thought process, trade-off awareness, and ability to communicate complex architectural decisions clearly.

