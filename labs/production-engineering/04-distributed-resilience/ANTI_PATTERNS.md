# ANTI-PATTERNS: Distributed Systems Resilience & Fault Tolerance
## Lab 04 | Production Engineering Academy — Staff & Distinguished Level

---

## 1. Summary of Lethal Distributed Resilience Anti-Patterns

```
+----------------------------------------------------------------------------------------------------+
| 10 LETHAL DISTRIBUTED RESILIENCE ANTI-PATTERNS AT A GLANCE                                         |
+-----+--------------------------------------+------------------------------+------------------------+
| #   | Anti-Pattern Name                    | Catastrophic Failure Mode    | Detection Metric       |
+-----+--------------------------------------+------------------------------+------------------------+
| 01  | Unjittered Fixed Retries             | Synchronized Thundering Herd | Periodic CPU/Req Spikes|
| 02  | Non-Idempotent Socket Timeout Retry  | Duplicate State / Double-Bill| Customer Support Tickets|
| 03  | Multi-Tier Retry Amplification       | Exponential Load ($R^N$)     | Offered Load >> Ingress|
| 04  | Global Unpartitioned Thread Pool     | Complete Blast Radius Spill  | Thread Pool Saturation |
| 05  | Inverted / Missing Timeout Hierarchy | Thread Leaks & Deadlocks     | High Latency + Hung TCP|
| 06  | Downstream-Coupled Liveness Probes   | Domino Pod Crash Loops       | KubePodCrashLooping    |
| 07  | Unprotected Cache/DB Fallbacks       | Database Death Spiral        | DB Connection Collapse |
| 08  | Default TCP Keepalive (15-min Stall) | Zombie Sockets Exhausting FD | ESTABLISHED socket pile|
| 09  | Blind Retries on 4xx Client Errors   | Circuit Breaker Poisoning    | False CB OPEN states   |
| 10  | Non-Atomic Redis Rate Limiting       | Over-Quota Concurrency Leak  | Rate Limit Bypassed    |
+-----+--------------------------------------+------------------------------+------------------------+
```

---

## Anti-Pattern 01: Unjittered Fixed Retries (Synchronized Thundering Herd)

### The Mistake
Retrying on a deterministic, synchronized schedule (e.g., waiting exactly $1,000\text{ ms}$ or purely linear exponential backoff without randomness).

```java
// FATAL: Synchronizes all retrying clients into harmonic waves
public <T> T executeWithDeterministicRetry(Supplier<T> action) {
    int maxAttempts = 3;
    long baseWaitMs = 1000;
    
    for (int attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            return action.get();
        } catch (Exception e) {
            if (attempt == maxAttempts) throw e;
            try {
                // BUG: Exactly 1000ms * attempt -> all 10,000 clients wake up at the EXACT same millisecond!
                Thread.sleep(baseWaitMs * (long) Math.pow(2, attempt - 1));
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                throw new RuntimeException(ie);
            }
        }
    }
    throw new IllegalStateException("Unreachable");
}
```

### Why It Fails
If 5,000 requests fail simultaneously due to a brief GC pause or BGP route flapping, all 5,000 threads sleep for exactly $1,000\text{ ms}$. At $t = 1000\text{ ms}$, all 5,000 clients awaken and slam the recovering dependency simultaneously. This creates massive, periodic square-wave traffic spikes that repeatedly knock the downstream service back into an unrecoverable state.

### The Production Fix: Full Decorrelated Jitter
```java
// PRODUCTION FIX: Full Jitter spreads retry timestamps uniformly across the interval
public class ProductionJitterRetry {
    private static final ThreadLocalRandom RANDOM = ThreadLocalRandom.current();

    public static long calculateFullJitter(int attempt, long baseMs, long capMs) {
        long exponentialBackoff = Math.min(capMs, baseMs * (1L << (attempt - 1)));
        // Uniform distribution: [0, exponentialBackoff]
        return ThreadLocalRandom.current().nextLong(0, exponentialBackoff + 1);
    }
}
```

---

## Anti-Pattern 02: Retrying Non-Idempotent Operations on Socket Read Timeout

### The Mistake
Treating a `java.net.SocketTimeoutException` on an HTTP `POST` request as a transient connection failure and automatically retrying the request.

