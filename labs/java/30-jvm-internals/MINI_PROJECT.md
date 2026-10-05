# MINI PROJECT — JVM Internals: Tune the Latency Outlier

## Goal (2 weeks, ~8–10h)
Take a deliberately misconfigured order API (wrong GC, tiny heap, cold JIT)
and ship a JFR-evidenced tuning memo cutting p99 by 50% with no OOM.

## Requirements
### Functional
1. Workload: synthetic `OrderApi` (JSON parse, price calc, in-memory store)
   with Gatling/k6 or loop driver producing p50/p99/throughput numbers.
2. Baseline: run with `-Xmx512m -XX:+UseParallelGC` on container-limited
   1GB; capture GC log (`-Xlog:gc*`), JFR profile, `jcmd Thread.print`.
3. Experiments (min 4): G1 vs ZGC, heap 1x vs 2.5x live set,
   `MaxRAMPercentage=75`, warmup vs cold; one flag change at a time.
4. JIT check: `-Xlog:jit+compilation` excerpt for hottest method; refactor
   one megamorphic call to monomorphic; show compile/deopt delta.
5. Classloader check: `jcmd <pid> VM.class_hierarchy` / GC.class_stats to
   spot duplicate-loaded `Order` class; fix if present.

### Non-functional
- Every claim backed by JFR event (`jdk.GarbageCollection`,
  `jdk.GCHeapSummary`, `jdk.Compilation`, `jdk.ObjectAllocationInNewTLAB`).
- Heap dumps before/after (`jcmd GC.heap_dump`) with dominator summary.
- 12+ tests: sizing math, flag-parse, warmup determinism, no-OOM soak.
- README: decision table (GC × heap × pause) + final `JAVA_OPTS`.

## Phases
### Week 1 — Baseline + Instruments (4–5h)
- Steps: driver harness, GC-log + JFR capture, heap dump, hotspot ID.
- Deliverable: baseline report (p99, pauses, top allocator).

### Week 2 — Tune + Prove (4–5h)
- Steps: 4 experiments, JIT refactor, soak 30 min, memo.
- Deliverable: tuned flags + p99 chart + JFR evidence pack.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–15) | Fail (<12) |
|-----------|----------------|--------------|------------|
| Measurement | JFR+GC log per run, 1-var changes | Timed runs | Anecdotes |
| GC sizing | Live-set math, right GC for SLO | Sensible flags | Flag soup |
| JIT insight | Deopt fixed + log proof | Log read | Ignored |
| Dump skill | Dominator analysis | Dump taken | Missing |
| Memo quality | Repro steps + risks | Claims listed | No evidence |

Pass >= 70. Stretch: container-memory (`cgroup`) ceiling test; async-profiler
flame graph; `-XX:+HeapDumpOnOutOfMemoryError` runbook.
