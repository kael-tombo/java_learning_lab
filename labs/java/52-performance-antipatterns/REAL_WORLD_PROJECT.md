# REAL-WORLD PROJECT — Performance Antipatterns: Death by a Thousand Cuts

## Incident Scenario
Catalog page p99 degrades 180ms → 2.4s over 6 weeks with no single
deploy to blame. Profiling was "on the backlog." The page is a museum
of antipatterns: N+1 reviews, boxed price streams, per-row JDBC,
recompiled regex slugs, `String.format` descriptions, and uncached
auth — each trivial, together fatal at holiday traffic.

## Symptoms
- p99 creep +13x over 6 weeks; p50 +3x; infra (CPU/GC/heap) scales
  linearly — waste, not leak; autoscale spend +62%.
- Trace: 1 page = 87 downstream calls (reviews N+1, per-item auth,
  per-row stock); JDBC round trips 120/page (no batch).
- JFR alloc 1.8GB/s: boxed `Stream<Double>` pricing, `String.format`
  per description, regex `Pattern.compile` per slug, date-format churn.
- `Thread.print` + JFR monitor: logging `synchronized` appender
  60ms/op under load; validation exceptions 40k/min (control flow).
- No single culprit >15% — flame is flat-wide, the classic
  thousand-cuts shape.

## Investigation Tasks
1. Call census: slowest 20 traces — count spans/page (87) by service;
   JDBC proxy counts round trips/page (120); rank by total ms.
2. JFR: `jcmd <pid> JFR.start name=cuts settings=profile duration=300s
   filename=cuts.jfr`; rank `jdk.ObjectAllocationInNewTLAB` by stack
   (boxing/format/regex) + `jdk.JavaExceptionThrow` (validation flow).
3. CPU+wall: async-profiler `-e cpu` + `-e wall` 60s; annotate top 10
   frames to antipattern names; quantify each bar's ms share.
4. Heap: `jcmd <pid> GC.heap_dump cuts.hprof` — char[]/boxed dominators
   confirm string/boxing share; `jhsdb jmap --histo` trend over a day.
5. History: `git log --oneline --since="8 weeks"` mapped to gradual
   call-count growth (each feature +3 calls, nobody counting).

## Root Cause
No performance budget or profiling gate: 10+ individually-shippable
inefficiencies accumulated. Traffic growth converted linear waste into
SLO breach + 62% extra compute.

## Resolution
- Immediate: cache auth/reviews (bounded, 60s TTL), batch stock
  (1 call), batch JDBC (50/page → 3), raise page-cache hit rate.
- Short-term: primitive pricing, precompiled regex/static formatters,
  validation-result (no exceptions), async logging; alloc budget 0.5GB/s.
- Long-term: calls/request + alloc-rate + p99 budgets per page with
  CI gates; flame-diff on every release; quarterly antipattern sweep.

## Runbook
```
1. Capture 20 slow traces + JFR 300s + cpu/wall 60s + heap dump (don't tune blind).
2. Ship batch+cache hotfix (calls 87->4) to canary; verify p99 2.4s -> 600ms.
3. Ship alloc fixes (boxing/format/regex/exceptions/logging) next train.
4. Verify: p99 <250ms, alloc <0.5GB/s, spend -50% at same RPS.
5. Roll 100%; warm caches; replay failed checkouts.
6. Land call/alloc/p99 gates + flame-diff job.
```

## Metrics
| Signal | Before | After | Gate |
|--------|--------|-------|------|
| p99 page | 2.4s | 210ms | SLO 400ms |
| Calls/page | 87 | 4 | Alert >8 |
| JDBC trips/page | 120 | 3 | Alert >6 |
| Alloc rate | 1.8GB/s | 0.4GB/s | Alert >0.6GB/s |
| Compute spend | +62% | baseline | Weekly review |

## Prevention Checklist
- [ ] Calls/request budget per page (CI-traced)
- [ ] Alloc-rate budget per endpoint (JFR gate)
- [ ] Flame-diff on release + p99 burn alert
- [ ] Bounded-cache-only rule with TTL review

## Failure-Injection Drill
- Reproduce on staging with fault injection (latency + error 5%).
- Capture JFR + `jcmd Thread.print` + heap dump during the drill.
- Verify alerts fire in <2 min and runbook step 1–3 completes <15 min.

## Interview Debrief
- Explain the signal that distinguished this root cause in 2 minutes.
- Whiteboard the before/after data path with the bounding fix circled.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Java performance / JFR guides: https://docs.oracle.com/en/java/javase/21/
- Spring / Micrometer metrics reference: https://docs.spring.io/spring-boot/reference/actuator/metrics.html
