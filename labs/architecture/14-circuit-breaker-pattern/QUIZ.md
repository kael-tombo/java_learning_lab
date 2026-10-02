# Circuit Breaker Pattern Quiz

## Questions

1. **States & Transitions**: A circuit breaker has three states: CLOSED, OPEN, HALF_OPEN. Draw the state transition diagram. What triggers each transition? What is the purpose of HALF_OPEN?

2. **Failure Threshold**: You configure `failureThreshold=5, failureRateThreshold=50%`. In a sliding window of 10 requests, 3 fail. Is the circuit OPEN? What if 5 fail?

3. **Timeout Configuration**: `waitDurationInOpenState=30s`. Circuit opens at T=0. At T=15s, a request comes in. What happens? At T=35s?

4. **Bulkhead vs Circuit Breaker**: Both prevent cascading failures. What's the key difference? When would you use each? Can they be combined?

5. **Idempotency & Retries**: Circuit breaker trips (OPEN). Client has retry logic with exponential backoff. What happens when circuit enters HALF_OPEN? How do you ensure retries don't overwhelm the recovering service?

6. **Distributed Circuit Breaker**: In a microservices mesh, Service A calls Service B (which calls Service C). Service C fails. Where should circuit breakers be placed? What happens if A has CB for B, and B has CB for C, and C fails?

7. **Fallback Design**: Design a fallback for: (a) `getUserProfile(userId)` — read operation, (b) `placeOrder(order)` — write operation. What's the difference in fallback strategy?

8. **Monitoring Metrics**: What are the 5 most critical metrics to alert on for circuit breaker health? For each, give a threshold example.

9. **Configuration Tuning**: High-throughput service (10k RPS) vs low-throughput (10 RPS). How do `slidingWindowSize`, `failureThreshold`, `waitDurationInOpenState` differ? Justify with numbers.

10. **Real-World Scenario**: Payment service calls external bank API (99.9% uptime, 200ms p99). Bank has occasional 5min outages. Design CB config: failure threshold, timeout, fallback. What's the business impact of wrong config?

---

## Answers

1. **State Diagram**:
   ```
   CLOSED --(failure threshold reached)--> OPEN
   OPEN --(waitDuration elapsed)--> HALF_OPEN
   HALF_OPEN --(test request succeeds)--> CLOSED
   HALF_OPEN --(test request fails)--> OPEN
   CLOSED --(success)--> CLOSED (reset failure count)
   ```
   **HALF_OPEN**: Allows probe requests to test if downstream recovered without fully opening.

2. **Failure Rate**: 3/10 = 30% < 50% → **CLOSED**. 5/10 = 50% ≥ 50% → **OPEN** (threshold met).

3. **Timeout Behavior**: 
   - T=15s: Circuit OPEN → request **rejected immediately** (fail fast)
   - T=35s: Circuit HALF_OPEN → **probe request allowed**, if succeeds → CLOSED

4. **Difference**: 
   - **Circuit Breaker**: Temporal — stops calling failing service for a period
   - **Bulkhead**: Structural — isolates resources (threads, connections) per service
   - **Combined**: Bulkhead limits concurrent calls; CB trips when bulkhead rejects/fails

5. **HALF_OPEN + Retries**: 
   - Only **one** probe request allowed in HALF_OPEN (or configured `permittedNumberOfCallsInHalfOpenState`)
   - Client retries should **respect CB state** — don't retry when OPEN
   - Use `Retry` + `CircuitBreaker` in Resilience4j: retry only on specific exceptions, not when CB OPEN

6. **Placement**: 
   - **Every service boundary**: A→B has CB, B→C has CB
   - If C fails: B's CB for C trips → B fails fast → A's CB for B sees failures → A trips
   - **Cascade prevention**: B should have fallback for C failure so A doesn't see errors
   - **Alternative**: Global CB at edge (API Gateway) for external dependencies

7. **Fallback Design**:
   - (a) `getUserProfile`: **Read fallback** — return cached profile, stale data OK, or default profile
   - (b) `placeOrder`: **Write fallback** — **cannot** return fake success. Options: queue for later (async), return "try later" error, save to local outbox. Never silently succeed.

8. **Critical Metrics**:
   | Metric | Threshold Example |
   |--------|-------------------|
   | `circuitbreaker.state` | Alert if OPEN > 1min |
   | `circuitbreaker.failure.rate` | Alert if > 30% for 5min |
   | `circuitbreaker.slow.call.rate` | Alert if > 50% calls > 2x baseline |
   | `circuitbreaker.calls` | Alert if drop > 80% (traffic loss) |
   | `circuitbreaker.halfopen.success` | Alert if 0 successes in 3 probes |

9. **Tuning**:
   | Param | High-Throughput (10k RPS) | Low-Throughput (10 RPS) |
   |-------|---------------------------|-------------------------|
   | `slidingWindowSize` | 1000 (100ms window) | 100 (10s window) |
   | `failureThreshold` | Count-based: 50 | Rate-based: 50% |
   | `waitDurationInOpenState` | 10s (fast recovery) | 60s (avoid flapping) |
   | **Why** | Need statistical significance quickly | Too few requests for rate-based; avoid noise |

10. **Payment Service Config**:
    - `failureThreshold=3` (count-based, low volume)
    - `waitDurationInOpenState=60s` (bank outage ~5min, but don't flap)
    - `slidingWindowType=COUNT_BASED, slidingWindowSize=10`
    - **Fallback**: Queue order locally, return "processing" to user, async retry
    - **Wrong config impact**: Too sensitive → false trips → lost orders. Too loose → cascade → thread exhaustion.