```java
// FATAL: Retrying on Read Timeout causes double-debiting
@Retryable(value = { SocketTimeoutException.class }, maxAttempts = 3)
public PaymentResponse chargeCreditCard(PaymentRequest request) {
    // If the server processed the charge but the ACK packet was dropped on the return path,
    // this method throws SocketTimeoutException and Spring re-executes the POST!
    return restTemplate.postForObject("/api/v1/charges", request, PaymentResponse.class);
}
```

### Why It Fails
A `SocketTimeoutException` on a read operation means the client transmitted the request bytes, the server received them, and the server began processing. The timeout occurred while waiting for the response. **The transaction may already have committed in the database.** Re-executing the call leads to duplicate debiting, multiple shipments, and database corruption.

### The Production Fix
```java
// PRODUCTION FIX: Enforce cryptographic Idempotency-Key and restrict retries to connection phase
public PaymentResponse chargeCreditCardSafely(PaymentRequest request) {
    String idempotencyKey = "idem_" + UUID.randomUUID().toString();
    HttpHeaders headers = new HttpHeaders();
    headers.set("Idempotency-Key", idempotencyKey);
    HttpEntity<PaymentRequest> entity = new HttpEntity<>(request, headers);

    try {
        return restTemplate.postForObject("/api/v1/charges", entity, PaymentResponse.class);
    } catch (ResourceAccessException ex) {
        if (ex.getCause() instanceof ConnectException) {
            // TCP SYN never connected - safe to retry
            return retryOnConnectionFailure(entity);
        } else if (ex.getCause() instanceof SocketTimeoutException) {
            // Socket read timed out - STATE IS INDETERMINATE!
            // Do NOT blind retry. Transition transaction to PENDING and trigger query/reconcile.
            return reconcileIndeterminatePayment(idempotencyKey);
        }
        throw ex;
    }
}
```

---

## Anti-Pattern 03: Multi-Tier Retry Amplification (Exponential $R^N$ Fanout)

### The Mistake
Configuring automatic retries at every single layer of a deep microservice call tree.

```
[Web App]      --> Retries 3x on Gateway
  |
[API Gateway]  --> Retries 3x on Order Service
  |
[Order Service]--> Retries 3x on Payment Service
  |
[Payment Serv] --> Retries 3x on Payment Provider
```

### Why It Fails
When the Payment Provider experiences an outage, the number of requests arriving at the database scales exponentially:

$$\text{Total Requests} = 3 \times 3 \times 3 \times 3 = 81\text{ requests per user action!}$$

A system normally taking $2,000\text{ req/s}$ is instantly blasted with $162,000\text{ req/s}$. The entire infrastructure melts down.

### The Production Fix: The Single-Retry Rule & Retry Budgets
1. **The Single Retry Rule**: Only the immediate caller of the failing component may retry, OR retries are only permitted at the edge client. Never both.
2. **Retry Budgets (Finagle / Envoy Standard)**: Enforce a strict ratio: at most **$10\%$** of total requests can be retries. If retry volume exceeds $10\%$, retries are immediately aborted and fail fast.

---

## Anti-Pattern 04: Global Unpartitioned Thread Pool (Blast Radius Spill)

### The Mistake
Sharing a single `ForkJoinPool.commonPool()` or single Tomcat executor for all outbound external integrations.

```java
// FATAL: Using common pool or unpartitioned executor for external calls
public CompletableFuture<Inventory> checkInventory(String sku) {
    return CompletableFuture.supplyAsync(() -> remoteInventoryClient.get(sku));
}

public CompletableFuture<Pricing> getPricing(String sku) {
    return CompletableFuture.supplyAsync(() -> remotePricingClient.get(sku));
}
```

### Why It Fails
If `remoteInventoryClient` slows down from $10\text{ ms}$ to $10\text{ s}$ due to a remote network issue, all threads in `ForkJoinPool.commonPool()` become blocked waiting on socket I/O. As a direct consequence, `getPricing()`, internal parallel streams, and unrelated application tasks freeze entirely. A localized failure in an optional service takes down the primary revenue path.

