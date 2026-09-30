# EXERCISES: Distributed Resilience & Fault Tolerance
## Lab 04 | Production Engineering Academy

---

## Exercise 1: Implement Idempotent Payment Consumer with Redis & PostgreSQL

### Objective
Build a fault-tolerant payment consumer that handles duplicate deliveries and network timeouts safely.

### Specification
1. Create a Java Spring Boot / JDBC service with endpoint `POST /api/v1/payments`.
2. Headers required: `Idempotency-Key: UUID`.
3. If duplicate key arrives within 24 hours:
   - If currently processing: return HTTP 425 / 409 Conflict with `Retry-After: 2` header.
   - If already completed: return original HTTP 200 payload directly from cache.
4. Simulate downstream payment gateway failure by randomly sleeping 5 seconds on 30% of requests.
5. Wrap the call with Resilience4j CircuitBreaker with a timeout of 1,000ms.
6. Write a JUnit test with 50 concurrent threads firing identical idempotency keys; verify that the payment gateway is called exactly once.

---

## Exercise 2: Chaos Injection with Toxiproxy

### Objective
Demonstrate cascading failure vs resilient recovery under injected network delay.

### Steps
1. Run Toxiproxy docker container: `ghcr.io/shopify/toxiproxy`.
2. Configure a downstream microservice mock behind Toxiproxy.
3. Inject 2,500ms latency toxic:
   ```bash
   toxiproxy-cli toxic add -t latency -a latency=2500 downstream_mock
   ```
4. Fire 200 concurrent requests against your client without circuit breaker: observe thread pool exhaustion and out-of-memory.
5. Enable Resilience4j Bulkhead + CircuitBreaker: observe that 10 requests time out, the circuit breaker opens, and the remaining 190 requests fail fast with fallback in $< 5\text{ms}$.
