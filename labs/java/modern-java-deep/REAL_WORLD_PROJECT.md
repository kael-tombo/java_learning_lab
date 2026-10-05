# REAL_WORLD_PROJECT — Modern Java Deep: Virtual-Threads Migration

## Project: FinTech order aggregator on virtual threads

Migrate a Spring Boot 3 order-aggregator (profile + orders + risk calls
per request) from a 200-thread Tomcat pool to virtual threads +
structured concurrency. Baseline: 4 vCPU / 8 GB container, JDK 21.

## 1. Baseline vs target (JMH + load numbers to reproduce)

| Metric | Platform threads (200) | Virtual threads (target) |
|--------|------------------------|--------------------------|
| Sustained RPS @ p99 < 300 ms | ~1,800 | ~9,500 |
| p99 @ 5k RPS | ~1,200 ms | ~180 ms |
| Thread count @ 5k RPS | 200 (saturated, queued) | ~5,200 virtual / 8 carriers |
| Memory per 1k concurrent | ~1 GB stack | ~15 MB stack |

JMH harness: `OrderAggregationBenchmark` (in `04-virtual-threads/`),
`-wi 3 -i 5 -f 2`; Gatling profile in `05-structured-concurrency-2/`.
Record your numbers in the results table before claiming success.

## 2. Structured concurrency shape

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var profile = scope.fork(profileClient::get);
    var orders  = scope.fork(orderClient::list);
    var risk    = scope.fork(riskClient::score);
    scope.join();
    scope.throwIfFailed();
    return Aggregated.of(profile.get(), orders.get(), risk.get());
}
```

Policy: `ShutdownOnFailure` for the order path (fail fast, cancel
siblings); `ShutdownOnSuccess` only for the redundant price-quote race.
Timeouts via `scope.joinUntil(Instant.now().plusMillis(800))`.

## 3. Pinning fixes (the 3 classic traps)

1. `synchronized` on the hot path → replace with `ReentrantLock`.
2. JNI crypto call pinning carriers → offload to bounded platform pool.
3. `ThreadLocal` request context → migrate to `ScopedValue`.

Verify with `jdk.VirtualThreadPinned` JFR events: pinning rate < 0.1%.

## 4. Capacity plan

8 carrier threads (== vCPU) handle ~10k concurrent virtual threads for
this I/O-bound mix (downstream p50 ~60 ms). Size Hikari to ~20
connections — pool is the real throttle, not threads. Scale pods on
p99 + CPU; load-test at 5x baseline before sign-off.

## 5. Runbook (pinning regression)

1. Alert: `rate(vt_pinned_total[5m]) > 0` for 10 min.
2. Capture: `jcmd <pid> JFR.start duration=120s filename=pin.jfr`.
3. Analyse: `jfr print --events jdk.VirtualThreadPinned pin.jfr`.
4. Mitigate: rollback flag `spring.threads.virtual.enabled=false`.
5. Fix forward: replace `synchronized`, re-run JMH, close with graph.

## 6. Grafana / Prometheus metrics

```promql
rate(http_server_requests_seconds_count[5m])
histogram_quantile(0.99, http_server_requests_seconds_bucket)
jvm_threads_virtual_threads
rate(jvm_virtual_threads_pinned_total[5m])
hikaricp_connections_active
```

Dashboard: RPS, p50/p99, virtual-thread count, pinning rate, pool
saturation on one row. Alert on p99 delta, not absolute.

## 7. Deliverables checklist

- [ ] JMH + load-test table (before/after, same hardware)
- [ ] Structured-concurrency aggregation service + tests
- [ ] Pinning audit (JFR excerpt, 3 fixes applied)
- [ ] Capacity note (pool sizing, HPA signal)
- [ ] Runbook + dashboard JSON committed

## Sourced field notes (fetched Oct 2026 — verify before citing)

- https://openjdk.org/jeps/444
- https://openjdk.org/jeps/462
- https://docs.oracle.com/en/java/javase/21/docs/api/
