# FLASHCARDS — Lab 07: Circuit-Breaker Failure

| Front | Back |
|---|---|
| CLOSED | Normal pass-through, monitoring failure rate |
| OPEN | Fail fast, invoke fallback, no downstream calls |
| HALF_OPEN | Limited probes to test recovery |
| failureRateThreshold | % failures to open; ~50% sane, 80% too slow |
| slidingWindowSize | Calls evaluated (10–20); 100 too sluggish |
| minimumNumberOfCalls | Min calls before rate evaluated |
| waitDurationInOpenState | Time OPEN before half-open (30–60s) |
| permittedCallsInHalfOpen | Probe count; keep small (2–3) |
| Bulkhead | Per-dep pool isolation |
| Semaphore bulkhead | Concurrency cap without extra threads |
| TimeLimiter | Caps call duration (3–5s) |
| Retry with backoff | e.g., 1s→2s→4s + jitter, max 2 |
| Jitter | Random delay preventing synchronized retries |
| Skip-if-OPEN | Never retry when breaker open |
| Fallback | Degraded response; must not throw |
| Cascading failure | Leaf slowdown propagates via blocked threads |
| Retry storm | Retries amplify load on sick service |
| Little's Law L=λW | Queue = arrival × wait; W↑ explodes L |
| Thread saturation alert | Active/queue >80% pages |
| Breaker state metric | resilience4j_circuitbreaker_state gauge |
| Fallback rate | % requests served by fallback; >5% investigates |
| Zipkin waterfall | Trace view pinning slowest leaf origin |
| Timeout 30s danger | Holds thread 300x longer than 100ms baseline |
| Force-open | Manually OPEN breaker to shed load |
| Half-open thundering | Too many probes re-sickens service; keep 2–3 |
| Degradation tier | Per-endpoint fallback plan (cache/default/queue) |
| Hystrix | Netflix breaker lib (legacy) → Resilience4j |
| Resilience4j | Modern Java fault-tolerance lib |
| Eureka | Service discovery in this stack |
| Zuul / Gateway | Edge routing tier that also queues |
| Ribbon | Client-side LB (legacy) |
| Atlas/Prometheus | Metrics aggregation |
| Thread pool 10–20 | Per-service size in this incident |
| 5000 rps capacity | Normal system throughput baseline |
| 78% peak errors | Cascade peak in this SEV1 |
| 94-min duration | Detection→recovery time |
| Level 0/1/2/3 | Gateway→edge→core→foundation dep tiers |
| Origin: payment-service | Leaf slowdown source |
| Retry max 3 | Never exceed; prefer 2 |
| Exp backoff formula | delay = base × 2^attempt + jitter |
| Chaos latency injection | Test breakers open in isolation |
| Config audit | Threshold/window/timeout/pool review checklist |
| Maturity L1→L3 | Basic defaults → per-dep + bulkhead + fallback |
| Shed load | Rate-limit/drop to protect core |
| Drain pools | Drop queued, fail fast, then recover |
| Blameless fix | Tune defaults + require fallback, not blame dev |
| p99 downstream | Tail latency that blocks threads longest |
| Queue depth | Waiting requests; unbounded = outage |
| Fail fast | Return fallback immediately vs blocking |
| Recovery probe | Half-open test call outcome decides CLOSED/OPEN |
| Coordinated retry | Global backoff policy across services |
| Dashboard must-have | Breaker state per dep + pool + fallback panels |
| Post-mortem action | e.g., bulkhead rollout, owner + date |
| Interview pitch | Origin→math→mitigation→prevention with numbers |
| SEV1/P0 cascade | Multi-service outage, coordinated restart |
| Graceful order path | Accept-with-review when fraud check down |
| Cache fallback | Serve stale catalog vs 500 |
| Queue-for-later | Async payment retry vs blocking user |
| Metric on fallback | Counter per fallback invocation |
| Log on fallback | Warn with cause + request id |
| Never-block fallback | No I/O to sick dep inside fallback |
| Recovery order | Sick leaf first, then edge, then gateway |
| Prevention trio | Short timeout + low threshold + bulkhead |