### The Production Fix: Dedicated Thread Pool Bulkheads
```java
// PRODUCTION FIX: Isolate each remote dependency in its own bounded ThreadPoolBulkhead
public class IsolatedBulkheadClient {
    private final ThreadPoolBulkhead inventoryBulkhead = ThreadPoolBulkhead.of(
        "inventory-bulkhead",
        ThreadPoolBulkheadConfig.custom()
            .coreThreadPoolSize(8)
            .maxThreadPoolSize(16)
            .queueCapacity(20)
            .build()
    );

    public CompletionStage<Inventory> checkInventory(String sku) {
        return inventoryBulkhead.executeSupplier(() -> remoteInventoryClient.get(sku));
    }
}
```

---

## Anti-Pattern 05: Inverted / Missing Timeout Hierarchy

### The Mistake
Configuring client timeouts longer than downstream proxy/gateway timeouts, or omitting timeouts entirely (`timeout = 0`).

```yaml
# FATAL TIMEOUT TOPOLOGY:
client.read-timeout: 30000ms          # Client waits 30 seconds
api-gateway.ingress.timeout: 15000ms  # Gateway cuts connection at 15 seconds (sends 504)
backend-service.db.timeout: 60000ms   # Database query waits 60 seconds
```

### Why It Fails
1. At $t = 15\text{ s}$, the Gateway terminates the connection to the client and returns HTTP 504.
2. The Backend Service and Database continue running the expensive calculation for another 45 seconds, oblivious to the fact that nobody is listening!
3. The client, receiving 504, immediately retries, spawning another heavy query on top of the ghost query.

### The Production Fix: Strict Decreasing Timeout Budgets
$$\text{Ingress Timeout} > \text{Gateway Timeout} > \text{Service Timeout} > \text{DB Timeout}$$

```
[Ingress LB: 10.0s] 
    └── [API Gateway: 8.0s] 
            └── [Service A: 5.0s] 
                    └── [Database Socket: 2.5s]
```

---

## Anti-Pattern 06: Downstream-Coupled Liveness Probes (Cluster Suicide)

### The Mistake
Checking downstream databases, Kafka brokers, or third-party APIs inside the Kubernetes `/actuator/health/liveness` probe.

```java
// FATAL: Liveness probe fails if downstream database is down
@Component
public class PoisonousLivenessCheck implements HealthIndicator {
    @Autowired private DataSource dataSource;

    @Override
    public Health health() {
        try (Connection c = dataSource.getConnection()) {
            if (c.isValid(1)) return Health.up().build();
        } catch (Exception e) {
            // BUG: Causes Kubernetes to RESTART the pod!
            return Health.down(e).build();
        }
        return Health.down().build();
    }
}
```

### Why It Fails
When PostgreSQL becomes temporarily overloaded, all 200 Kubernetes Pods fail their liveness probes simultaneously. Kubernetes immediately kills and restarts all 200 Pods. Upon restarting, all 200 Pods flood PostgreSQL with startup connection pools and schema validation queries, ensuring the database never recovers.

### The Production Fix: Decouple Liveness from Readiness
- **Liveness (`/health/liveness`)**: Verifies only internal JVM health (no deadlocked JVM threads, heap memory not corrupted). **NEVER check network dependencies.**
- **Readiness (`/health/readiness`)**: Verifies if the pod can accept traffic. If the database is down, readiness returns `DOWN`, and Kubernetes stops routing ingress traffic to the pod without killing it.

---

## Anti-Pattern 07: Unprotected Cache / Database Fallbacks (Fallback Stampede)

### The Mistake
When a cache misses or a fast microservice fails, falling back directly to an unthrottled relational database query.

```java
// FATAL: Fallback hits the raw database without concurrency isolation
public UserProfile getProfile(String userId) {
    try {
        return redisCache.get(userId);
    } catch (RedisException ex) {
        log.warn("Redis down, falling back to PostgreSQL directly");
        // BUG: If Redis goes down under 50,000 rps, 50,000 rps instantly slam PostgreSQL!
        return userRepository.findById(userId).orElse(null);
    }
}
```

### Why It Fails
A cache is designed to absorb $99\%$ of read traffic. If the cache layer fails, the database is subjected to a $100\times$ surge in query volume. The database connection pool exhausts in milliseconds, crashing the core persistence layer.

