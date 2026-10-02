# Circuit Breaker Pattern Exercises

## Exercise 1: Core Implementation from Scratch (Code Task)

**Implement** a minimal circuit breaker without libraries:

```java
// CircuitBreaker.java
public class CircuitBreaker {
    enum State { CLOSED, OPEN, HALF_OPEN }
    
    // Config
    private final int failureThreshold;        // count-based
    private final double failureRateThreshold; // rate-based
    private final int slidingWindowSize;
    private final long waitDurationInOpenState;
    private final int permittedCallsInHalfOpen;
    
    // State
    private volatile State state = State.CLOSED;
    private final AtomicLong failureCount = new AtomicLong();
    private final AtomicLong successCount = new AtomicLong();
    private final AtomicLong lastStateChange = new AtomicLong();
    private final RingBuffer<Boolean> window; // true=success, false=failure
    
    // TODO:
    // recordSuccess()
    // recordFailure()
    // boolean allowRequest() // returns true if request permitted
    // State getState()
    // void reset() // manual reset for admin
}
```

**Requirements**:
- Thread-safe (concurrent requests)
- Both count-based and rate-based threshold modes
- Sliding window (ring buffer) for rate calculation
- Automatic state transitions
- Configurable `waitDurationInOpenState`
- HALF_OPEN permits limited probe requests

**Tests**:
1. CLOSED → success → stays CLOSED, counts reset
2. CLOSED → N failures → OPEN
3. OPEN → waitDuration elapsed → HALF_OPEN
4. HALF_OPEN → success → CLOSED
5. HALF_OPEN → failure → OPEN
6. Concurrent requests: state transitions atomic

---

## Exercise 2: Resilience4j Integration (Code Task)

**Integrate** Resilience4j CircuitBreaker with Spring Boot:

```java
// OrderService.java
@Service
public class OrderService {
    private final CircuitBreaker circuitBreaker;
    private final Retry retry;
    
    @CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")
    @Retry(name = "paymentService")
    public PaymentResponse chargePayment(PaymentRequest request) {
        return paymentClient.charge(request);
    }
    
    public PaymentResponse paymentFallback(PaymentRequest request, Exception ex) {
        // TODO: Implement fallback
    }
}
```

**Configuration** (`application.yml`):
```yaml
resilience4j:
  circuitbreaker:
    instances:
      paymentService:
        registerHealthIndicator: true
        slidingWindowSize: 100
        slidingWindowType: COUNT_BASED
        failureRateThreshold: 50
        slowCallRateThreshold: 50
        slowCallDurationThreshold: 2s
        waitDurationInOpenState: 30s
        permittedNumberOfCallsInHalfOpenState: 3
        minimumNumberOfCalls: 10
  retry:
    instances:
      paymentService:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
```

**Requirements**:
- Health endpoint shows CB state
- Metrics exported to Prometheus (`resilience4j_circuitbreaker_*`)
- Fallback returns `PaymentResponse` with `status=QUEUED` and local order ID
- Events logged: state transitions, fallback invocations

**Test**:
1. Start service, verify CLOSED
2. Kill payment service → verify OPEN after threshold
3. Verify fallback returns QUEUED
4. Restore payment service → verify HALF_OPEN → CLOSED
5. Check Prometheus metrics

---

## Exercise 3: Circuit Breaker + Bulkhead + Retry Composition (Code Task)

**Implement** combined resilience pattern:

```java
// ResilientPaymentClient.java
@Component
public class ResilientPaymentClient {
    private final CircuitBreaker cb;
    private final Bulkhead bulkhead;
    private final Retry retry;
    private final TimeLimiter timeLimiter;
    
    public CompletableFuture<PaymentResponse> chargeAsync(PaymentRequest request) {
        // TODO: Compose: TimeLimiter → Bulkhead → CircuitBreaker → Retry → Supplier
        // Decorator pattern: Decorators.ofSupplier(supplier)
        //   .withCircuitBreaker(cb)
        //   .withBulkhead(bulkhead)
        //   .withRetry(retry)
        //   .withTimeLimiter(timeLimiter)
        //   .decorate()
    }
}
```

**Configuration**:
```yaml
resilience4j:
  bulkhead:
    instances:
      paymentService:
        maxConcurrentCalls: 20
        maxWaitDuration: 100ms
  timelimiter:
    instances:
      paymentService:
        timeoutDuration: 3s
        cancelRunningFuture: true
```

**Analyze** the composition order. Why this order?
- TimeLimiter outer: bounds total time including retries
- Bulkhead: limits concurrency before CB checks
- CircuitBreaker: fails fast if downstream unhealthy
- Retry inner: retries only on transient failures (not CB OPEN)

**Test**: 
1. Load test with 50 concurrent calls → verify bulkhead rejects (queue full)
2. Slow downstream (5s) → verify TimeLimiter cancels
3. 50% errors → verify CB opens, bulkhead not exhausted

