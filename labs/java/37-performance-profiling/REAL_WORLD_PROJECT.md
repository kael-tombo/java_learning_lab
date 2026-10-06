# REAL-WORLD PROJECT — Performance: Flash-Sale p99 Meltdown

## Incident Scenario
Flash sale: p99 300ms → 8s at 3k rps, pods autoscale 6→40 with no relief,
then Full GCs cascade — "just add CPU" burns budget while checkout abandons
hit 35%.

## Symptoms
- CPU 95% yet throughput flat; lock flame shows `synchronized PriceCache`.
- Alloc flame: `Pattern` + `String.split` + boxed stream per search.
- GC log: Young every 1s, promotion failures → Full GC 4s pauses.
- `jcmd Thread.print` shows 300 threads parked on cache monitor.
- No baseline flame; last "optimization" (extra cache layer) never measured.

## Investigation Tasks
1. Hold one bad pod (don't kill): `jcmd <pid> Thread.print` × 3 + 
   `jcmd <pid> JFR.start duration=300s filename=sale.jfr settings=profile`.
2. async-profiler (if available): wall + cpu + alloc + lock 60s each;
   otherwise JFR `jdk.ExecutionSample`, `jdk.ObjectAllocationInNewTLAB`,
   `jdk.JavaMonitorEnter` triangulation.
3. Heap: `jcmd <pid> GC.heap_dump`; dominators for cache copies (double
   caching: Caffeine + HashMap + request-scope list triplicating results).
4. Flags: `jcmd <pid> VM.flags`; check heap vs container, GC choice, and
   whether new cache layer increased Old Gen tenuring.
5. Log/trace: p99-by-endpoint split; confirm search (not checkout) dominates;
   `grep "Full GC\|Promotion Failed" gc.log | tail -20`.
6. Repro: replay 3k-rps slice on staging with same flags; capture before
   flame as the baseline the team never took.
7. Gate audit: CI has no bench job — record the gap for postmortem.

## Root Cause
Lock-contended cache + per-request regex/alloc churn + over-caching (3 copies)
+ undersized heap turns load into contention → allocation storm → Full GCs;
scaling replicates the bottleneck instead of removing it.

## Resolution
- Immediate: raise cache concurrency (Caffeine, no `synchronized`), hoist
  patterns, kill duplicate cache layer, cap autoscale + shed non-critical
  traffic, stagger sale cohorts.
- Short-term: primitive/pooled hot path, right-size heap (`MaxRAMPercentage`),
  G1 tuning, JMH + macro evidence per fix.
- Long-term: flame + bench gate in CI, p99/alloc SLO alerts, capacity model,
  pre-sale load + profile game day.

## Runbook
```
1. Pin one pod: Thread.print + JFR + heap_dump + GC log slice.
2. Ship lock+regex hotfix to canary; compare flames + p99.
3. De-duplicate caches; re-size heap; verify Full GCs = 0.
4. Gate the gain (CI bench); scale only after p99 recovers.
5. Postmortem: budgets + game-day schedule.
```

## Metrics
- p99 <= 400ms at 3k rps; Full GCs = 0 over sale window.
- Lock samples on cache < 2%; alloc from search path -70%.
- Gate blocks planted 10% regression in CI drill.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- JFR runtime guide (JEP 328, Flight Recorder, JDK 11): https://openjdk.org/jeps/328
- jcmd reference: https://docs.oracle.com/en/java/javase/21/docs/specs/man/jcmd.html
