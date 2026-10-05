# REAL-WORLD PROJECT — Streams: Nightly Report OOMs + Wrong Revenue

## Incident Scenario
Revenue report job OOMs at 1.2M orders, and when it finishes, totals are 7% high vs finance. Both perf and correctness broken in one pipeline.

## Symptoms
- `orders.stream().boxed().collect(toList())` materializes 3 copies; `parallelStream` with non-thread-safe `ArrayList::add` side effect → lost/dupe adds.
- `toMap(id, value)` with dupe order IDs throws; catch wraps whole job as failed; fallback manual sum double-counts.
- `findFirst` on unordered parallel returns nondeterministic promo winner daily.

## Investigation Tasks
1. Heap/JFR: `jcmd GC.heap_dump`, JFR `jdk.GCHeapSummary` + allocation events — `Order[]/ArrayList` dominance.
2. Logs: `grep "Duplicate key\|OutOfMemory"`; diff stream total vs SQL `SUM` grouped by day.
3. Repro: 50k-row slice — show side-effect race (run 10x, varying totals) and dupe-key crash.
4. Threads: `jcmd Thread.print` shows ForkJoinPool saturated on blocking I/O inside `map` (I/O in parallel stream).
5. Correctness: verify merge-fn + downstream `summingDouble` vs hand total.

## Root Cause
Materializing intermediates, stateful lambdas in parallel, missing `toMap` merge fn, blocking I/O in common pool, unordered `findFirst` misuse.

## Resolution
- Immediate: pure-function pipeline, `toMap` merge (sum dupes) or `groupingBy`, sequential for I/O, `findAny` or ordered `findFirst`; chunk file streaming (`Files.lines`).
- Short-term: collector review checklist, parallel-only-if-CPU-bound rule + benchmark gate, reconciliation vs SQL nightly.
- Long-term: batch/streaming framework option, property tests (parallel ≡ sequential), memory budget + JFR allocation alerts.

## Runbook
```
1. Save dump + JFR; switch job to sequential-streaming build.
2. Rerun; diff vs finance baseline to $0.
3. Land merge-fn + purity lint; doc parallel policy.
4. Schedule recon alert.
```

## Metrics
- Job heap < 1GB at 2M rows; totals match SQL exactly; nondeterminism = 0 (10/10 identical); runtime p95 within SLA.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Stream API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/package-summary.html
- Collectors: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/Collectors.html
