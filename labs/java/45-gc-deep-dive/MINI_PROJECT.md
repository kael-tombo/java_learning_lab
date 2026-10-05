# MINI PROJECT — GC Deep Dive: Collector Bake-Off Under Pressure

## Goal (2 weeks, ~8–10h)
Run the same allocation-heavy order service under G1, ZGC, and
Parallel with `-Xlog:gc*` + JFR, then recommend one with numbers —
including one allocation fix that beats any flag change.

## Requirements
### Functional
1. Workload app: HTTP-ish order ingest with JSON churn, boxed
   streams, and occasional humongous `byte[]` (configurable MB/s);
   exposes p50/p99 + GC pause stats endpoint.
2. Three flag sets committed: `g1.flags`, `zgc.flags`,
   `parallel.flags` (heap, pause goal, thread counts pinned for test).
3. Load script (k6/gatling-lite or Java driver): 10-min steady + 2-min
   burst per collector; same seed/RPS; GC logs + JFR per run saved.
4. Allocation fix: remove top churn (e.g., `String.format` in loop →
   builder, boxed `Stream<Integer>` → primitive, cached headers) and
   re-run winner; allocation rate (MB/s) delta in README.
5. Humongous exhibit (G1): force `byte[8MB]` bursts; show mixed-GC /
   humongous lines in `Xlog:gc*` and JFR `GarbageCollection` phases.
6. OOM-safety: `HeapDumpOnOutOfMemoryError` + `ExitOnOutOfMemoryError`
   wired; one promotion-failure scenario documented (too-small heap).

### Non-functional
- 12+ tests: workload invariants, flag files parse, humongous path,
  no-`System.gc` ArchUnit rule, log-presence assertions.
- Artifacts: 3 GC logs, 3 JFR files, pause histogram chart (CSV +
  rendered), allocation flame (async-profiler alloc mode).
- README table: p50/p99/max pause, throughput, CPU, footprint, verdict.
- Repro: `scripts/bakeoff.sh` runs all three unattended.

## Starter Layout
```
src/main/java/com/lab45/load/{Workload,OrderHandler,Churn}.java
flags/{g1.flags,zgc.flags,parallel.flags}
scripts/{bakeoff.sh,analyze.sh}  results/{logs,jfr,csv}
```

## Phases
### Week 1 — Harness + Baseline (4–5h)
- Workload + drivers + 3 flag sets; first bake-off captured.
- Deliverable: raw logs + pause table draft.
### Week 2 — Fix + Verdict (4–5h)
- Allocation fix, humongous exhibit, final recommendation.
- Deliverable: verdict report with charts + runbook snippet.

## Test Plan
- Same-seed replay: request counts identical across collectors ±1%.
- Pause attribution: longest JFR GC event matches log's longest pause.
- Fix proof: alloc MB/s down ≥ 30%, p99 improved on same collector.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Workload | Realistic churn + burst | Runs | Toy loop |
| Bake-off | 3 collectors, same seed | 2 compared | Single run |
| Logs/JFR | Phase-level reading | Captured | Missing |
| Alloc fix | ≥30% cut, proven | Fixed | Flag-only |
| Verdict | Numbers + tradeoff + runbook | Picked | Vibes |

Pass ≥ 70. Stretch: Shenandoah 4th runner; generational-ZGC vs
non-generational comparison with CPU delta.

## Demo Checklist
- [ ] Pause histogram overlay (3 collectors, one chart)
- [ ] Point at humongous/G1-mixed lines in the log live
- [ ] Allocation flame: top frame before → gone after
- [ ] Verdict: "use X because p99/CPU/footprint table says so"

## Common Traps
Comparing different heaps/RPS, benchmarking with cold JIT, tuning
flags before measuring allocation — all auto-fail.
