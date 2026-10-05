# MINI PROJECT — JVM Tuning: Right-Size a Containerized Service

## Goal (2 weeks, ~8–10h)
Take an over-provisioned (4GB/2CPU, random flags) order service and
ship a tuned manifest: measured heap, chosen collector, container-fit
proof, and a rollback-ready flag file.

## Requirements
### Functional
1. Baseline capture: `GC.heap_info`, NMT baseline, `Xlog:gc*` 10-min
   run, JFR 5-min run at fixed RPS; record live-set (heap after GC),
   alloc rate, p50/p99, CPU throttle %.
2. Heap math: `-Xmx` from live-set × 3.5 (show arithmetic) via
   `MaxRAMPercentage=65–75` (not hardcoded Xmx) + explicit
   `InitialRAMPercentage`; metaspace + direct + thread-stack budget
   table vs cgroup `memory.max`.
3. Collector pick: G1 vs ZGC 10-min bake-off at same RPS; choose by
   pause SLO (e.g., p99 <300ms) + CPU cost; commit `jvm.flags` + rationale.
4. Thread right-size: platform pool = nCPU, virtual for I/O, G1
   `ConcGCThreads`/`ParallelGCThreads` capped for 2CPU; prove throttle
   % drops in `cpu.stat` / container metrics.
5. Startup trim: CDS archive (`-Xshare:on`) or AppCDS note + lazy-init
   audit; record startup ms before/after.
6. Safety: `HeapDumpOnOutOfMemoryError`, `ExitOnOutOfMemoryError`,
   `CrashOnOutOfMemoryError` policy + tested rollback manifest.

### Non-functional
- 12+ tests: flag-file parse, heap-math unit test, container-limit
  assert (Xmx+NMT+direct < limit), no `System.gc` rule.
- Artifacts: gc.logs, JFRs, NMT diffs, k8s manifest diff
  (before/after resources + flags), cost delta ($/mo estimate).
- Soak: 30-min run, zero OOMKill, throttle <5%, p99 within SLO.
- README: sizing worksheet (live-set → flags → headroom).

## Starter Layout
```
src/main/java/com/lab46/svc/{OrderService}.java
flags/{baseline.flags,tuned.flags}  k8s/{deploy-before.yaml,deploy-after.yaml}
scripts/{capture.sh,soak.sh}  results/{gc,jfr,nmt}
```

## Phases
### Week 1 — Measure (4–5h)
- Baseline JFR/gc.log/NMT + heap math + first flag draft.
- Deliverable: sizing worksheet filled with real numbers.
### Week 2 — Tune + Prove (4–5h)
- Bake-off, thread caps, startup trim, soak + rollback drill.
- Deliverable: tuned manifest + cost/slo report.

## Test Plan
- Limit test: tuned flags under `memory.max` simulator, no OOMKill.
- Rollback: apply `deploy-before.yaml`, service recovers <2 min.
- Regression: same-seed load, tuned p99 ≤ baseline p99.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Heap math | Live-set arithmetic shown | Sized | Copied flags |
| Collector | Bake-off + CPU cost | Picked w/ reason | Default only |
| Container fit | NMT+stack+direct budget | Fits | OOMKill risk |
| Soak/SLO | 30-min green + throttle | Short run | No soak |
| Rollback/cost | Tested + $ delta | Documented | Missing |

Pass ≥ 70. Stretch: `-XX:+UseCompactObjectHeaders` experiment;
Kubernetes VPA recommendation comparison.

## Demo Checklist
- [ ] Worksheet: live-set → flags → headroom in one page
- [ ] gc.log pause overlay before/after
- [ ] NMT diff + cgroup fit bar chart
- [ ] Rollback drill live (<2 min)

## Common Traps
Hardcoded Xmx above cgroup limit, unlimited GC threads on shared
CPU, tuning 5 flags at once — all auto-fail.
