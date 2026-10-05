# MINI PROJECT — Performance Antipatterns: Exterminate the Rogues' Gallery

## Goal (2 weeks, ~8–10h)
Take a checkout service seeded with 10 classic antipatterns and kill
them one by one — each with trace/flame/JFR proof and a lint rule so
it never returns.

## Requirements
### Functional
1. Fix all 10 (seeded): N+1 fee queries, `String` concat in loop,
   boxed-stream pricing, `SimpleDateFormat` per-call + static race,
   regex recompile per request, row-by-row JDBC, missing batch,
   exception-as-control-flow for validation, `synchronized` log path,
   uncached auth introspection per item.
2. Call-count proof: trace waterfall per request — fee/auth calls
   40+1 → 2 batched; JDBC round trips counted via datasource proxy
   (P6Spy-style or counter); README table per fix.
3. Alloc proof: JFR `ObjectAllocationInNewTLAB` MB/s before/after
   (target ≥50% cut); async-profiler alloc flame shrinks visibly.
4. CPU proof: cpu flame top-5 frames change; p50/p99 + throughput at
   fixed RPS tabulated (k6/hey driver, same seed).
5. Cache discipline: exactly one bounded cache (Caffeine, max +
   TTL) with invalidation test; no unbounded maps (ArchUnit rule).
6. Lint wall: one automated check per fix (ArchUnit/Error Prone/
   regex-grep test) — reintroducing any antipattern fails the build.

### Non-functional
- 18+ tests: one regression test per antipattern (fails on old code
  shape), plus parity (totals identical to the cent).
- Artifacts: traces, flames (cpu+alloc), JFR excerpts, load CSVs.
- Soak 15 min: p99 stable, alloc flat, no cache unbounded growth.
- README: gallery table (symptom → profiler signature → fix → delta).

## Starter Layout
```
src/main/java/com/lab52/shop/{CheckoutService,FeeRepo,AuthClient,Pricing}.java
src/test/java/.../{AntipatternRegressionTest,ParityTest}.java
scripts/{load.sh,flames.sh}  results/{jfr,flames,csv}
```

## Phases
### Week 1 — Calls + Strings (4–5h)
- Batch N+1s/JDBC, cache auth, fix concat/regex/date hot paths.
- Deliverable: calls/request table collapsed + first flame delta.
### Week 2 — Alloc + Guards (4–5h)
- Boxing/exception/log-lock fixes, lint wall, soak.
- Deliverable: gallery report with 10 measured kills.

## Test Plan
- Golden totals: 5k-order replay identical pre/post (cent-exact).
- Per-fix test: e.g., fee-repo call count == 1 for 40-item order.
- Cache test: TTL expiry + max-size eviction proven.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Call-count | 40+1→batched w/ traces | Reduced | Still N+1 |
| Alloc | ≥50% cut, JFR-proven | Cut | Unmeasured |
| CPU/p99 | Tabulated win | Improved | Claimed |
| Cache | Bounded+tested | Cached | Unbounded/none |
| Lint+tests | 10 guards + 18 tests | Partial | No guards |

Pass ≥ 70. Stretch: JDBC `rewriteBatchedStatements` + batch-size
tuning curve; log-sampling (5% debug) with cost measurement.

## Demo Checklist
- [ ] Trace waterfall: 41 spans → 2 spans live
- [ ] Alloc flame shrink + MB/s number
- [ ] Reintroduce one antipattern → build fails (lint wall)
- [ ] Load table: p99 + RPS before/after

## Common Traps
Caching without bounds/TTL, "fixing" cold code, string micro-tuning
while N+1 burns 300ms — all auto-fail.