---

## Exercise 4: Fallback Design Patterns (Design + Code Task)

**Design fallbacks** for these scenarios:

### 4a: Read Operation with Cache Fallback
```java
@CircuitBreaker(name = "userService", fallbackMethod = "getUserFallback")
public UserProfile getUser(String userId) {
    return userClient.getUser(userId);
}

public UserProfile getUserFallback(String userId, Exception ex) {
    // TODO: Return cached profile from Redis
    // If cache miss: return minimal default profile
    // Log fallback reason
}
```

### 4b: Write Operation with Outbox Fallback
```java
@CircuitBreaker(name = "inventoryService", fallbackMethod = "reserveInventoryFallback")
public Reservation reserveInventory(ReservationRequest request) {
    return inventoryClient.reserve(request);
}

public Reservation reserveInventoryFallback(ReservationRequest request, Exception ex) {
    // TODO: Save to local OUTBOX table
    // Return Reservation with status=PENDING, localId
    // Async processor will retry inventory service
}
```

### 4c: Idempotent Write with Status Polling
```java
@CircuitBreaker(name = "paymentGateway", fallbackMethod = "chargeFallback")
public ChargeResponse charge(ChargeRequest request) {
    return paymentGateway.charge(request);
}

public ChargeResponse chargeFallback(ChargeRequest request, Exception ex) {
    // TODO: Generate idempotency key
    // Save pending charge to DB
    // Return ChargeResponse with status=PROCESSING, pollUrl
    // Client polls /charges/{id} for final status
}
```

**Requirements**:
- All fallbacks: non-blocking, fast (< 10ms)
- Fallback logs: correlation ID, CB state, exception type
- Fallback metrics: `fallback.invoked`, `fallback.success`, `fallback.latency`

---

## Exercise 5: Configuration Tuning Workshop (Analysis Task)

**Given** these services, design CB config for each:

| Service | RPS | Latency p99 | Downstream | Failure Cost |
|---------|-----|-------------|------------|--------------|
| API Gateway → Auth | 5000 | 5ms | Internal (99.99%) | Request rejected |
| Checkout → Payment | 50 | 500ms | External (99.5%) | Lost revenue |
| Recommendations → ML | 200 | 200ms | Internal (99.9%) | Degraded UX |
| Notifications → Email | 10 | 2s | External (99%) | Delayed email |

**For each, specify**:
- `slidingWindowType` + `slidingWindowSize`
- `failureRateThreshold` OR `failureThreshold`
- `slowCallRateThreshold` + `slowCallDurationThreshold`
- `waitDurationInOpenState`
- `permittedNumberOfCallsInHalfOpenState`
- Fallback strategy

**Justify** each number with math (e.g., "at 50 RPS, 100 calls = 2s window").

---

## Exercise 6: Distributed Circuit Breaker Observability (Code Task)

**Build** a CB dashboard for a 10-service mesh:

```java
// CircuitBreakerAggregator.java
@Component
public class CircuitBreakerAggregator {
    // Collects CB state from all services via Prometheus/API
    // Provides unified view
    
    // TODO:
    // getFleetHealth() → FleetHealth { healthy, degraded, critical }
    // getServiceHealth(serviceName) → ServiceHealth
    // detectCascadingFailure() → boolean (multiple CBs OPEN in call chain)
}
```

**Metrics to aggregate** (per service):
- `circuitbreaker_state` (0=CLOSED, 1=OPEN, 2=HALF_OPEN)
- `circuitbreaker_failure_rate`
- `circuitbreaker_slow_call_rate`
- `circuitbreaker_buffered_calls` (bulkhead queue)

**Alert Rules**:
- Single service OPEN > 2min → PAGE
- > 3 services OPEN in same call chain → CASCADING ALERT
- Fleet failure rate > 20% → INCIDENT

**Implement** Grafana dashboard JSON + PrometheusRule alerts.

---

## Exercise 7: Chaos Engineering for Circuit Breakers (Experimental Task)

**Target**: Running microservice with Resilience4j CB.

**Chaos Experiments**:

| Experiment | Injection | Expected CB Behavior | Verification |
|------------|-----------|---------------------|--------------|
| **Latency Spike** | Add 5s delay to downstream | Slow call rate ↑ → CB OPEN | State=OPEN, fallback active |
| **Error Burst** | Return 500 for 10 requests | Failure rate ↑ → CB OPEN | State=OPEN, fast fail |
| **Partial Degradation** | 30% errors, 200ms latency | Both thresholds triggered | Metrics show both rates |
| **Network Partition** | iptables DROP to downstream | Connection failures → OPEN | No thread exhaustion |
| **Recovery** | Restore downstream | HALF_OPEN probes → CLOSED | State=CLOSED, no fallback |

