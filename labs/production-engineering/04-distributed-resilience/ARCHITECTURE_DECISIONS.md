# ARCHITECTURE DECISIONS: Distributed Resilience & Fault Tolerance
## Lab 04 | Production Engineering Academy

---

## ADR-01: Microservices Communication & Fault Tolerance Standard

### Status: ACCEPTED

### Context
Our distributed architecture comprises over 80 independent microservices communicating via synchronous REST/JSON and asynchronous Kafka events. In 2025, cascading failures originating in downstream payment and inventory databases accounted for 64% of total customer-facing downtime.

### Decisions
1. **Mandatory Strict Timeouts on All Sockets**:
   - Connection Timeout: Maximum $500\text{ms}$.
   - Read/Request Timeout: Strict deadline based on $3\times$ measured p99 of the target API, capped at $2,000\text{ms}$.
   - No HTTP client may ship to production with default unconfigured (infinite) timeouts.
2. **Circuit Breakers as Architectural Standard**:
   - Every outbound synchronous client must be wrapped in a Resilience4j Circuit Breaker.
   - Default threshold: 50% failure rate over 50 calls; 5s open state duration.
3. **Idempotency Header Requirement**:
   - All state-mutating APIs (POST / PATCH) must require an `Idempotency-Key: <UUID>` header.
   - The server must cache the idempotency key in Redis with a 24-hour TTL and return the exact previous response if a duplicate request arrives.
4. **Retry Budgeting**:
   - Retries are limited to a maximum of 2 attempts.
   - Retries MUST use exponential backoff with full random jitter.
   - Overall retry budget capped at 10% of total outbound requests to prevent retry amplification during outages.

### Consequences
- Downstream failures are isolated within 2-3 seconds instead of cascading across the entire cluster.
- Prevents double-charging and duplicate transactions during network partitions.
- Slight developer overhead to configure resilience wrappers and idempotency interceptors.
