# MINI PROJECT — Performance: Kill the p99 Outlier

## Goal (2 weeks, ~8–10h)
Profile a rigged `search-api` (regex-per-call, synchronized cache, boxed
streams) and cut p99 50% with flame-evidenced fixes plus a CI bench gate.

## Requirements
### Functional
1. Workload: `search-api` + k6/loop driver (1k rps, 5 min) recording p50/p99
   + throughput; JFR `profile` + async-profiler wall/CPU/alloc per run.
2. Finds (min 3, each flame-linked): per-call `Pattern.compile`, `synchronized`
   cache (lock flame), boxing/`Collectors` churn (alloc flame).
3. Fixes: hoisted `static final Pattern`, `ConcurrentHashMap`/Caffeine,
   primitive/pooled path; one change per run with before/after flames.
4. JMH: microbench the three idioms (regex, map-get, concat) with warmup +
   forks + Blackhole; publish ops/s + alloc-rate table.
5. Gate: CI script failing PR if p99 regresses > 10% or alloc > budget;
   planted-regression proof (revert one fix, gate goes red).

### Non-functional
- Evidence pack per run: flame SVG + JFR + GC log + `jcmd Thread.print`
  during peak (lock proof) + `GC.heap_dump` if leak suspected.
- 12+ tests: cache correctness under contention, regex equivalence,
  gate script unit tests.
- README: top-3 frames table (method, % samples, fix, delta).

## Phases
### Week 1 — Profile (4–5h)
- Steps: driver + baseline flames (wall/CPU/alloc/lock), name top 3.
- Deliverable: ranked flame report.

### Week 2 — Fix + Gate (4–5h)
- Steps: 3 fixes (re-profile each), JMH table, gate + planted proof.
- Deliverable: p99 chart + evidence pack.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–15) | Fail (<12) |
|-----------|----------------|--------------|------------|
| Profiling | 3 views, top frames named | One flame | No flame |
| Fixes | Each flame-linked + re-measured | Fixed | Unmeasured |
| JMH rigor | Warmup/forks/BH correct | Runs | NanoTime loop |
| Macro proof | p99 -50% at same rps | Improved | Local only |
| Gate | Blocks planted regression | Exists | Missing |

Pass >= 70. Stretch: lock-free vs striped-map shootout; JFR `jdk.ObjectAllocationSample`
budget alert; capacity-headroom model.
