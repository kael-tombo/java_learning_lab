# CODE DEEP DIVE: Distributed Systems Resilience Patterns
## Lab 04 | Production Engineering Academy

---

## Pattern 1: Production Resilience4j Pipeline (Circuit Breaker + Rate Limiter + Retry + Bulkhead)

### Complete Architecture
A production remote client must compose resilience patterns in a specific sequence:
$$\text{Request} \longrightarrow \text{Bulkhead} \longrightarrow \text{CircuitBreaker} \longrightarrow \text{RateLimiter} \longrightarrow \text{Retry} \longrightarrow \text{Target Service}$$

```java
package com.learning.production.lab04;

import io.github.resilience4j.bulkhead.ThreadPoolBulkhead;
import io.github.resilience4j.bulkhead.ThreadPoolBulkheadConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.core.IntervalFunction;
import io.github.resilience4j.ratelimiter.RateLimiter;
import io.github.resilience4j.ratelimiter.RateLimiterConfig;
import io.github.resilience4j.retry.Retry;
import io.github.resilience4j.retry.RetryConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.*;
import java.util.function.Supplier;

public class ResilientPaymentServiceClient {
    private static final Logger log = LoggerFactory.getLogger(ResilientPaymentServiceClient.class);

    private final CircuitBreaker circuitBreaker;
    private final Retry retry;
    private final RateLimiter rateLimiter;
    private final ThreadPoolBulkhead bulkhead;

    public ResilientPaymentServiceClient() {
        // 1. Circuit Breaker: Trip to OPEN if 50% of requests fail out of last 20 calls
        CircuitBreakerConfig cbConfig = CircuitBreakerConfig.custom()
                .slidingWindowType(CircuitBreakerConfig.SlidingWindowType.COUNT_BASED)
                .slidingWindowSize(20)
                .minimumNumberOfCalls(10)
                .failureRateThreshold(50.0f) // 50%
                .slowCallRateThreshold(50.0f)
                .slowCallDurationThreshold(Duration.ofMillis(1000)) // Calls > 1s deemed slow
                .waitDurationInOpenState(Duration.ofSeconds(5)) // Fast recovery probe
                .permittedNumberOfCallsInHalfOpenState(5)
                .automaticTransitionFromOpenToHalfOpenEnabled(true)
                .recordExceptions(IOException.class, TimeoutException.class)
                .ignoreExceptions(IllegalArgumentException.class) // Client error != system failure
                .build();
        this.circuitBreaker = CircuitBreaker.of("payment-service-cb", cbConfig);

        // 2. Retry: Exponential Backoff with Full Decorrelated Jitter
        RetryConfig retryConfig = RetryConfig.custom()
                .maxAttempts(3)
                .intervalFunction(IntervalFunction.ofExponentialRandomBackoff(
                        Duration.ofMillis(100), 2.0, 0.5)) // base 100ms, multiplier 2x, jitter 50%
                .retryExceptions(IOException.class, TimeoutException.class)
                .build();
        this.retry = Retry.of("payment-service-retry", retryConfig);

        // 3. Rate Limiter: Max 500 calls per second outbound to avoid saturating downstream
        RateLimiterConfig rlConfig = RateLimiterConfig.custom()
                .limitForPeriod(500)
                .limitRefreshPeriod(Duration.ofSeconds(1))
                .timeoutDuration(Duration.ofMillis(50)) // Fail fast if quota exceeded
                .build();
        this.rateLimiter = RateLimiter.of("payment-service-rl", rlConfig);

        // 4. Thread Pool Bulkhead: Prevent downstream stalls from starving main application threads
        ThreadPoolBulkheadConfig bhConfig = ThreadPoolBulkheadConfig.custom()
                .coreThreadPoolSize(16)
                .maxThreadPoolSize(32)
                .queueCapacity(50)
                .keepAliveDuration(Duration.ofMinutes(1))
                .build();
        this.bulkhead = ThreadPoolBulkhead.of("payment-service-bh", bhConfig);
    }

    public CompletionStage<PaymentResult> executePaymentAsync(String paymentId, double amount) {
        Supplier<PaymentResult> rawCall = () -> invokeDownstreamPaymentApi(paymentId, amount);

        // Decorate: RateLimiter -> CircuitBreaker -> Retry
        Supplier<PaymentResult> decorated = CircuitBreaker.decorateSupplier(circuitBreaker, rawCall);
        decorated = RateLimiter.decorateSupplier(rateLimiter, decorated);
        decorated = Retry.decorateSupplier(retry, decorated);

        // Submit through Bulkhead thread pool
        Supplier<PaymentResult> finalDecorated = decorated;
        return bulkhead.executeSupplier(finalDecorated)
                .exceptionally(throwable -> {
                    log.error("Payment fallback triggered for id: {}. Reason: {}",
                            paymentId, throwable.getMessage());
                    return PaymentResult.fallback(paymentId, "Service degraded, queued for async reconciliation");
                });
    }

    private PaymentResult invokeDownstreamPaymentApi(String id, double amount) {
        // Real HTTP invocation (e.g. HttpClient or WebClient) with strict 800ms timeout
        return new PaymentResult(id, "SUCCESS", "AUTH-" + UUID.randomUUID());
    }

    public record PaymentResult(String id, String status, String authCode) {
        public static PaymentResult fallback(String id, String reason) {
            return new PaymentResult(id, "QUEUED_DEGRADED", reason);
        }
    }
}
```

---

## Pattern 2: Request Hedging Pattern (Taming p99.9 Tail Latency)

### Context
In distributed environments, a small percentage of requests experience tail latency spikes (e.g. minor GC, TCP retransmit, VM steal time). The hedging pattern issues a speculative duplicate request to a backup server if the primary request does not respond within the p95 latency budget (e.g. 50ms), taking whichever response returns first.

```java
package com.learning.production.lab04;

import java.util.concurrent.*;

public class RequestHedger<T> {
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

    public CompletableFuture<T> executeWithHedge(
            Callable<T> primaryRequest,
            Callable<T> hedgedRequest,
            Duration hedgeDelay) {

        CompletableFuture<T> result = new CompletableFuture<>();

        // 1. Fire primary request immediately
        CompletableFuture.supplyAsync(() -> {
            try {
                return primaryRequest.call();
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        }).whenComplete((val, ex) -> {
            if (ex == null) {
                result.complete(val);
            }
        });

        // 2. Schedule speculative hedge after delay if primary hasn't finished
        scheduler.schedule(() -> {
            if (!result.isDone()) {
                CompletableFuture.supplyAsync(() -> {
                    try {
                        return hedgedRequest.call();
                    } catch (Exception e) {
                        throw new CompletionException(e);
                    }
                }).whenComplete((val, ex) -> {
                    if (ex == null) {
                        result.complete(val);
                    }
                });
            }
        }, hedgeDelay.toMillis(), TimeUnit.MILLISECONDS);

        return result;
    }
}
```
