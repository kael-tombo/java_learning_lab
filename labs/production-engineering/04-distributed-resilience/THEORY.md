# THEORY: Distributed Systems Failures & Resilience
## Lab 04 | Production Engineering Academy

---

## 1. The 8 Fallacies of Distributed Computing

Peter Deutsch's list — every distributed system architect must internalize these:

1. **The network is reliable** — packets drop, routers fail, cables break
2. **Latency is zero** — even "local" network calls take 1-10ms
3. **Bandwidth is infinite** — sending large payloads is expensive
4. **The network is secure** — man-in-the-middle attacks are real
5. **Topology doesn't change** — IPs change, services scale up/down
6. **There is one administrator** — in microservices, multiple teams own services
7. **Transport cost is zero** — serialization, network, infrastructure have costs
8. **The network is homogeneous** — different services use different protocols

**Implication**: You MUST design for failure. Everything will fail. Eventually.

---

## 2. CAP Theorem — The Fundamental Tradeoff

In a distributed system, you can only guarantee 2 of 3:

```
         C (Consistency)
        / \
       /   \
      /     \
     /  CAP  \
    /         \
   A-----------P
(Availability) (Partition
               Tolerance)
```

- **C (Consistency)**: Every read returns the most recent write or an error
- **A (Availability)**: Every request gets a response (not necessarily latest data)
- **P (Partition Tolerance)**: System operates even when network partition occurs

**The practical reality**: Network partitions WILL happen. So you choose CP or AP.

| System | Choice | When Partition Occurs |
|--------|--------|----------------------|
| PostgreSQL (cluster) | CP | Returns error (sacrifices availability) |
| Cassandra | AP | Returns stale data (sacrifices consistency) |
| DynamoDB | AP (by default) | Returns stale data |
| ZooKeeper | CP | Refuses requests if quorum not reached |
| MongoDB | CP | Primary election takes time |

---

## 3. Resilience Patterns

### 3.1 Circuit Breaker — The Fuse Box

```
CLOSED state (normal):
  Requests pass through. Failures counted.
  If failures > threshold → OPEN

OPEN state (failure):
  All requests REJECTED immediately (fail fast)
  No load to failing service
  After waitDuration → HALF-OPEN

HALF-OPEN state (testing):
  N requests allowed through as probe
  If probe succeeds → CLOSED (recovered)
  If probe fails → OPEN (still failing)
```

```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)           // Open if 50% fail
    .slowCallRateThreshold(80)          // Also open if 80% are slow
    .slowCallDurationThreshold(Duration.ofSeconds(2))  // "Slow" threshold
    .waitDurationInOpenState(Duration.ofSeconds(30))   // How long to stay open
    .slidingWindowType(COUNT_BASED)     // Count last N calls
    .slidingWindowSize(10)              // Last 10 calls
    .minimumNumberOfCalls(5)            // Need 5 calls before evaluating
    .permittedNumberOfCallsInHalfOpenState(3)
    .build();

CircuitBreaker cb = CircuitBreaker.of("payment-gateway", config);

// Usage
cb.executeCallable(() -> paymentGateway.charge(request));

// With fallback
Try.of(CircuitBreaker.decorateCheckedSupplier(cb, () -> primaryService.call()))
   .recover(CallNotPermittedException.class, e -> fallbackService.call())
   .recover(Exception.class, e -> cachedResult)
   .get();
```

### 3.2 Retry with Exponential Backoff + Jitter

```java
RetryConfig retryConfig = RetryConfig.custom()
    .maxAttempts(3)
    .waitDuration(Duration.ofMillis(200))           // Base: 200ms
    .intervalFunction(IntervalFunction.ofExponentialRandomBackoff(
        200,    // base
        2.0,    // multiplier
        0.5,    // jitter factor (±50%)
        5000    // max wait 5 seconds
    ))
    // Retry only on retriable errors
    .retryOnException(e -> e instanceof SocketTimeoutException
                         || e instanceof ServiceUnavailableException)
    // Do NOT retry on business errors
    .ignoreException(e -> e instanceof ValidationException
                        || e instanceof AuthorizationException)
    .build();

// Retry sequence example:
// Attempt 1: immediate
// Attempt 2: wait 200ms ± 100ms (jitter)
// Attempt 3: wait 400ms ± 200ms
// Fail: total 600ms spent in retries
```

### 3.3 Bulkhead — Isolation

```java
// Thread pool bulkhead: separate pool per downstream service
ThreadPoolBulkheadConfig config = ThreadPoolBulkheadConfig.custom()
    .maxThreadPoolSize(10)    // Max 10 concurrent calls to this service
    .coreThreadPoolSize(5)
    .queueCapacity(50)        // Queue up to 50 waiting calls
    .build();

ThreadPoolBulkhead bulkhead = ThreadPoolBulkhead.of("fraud-service", config);

// Effect: even if fraud-service is slow, it only occupies 10 threads
// API threads are NOT blocked — they fail fast at bulkhead limit
// Other services unaffected
```

