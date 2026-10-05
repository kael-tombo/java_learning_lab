# REAL-WORLD PROJECT — Profiling: p99 Triples, All Dashboards Green

## Incident Scenario
After a "minor" SDK bump, search p99 jumps 120ms → 900ms but CPU,
GC, and error dashboards stay green. Averages barely move — only the
tail suffers. Three teams blame the network. The truth is in a wall
flame nobody captured: a lock + N+1 + retry storm visible only at p99.

## Symptoms
- p50 +20ms, p99 +780ms, max 6s — tail-only shape; avg-based alerts
  never fire; SLO burn missed for 5h.
- CPU 40% (flat), GC pauses flat — not compute/collector.
- Downstream SDK changelog: new per-item `fetchFee` call + shared
  `synchronized` rate-limiter + default retry 3x with no backoff.
- Traces show 1 root span fanning to 40 fee spans (N+1) + retried
  spans on timeouts; lock contention invisible in metrics.
- Staging (low concurrency) cannot reproduce — needs 200 RPS + cold
  cache to trigger the tail.

## Investigation Tasks
1. Tail-first metrics: histogram query `histogram_quantile(0.99, ...)`
   by endpoint/version; confirm deploy-correlated tail jump; pull
   exemplar trace ids for the slowest 10.
2. JFR: `jcmd <pid> JFR.start name=tail settings=profile duration=300s
   filename=tail.jfr`; rank `jdk.SocketRead`, `jdk.JavaMonitorEnter`,
   `jdk.ThreadPark`, `jdk.ObjectAllocationInNewTLAB` in JMC.
3. async-profiler quad on one prod-canary (60s each): `-e wall`,
   `-e cpu`, `-e alloc`, `-e lock`; render differential vs pre-deploy
   build; name the fee-loop + limiter frames.
4. Threads: `jcmd <pid> Thread.print` during spike — parking on
   `RateLimiter` monitor + `WAITING socketRead` chains; `jstack`
   diff pre/post deploy.
5. Repro: load driver at p99-triggering RPS on staging with SDK flag
   on/off; capture trace waterfall (40 fee spans → 1 batched).

## Root Cause
SDK introduced N+1 fan-out (40 calls/order) through a single
synchronized limiter with aggressive retries. At concurrency, queueing
+ head-of-line blocking explodes the tail while averages and CPU look
fine. No single metric caught the interaction — only combined
wall/lock/trace evidence does.

## Resolution
- Immediate: pin SDK to prior version (flag), disable retries
  (or 1 retry + jitter), raise fee-cache TTL 5s → 60s on canary.
- Short-term: batch `fetchFees(ids)` (1 call), limiter
  `synchronized` → token-bucket lock-free, deadline propagation
  (2s global), tail-based alerting (p99 + p99.9 burn).
- Long-term: SDK-upgrade profiler gate (wall/alloc/lock diff in CI),
  tail-SLO per endpoint, exemplar-to-JFR linkage standard.

## Runbook
```
1. Quantile check (p50/p99/p99.9 by version) + grab 10 exemplar traces.
2. JFR 300s + wall/lock profiler 60s on canary (NOT full restart).
3. Pin SDK back / flag off; verify p99 900ms -> 120ms on canary.
4. Ship batch-fee + lock-free limiter; load-test at tail RPS.
5. Roll 100%; replay timed-out searches idempotently.
6. Land p99-burn alert + SDK profiler gate.
```

## Metrics
| Signal | Before | After | Gate |
|--------|--------|-------|------|
| p99 search | 900ms | 120ms | Burn alert >250ms |
| p99.9 | 6s | 400ms | Page >1s |
| Fee calls/order | 40 | 1 | Trace assertion |
| Lock wait/op | 180ms | <2ms | JFR monitor budget |
| Retry amplification | 3.1x | 1.05x | Client metric |

## Prevention Checklist
- [ ] p99/p99.9 burn alerts (never avg-only)
- [ ] Profiler gate on dependency bumps
- [ ] Exemplars from metrics to traces to JFR
- [ ] Wall+lock flames for any tail regression

## Failure-Injection Drill
- Reproduce on staging with fault injection (latency + error 5%).
- Capture JFR + `jcmd Thread.print` + heap dump during the drill.
- Verify alerts fire in <2 min and runbook step 1–3 completes <15 min.

## Interview Debrief
- Explain the signal that distinguished this root cause in 2 minutes.
- Whiteboard the before/after data path with the bounding fix circled.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- JFR runtime guide: https://docs.oracle.com/javacomponents/jmc-5-4/jfr-runtime-guide/about.htm
- Micrometer / Spring observability: https://docs.spring.io/spring-boot/reference/actuator/metrics.html
