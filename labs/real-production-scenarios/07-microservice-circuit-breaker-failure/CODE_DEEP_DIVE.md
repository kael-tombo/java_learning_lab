# CODE DEEP DIVE — Lab 07: Breaker Runbook

## 1. Spot Saturation + Breaker State
```bash
curl -s http://order-service:8080/actuator/metrics/thread.pool.active | jq .
curl -s http://order-service:8080/actuator/circuitbreakers | jq .
# Prometheus:
# resilience4j_circuitbreaker_state{breaker="payment"}  # 0 closed,1 open,2 half_open
kubectl top pods -l app=order-service
kubectl logs -l app=order-service --tail=100 | grep -i "timeout\|bulkhead\|fallback"
# log snippet:
# TimeoutException: payment-service call timed out after 30000ms [thread=order-tp-19]
# BulkheadFullException: payment bulkhead at 20/20 — thread pool exhausted
```

## 2. Fixed Resilience4j Config
```yaml
resilience4j.circuitbreaker.configs.default:
  failureRateThreshold: 50
  slidingWindowSize: 20
  minimumNumberOfCalls: 10
  waitDurationInOpenState: 30s
  permittedNumberOfCallsInHalfOpenState: 2
resilience4j.timelimiter.configs.default:
  timeoutDuration: 3s
resilience4j.retry.configs.default:
  maxAttempts: 2
  waitDuration: 1s
  enableExponentialBackoff: true
resilience4j.bulkhead.configs.payment:
  maxConcurrentCalls: 5
  maxWaitDuration: 100ms
```

## 3. Java Breaker + Fallback
```java
CircuitBreaker cb = registry.circuitBreaker("payment");
Supplier<OrderResult> s = () -> paymentClient.charge(order);
OrderResult r = Decorators.ofSupplier(s)
  .withCircuitBreaker(cb).withBulkhead(bulkhead)
  .withRetry(retry).withFallback(e -> OrderResult.queuedForReview(order.getId()))
  .get();
```

## 4. Force-Open + Verify
```bash
curl -X POST http://order-service:8080/actuator/circuitbreakers/payment/force-open
curl -s http://order-service:8080/actuator/circuitbreakers/payment | jq .state
curl -s "http://prom:9090/api/v1/query?query=rate(fallback_total[2m])" | jq .
```

## 5. Trace Origin
```bash
curl -s http://zipkin:9411/api/v2/traces?serviceName=order-service&limit=5 | jq '.[0][] | {service: .localEndpoint.serviceName, dur: .duration}'
```

## 6. Load-Shed (Gateway)
```bash
# drop retries upstream temporarily
curl -X PATCH http://gateway:8080/actuator/retry-policy -d '{"maxAttempts":1}'
kubectl scale deployment order-service --replicas=12  # add edge capacity while leaf recovers
```

## 7. Anti-Patterns
- Raising threads to 200 instead of opening breaker — just delays collapse.
- Fallback calling the same sick service — re-blocks.
- `waitDuration 5s` + 10 probes on DB-backed leaf — hammers recovering DB.