### 3.4 Timeout — The Most Important Pattern

```java
// ALWAYS set timeouts on EVERY external call
// No timeout = thread leaks when downstream is slow

// Spring RestTemplate
restTemplate.setRequestFactory(new HttpComponentsClientHttpRequestFactory() {{
    setConnectTimeout(1000);    // TCP connection: 1s max
    setReadTimeout(3000);       // Response: 3s max
}});

// WebClient (reactive)
webClient.get()
    .uri("/resource")
    .retrieve()
    .bodyToMono(String.class)
    .timeout(Duration.ofSeconds(3))  // 3s overall timeout
    .onErrorResume(TimeoutException.class, e -> Mono.just("timeout-fallback"));

// CompletableFuture
CompletableFuture.supplyAsync(() -> slowService.call())
    .completeOnTimeout("default", 3, TimeUnit.SECONDS)
    .orTimeout(5, TimeUnit.SECONDS);  // Hard abort at 5s
```

---

## 4. Distributed Transactions

### 4.1 The Problem

Two-phase commit (2PC) is theoretically correct but:
- Coordinator is single point of failure
- Locks resources across services during vote phase (low throughput)
- In microservices: services have different DBs, 2PC not practical

### 4.2 Saga Pattern — The Production Solution

```
Choreography Saga:
  Service A completes → publishes event → Service B starts
  Service B fails → publishes compensation event → Service A compensates

  PRO: No central coordinator
  CON: Complex flow tracking, hard to debug

Orchestration Saga:
  Saga Orchestrator → tells Service A to execute step 1
                   → tells Service B to execute step 2
  Service B fails → Orchestrator → tells Service A to compensate step 1

  PRO: Clear flow, easier to monitor
  CON: Orchestrator is critical path, needs to be reliable
```

```java
// Orchestration Saga example
@Service
public class OrderSagaOrchestrator {

    public void createOrder(CreateOrderCommand cmd) {
        SagaState state = sagaRepository.save(new SagaState(cmd.orderId()));

        try {
            // Step 1: Reserve inventory
            inventoryService.reserve(cmd.productId(), cmd.quantity());
            state.markStep("INVENTORY_RESERVED");

            // Step 2: Process payment
            paymentService.charge(cmd.userId(), cmd.amount());
            state.markStep("PAYMENT_PROCESSED");

            // Step 3: Create order record
            Order order = orderService.create(cmd);
            state.markComplete(order.id());

        } catch (Exception e) {
            compensate(state, cmd);  // Roll back completed steps
            throw new SagaFailedException(e);
        }
    }

    private void compensate(SagaState state, CreateOrderCommand cmd) {
        if (state.hasStep("PAYMENT_PROCESSED")) {
            paymentService.refund(cmd.userId(), cmd.amount());  // Compensating action
        }
        if (state.hasStep("INVENTORY_RESERVED")) {
            inventoryService.release(cmd.productId(), cmd.quantity());
        }
    }
}
```

---

## 5. Idempotency — Design for Retry Safety

```java
// Problem: payment API called twice (retry) → double charge

// Solution: Idempotency keys
@PostMapping("/payments")
public ResponseEntity<PaymentResult> createPayment(
        @RequestHeader("Idempotency-Key") String idempotencyKey,
        @RequestBody PaymentRequest req) {

    // Check if already processed
    Optional<PaymentResult> existing = idempotencyStore.get(idempotencyKey);
    if (existing.isPresent()) {
        return ResponseEntity.ok(existing.get());  // Return same result, no duplicate charge
    }

    // Process payment
    PaymentResult result = paymentProcessor.charge(req);

    // Store result linked to key (with TTL)
    idempotencyStore.put(idempotencyKey, result, Duration.ofDays(7));

    return ResponseEntity.status(201).body(result);
}
```

---

## 6. Health Checks & Readiness

```java
// Spring Boot Actuator — separate liveness from readiness
@Component
public class PaymentServiceHealthIndicator implements HealthIndicator {

    @Override
    public Health health() {
        // Liveness: is the service alive? (if not, K8s restarts it)
        // Check: can it process requests at all?
        return Health.up()
            .withDetail("threadPool", executor.getActiveCount() < executor.getMaximumPoolSize())
            .withDetail("memoryOk", Runtime.getRuntime().freeMemory() > 100_000_000)
            .build();
    }
}

// application.yml:
management:
  health:
    livenessstate:
      enabled: true
    readinessstate:
      enabled: true
  endpoint:
    health:
      probes:
        enabled: true
# Endpoints:
# /actuator/health/liveness  → K8s liveness probe
# /actuator/health/readiness → K8s readiness probe (remove from load balancer if DOWN)
```
