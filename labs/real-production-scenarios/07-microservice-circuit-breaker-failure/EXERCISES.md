# EXERCISES — Lab 07: Circuit-Breaker Failure

## Exercise 1: Audit the Bad Config (15 min)
Given threshold 80, window 100, minCalls 50, wait 60s, timeout 30s — list 4 dangers + fixed values (50%, 20, 10, 30s, timeout 3s).

## Exercise 2: Resilience4j Tuning (20 min)
Write `application.yml` breaker + timelimiter + retry + bulkhead for payment (500ms avg, 50 rps). Justify thread count via Little's Law.

## Exercise 3: Fallback That Never Throws (20 min)
Implement `paymentFallback(Throwable)` returning queued-for-review order + metric + log. Test: fallback on timeout, no exception, status flag set.

## Exercise 4: Bulkhead Sizing (20 min)
5 deps with given latency/rps — allocate pools summing <40 threads. Show math L=λW per dep.

## Exercise 5: Retry Storm Containment (15 min)
Convert fixed 3-immediate-retries to exp-backoff+jitter, max 2, skip-if-OPEN. Diagram load before/after.

## Exercise 6: Trace the Cascade (15 min)
Given Zipkin waterfall, identify origin service + propagation path Level 2→1→0. Write 5-line timeline.

## Exercise 7: Force-Open Drill (15 min)
Practice: force breaker OPEN via actuator, verify fallback rate jumps, downstream QPS drops, then half-open recovery.

## Exercise 8: Alert Design (15 min)
Write alerts: pool saturation >80%, breaker state=open >2min, fallback rate >5%. Include PromQL + severity.

## Exercise 9: Chaos Test (20 min)
Inject 2s latency into fraud-service; confirm only its breaker opens, others stay CLOSED. Record fallback correctness.

## Exercise 10: Post-Mortem (20 min)
5-Whys to misconfig + missing bulkhead + no fallback requirement. 3 actions with owners/dates.