**Tools**: Chaos Mesh, Litmus, or simple `tc`/`iptables` scripts.

**Runbook**:
1. Baseline: record normal metrics
2. Inject failure: start experiment
3. Observe: CB state transitions, fallback latency, upstream impact
4. Stop injection: verify recovery
5. Document: time to OPEN, time to CLOSED, any issues

**Deliverable**: Experiment results table + recommendations for config tuning.

---

## Exercise 8: Circuit Breaker for gRPC / Async (Code Task)

**Implement** CB for reactive gRPC client:

```java
// ReactivePaymentClient.java
@Service
public class ReactivePaymentClient {
    private final PaymentServiceGrpc.PaymentServiceStub stub;
    private final CircuitBreaker circuitBreaker;
    
    public Mono<ChargeResponse> charge(ChargeRequest request) {
        // TODO: Wrap gRPC call with CB
        // Use Reactor addon: CircuitBreakerOperator
        // Mono.fromCallable(() -> stub.charge(request))
        //     .transformDeferred(CircuitBreakerOperator.of(circuitBreaker))
        //     .onErrorResume(ex -> fallback(request, ex));
    }
}
```

**Alternative**: Use `resilience4j-micrometer` + `resilience4j-reactor`

**Test**:
1. Verify CB trips on gRPC error codes (UNAVAILABLE, DEADLINE_EXCEEDED)
2. Verify fallback returns `Mono.just(fallbackResponse)`
3. Load test with 1000 concurrent reactive streams

---

## Exercise 9: Anti-Patterns & Fixes (Analysis Task)

**Identify the problem** and fix each anti-pattern:

### 9a: CB with Synchronous Fallback Doing I/O
```java
@CircuitBreaker(name = "service", fallbackMethod = "fallback")
public Data getData() { return client.get(); }

public Data fallback(Exception ex) {
    return database.findBackup(); // BLOCKS caller thread!
}
```

### 9b: Retry Outside Circuit Breaker
```java
@Retry(name = "service")
@CircuitBreaker(name = "service") // Wrong order!
public Data getData() { return client.get(); }
```

### 9c: Shared Circuit Breaker for Unrelated Operations
```java
@CircuitBreaker(name = "userService") // Same CB for read AND write
public User getUser(String id) { ... }

@CircuitBreaker(name = "userService")
public void updateUser(User u) { ... }
```

### 9d: No Slow Call Threshold
```yaml
# Only failureRateThreshold configured
circuitbreaker:
  failureRateThreshold: 50
# Missing: slowCallRateThreshold, slowCallDurationThreshold
```

### 9e: Fallback Swallows Exception Type
```java
public Data fallback(Exception ex) { // Catches everything
    return defaultData();
}
// Can't distinguish: CB_OPEN vs TIMEOUT vs BUSINESS_ERROR
```

**For each**: Explain why it's wrong, show corrected code.

---

## Exercise 10: Production Incident Simulation (Scenario Task)

**Scenario**: Black Friday. Your e-commerce platform:
- 50 services, all with CBs
- Traffic 10x normal
- Payment provider has 5-minute outage
- 3 services have misconfigured CBs

**Simulate** (on paper or test env):
1. Payment CB config: `failureThreshold=3, waitDuration=10s` (too aggressive)
2. Inventory CB: no slow call threshold, downstream latency 10s
3. Shipping CB: fallback does synchronous DB write

**Trace the cascade**:
- T+0: Payment errors → Payment CB OPEN (after 3 failures)
- T+10s: Payment CB HALF_OPEN → probe fails → OPEN
- T+30s: Checkout threads blocked on Inventory (10s latency) → thread pool exhausted
- T+60s: Checkout CB OPEN (failure rate from timeouts)
- T+90s: Shipping fallback DB writes pile up → DB saturated
- T+120s: Platform down

**Fix each misconfiguration**. Show corrected configs.

**Post-Incident Action Items**:
1. CB config review checklist
2. Chaos engineering schedule
3. CB dashboard alerting rules
4. Fallback pattern guidelines

---

## Grading Rubric

| Exercise | Points | Criteria |
|----------|--------|----------|
| 1. Core Implementation | 20 | Thread-safe, correct state machine, tested |
| 2. Resilience4j Integration | 15 | Working config, health, metrics, fallback |
| 3. Pattern Composition | 15 | Correct order, reasoning, tested under load |
| 4. Fallback Design | 15 | Appropriate per operation type, non-blocking |
| 5. Config Tuning | 10 | Math-backed, realistic numbers |
| 6. Observability | 15 | Dashboard + alerts, cascading detection |
| 7. Chaos Engineering | 15 | Executed, documented, insights |
| 8. gRPC/Async | 10 | Working reactive CB |
| 9. Anti-Patterns | 10 | All 5 identified and fixed |
| 10. Incident Simulation | 10 | Cascade traced, fixes practical |

**Total**: 135 points