### The Production Fix: Degraded Static Fallbacks or Bulkhead-Gated Queries
```java
// PRODUCTION FIX: Fallback to static degraded data OR strictly rate-limited DB bulkhead
public UserProfile getProfileSafely(String userId) {
    try {
        return redisCache.get(userId);
    } catch (RedisException ex) {
        return dbFallbackBulkhead.executeSupplier(() -> 
            userRepository.findById(userId).orElse(UserProfile.ANONYMOUS_PLACEHOLDER)
        );
    }
}
```

---

## Anti-Pattern 08: Default Linux TCP Keepalive (The 15-Minute Zombie Hang)

### The Mistake
Relying on default operating system TCP keepalive settings for long-lived HTTP/1.1 or gRPC connection pools.

### Why It Fails
In Linux, the default TCP keepalive parameters are:
- `tcp_keepalive_time = 7200` (2 hours before first probe)
- `tcp_keepalive_intvl = 75` (75 seconds between probes)
- `tcp_keepalive_probes = 9` (9 unacknowledged probes before drop)
- `tcp_retries2 = 15` (Up to 15-30 minutes of retransmissions for unacknowledged data!)

If a cloud network path or intermediate NAT gateway silently drops state without sending a TCP RST, the JVM socket remains in `ESTABLISHED` state. Worker threads block in `socketRead0` for **up to 15-30 minutes**, draining the entire HTTP connection pool.

### The Production Fix
Set socket-level `TCP_USER_TIMEOUT` (Linux socket option) and aggressive application-level keepalives:
```java
// Set TCP keepalive and user timeout via Netty / OkHttp
bootstrap.option(EpollChannelOption.TCP_USER_TIMEOUT, 10000); // 10s max unacknowledged data
bootstrap.option(ChannelOption.SO_KEEPALIVE, true);
```

---

## Anti-Pattern 09: Blind Retries on Non-Transient HTTP 4xx Errors

### The Mistake
Retrying on any exception returned by the HTTP client, including `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, and `422 Unprocessable Entity`.

```java
// FATAL: Retrying on 4xx business errors poisons circuit breakers
CircuitBreakerConfig.custom()
    .recordExceptions(Throwable.class) // BUG: 400 Bad Request trips the circuit breaker!
    .build();
```

### Why It Fails
A malformed request with invalid JSON will consistently return HTTP 400. Retrying it 3 times wastes bandwidth. Worse, if a buggy frontend release sends thousands of invalid requests, the backend circuit breaker counts these 400s as system failures and trips to `OPEN`, blocking valid users from using the application.

### The Production Fix: Strict Classification of Retriable vs. Non-Retriable
```java
// PRODUCTION FIX: Only retry idempotent transient infrastructure errors
RetryConfig.custom()
    .retryOnException(e -> {
        if (e instanceof HttpServerErrorException hse) {
            // Retry 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout
            HttpStatus status = hse.getStatusCode();
            return status == HttpStatus.BAD_GATEWAY || 
                   status == HttpStatus.SERVICE_UNAVAILABLE || 
                   status == HttpStatus.GATEWAY_TIMEOUT;
        }
        return e instanceof SocketException || e instanceof TimeoutException;
    })
    .ignoreExceptions(HttpClientErrorException.class) // Never retry 4xx
    .build();
```

---

## Anti-Pattern 10: Non-Atomic Distributed Rate Limiting via Redis

### The Mistake
Implementing distributed rate limiting with separate Redis `GET` followed by `INCR` and `EXPIRE`.

```java
// FATAL: Race condition under concurrency
public boolean isAllowed(String userId) {
    String count = redis.get("rate:" + userId);
    if (count != null && Integer.parseInt(count) >= 100) {
        return false;
    }
    redis.incr("rate:" + userId);
    redis.expire("rate:" + userId, 60);
    return true;
}
```

### Why It Fails
Under concurrent load (e.g., 50 requests arriving simultaneously), all threads read `count = 99` before any thread increments. All 50 requests are permitted, exceeding the rate limit by $50\%$. Furthermore, if the server crashes between `INCR` and `EXPIRE`, the key becomes permanent, indefinitely locking out the user.

### The Production Fix: Atomic Redis Lua Script (GCRA or Sliding Window)
Execute the check, increment, and expiration atomically in a single Redis Lua script evaluation.
