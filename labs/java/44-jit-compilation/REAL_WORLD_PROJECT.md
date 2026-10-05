# REAL-WORLD PROJECT — JIT: Deopt Storm After a "Harmless" Refactor

## Incident Scenario
A "cleanup" makes a hot pricing interface megamorphic (5 new impls
via ServiceLoader) and grows the hottest method past the inline
limit. p99 climbs 40ms → 320ms with no traffic change, no GC change.
Dashboards blame "CPU saturation" — but CPU is the JIT undoing itself.

## Symptoms
- p99 8x on one endpoint only; throughput down 30%; CPU +45% with
  identical RPS — work per request exploded.
- `-XX:+PrintCompilation` shows `made not entrant` storm on
  `PriceEngine.apply` (deopt every few seconds); C2 recompiles loop.
- JFR `jdk.Deoptimization` + `jdk.CompilationFailure` counts spike
  exactly at deploy; `jdk.ObjectAllocationInNewTLAB` up (escape lost).
- async-profiler: previously inlined `apply` frame now appears as
  separate fat frame + virtual dispatch (`itable` stub) on top.
- Rollback restores p99 in minutes — code-shape, not capacity.

## Investigation Tasks
1. Compiler timeline: enable `-XX:+PrintCompilation
   -XX:+PrintInlining` on one canary; `grep "made not entrant\|
   deoptimized" compilation.log | head`; map to deploy timestamp.
2. JFR: `jcmd <pid> JFR.start name=jit settings=profile duration=180s
   filename=jit.jfr`; count `jdk.Deoptimization`,
   `jdk.CompilerInlining`, `jdk.ObjectAllocationInNewTLAB` in JMC.
3. Shape forensics: heap/`jcmd GC.class_histogram` + code diff —
   count `PriceEngine` impls loaded (1 → 6); measure hottest method
   bytecode size vs `MaxInlineSize/FreqInlineSize`.
4. CPU proof: async-profiler `alloc + cpu` 60s before/after; confirm
   dispatch + allocation frames, while `jcmd GC.heap_dump` shows GC
   healthy (rule out heap blame).
5. Repro: JMH mono-vs-mega pair on staging build; show 3–5x delta
   matching prod ratio.

## Root Cause
Profile-guided speculation invalidated: monomorphic → megamorphic
dispatch (no inline) plus oversized hot method (no inline, no escape).
Every request pays dispatch + allocation that used to be free.

## Resolution
- Immediate: roll back to 1-impl dispatch (feature-flag the 5 new
  impls off); split hot method into sub-40-byte inlineable pieces.
- Short-term: seal dispatch (`sealed` + exhaustive switch or single
  impl per path), `-XX:CompileCommand` guard on `PriceEngine.apply`,
  deopt-rate alert; keep method-size lint (`MaxInlineSize` budget).
- Long-term: JIT-aware review checklist (dispatch cardinality +
  hot-method size); JMH guard benchmarks in CI failing on >15% regression.

## Runbook
```
1. Capture PrintCompilation + JFR 180s + profiler 60s BEFORE rollback.
2. Roll back / flag off new impls; verify made-not-entrant rate -> 0.
3. Split hot method; canary with CompileCommand + JMH numbers.
4. Roll 100%; verify p99 320ms -> 40ms, CPU -45%, alloc flat.
5. Land deopt + inline-failure + JMH-regression alerts.
6. Postmortem: dispatch-cardinality rule + method-size budget.
```

## Metrics
| Signal | Before | After | Gate |
|--------|--------|-------|------|
| p99 price | 320ms | 40ms | SLO 100ms |
| Deopts/min | ~900 | <5 | Alert >50 |
| CPU/RPS | +45% | baseline | Autoscale guard |
| Alloc/op | 3.2KB | 0.1KB | JFR alloc budget |
| JMH dispatch | 5x slower | 1x (mono) | CI fail >15% |

## Prevention Checklist
- [ ] Dispatch cardinality review on hot interfaces
- [ ] Hot-method size budget enforced
- [ ] Deopt-rate dashboard + alert
- [ ] JMH regression suite in CI

## Failure-Injection Drill
- Reproduce on staging with fault injection (latency + error 5%).
- Capture JFR + `jcmd Thread.print` + heap dump during the drill.
- Verify alerts fire in <2 min and runbook step 1–3 completes <15 min.

## Interview Debrief
- Explain the signal that distinguished this root cause in 2 minutes.
- Whiteboard the before/after data path with the bounding fix circled.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- HotSpot / JIT tuning docs: https://docs.oracle.com/en/java/javase/21/
- OpenJDK HotSpot compiler wiki: https://openjdk.org/groups/hotspot/
