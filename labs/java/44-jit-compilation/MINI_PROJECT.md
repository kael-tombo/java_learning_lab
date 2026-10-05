# MINI PROJECT — JIT Compilation: Deopt Hunter Benchmark Suite

## Goal (2 weeks, ~8–10h)
Build a JMH suite with 5 paired benchmarks (mono vs megamorphic,
inlineable vs too-big, escaping vs non-escaping, intrinsic vs loop,
branch-predictable vs random) plus PrintCompilation/JFR evidence for
each verdict.

## Requirements
### Functional
1. JMH module: 5 pairs, each with `@Warmup/@Measurement/@Fork`,
   Blackhole consumption, dead-code-elimination-safe shapes; README
   shows ops/s + error bars per pair.
2. Inlining pair: `final` monomorphic call (inlined) vs 5-impl
   megamorphic switch; `-XX:+PrintCompilation -XX:+PrintInlining`
   excerpt proves inline vs virtual.
3. Escape pair: scalar-replaceable point math (0 alloc with
   `-XX:+PrintEscapeAnalysis` or profiler alloc=0) vs escaping-box
   version (alloc rate quantified via JFR `jdk.ObjectAllocation`).
4. Deopt exhibit: speculative-monomorphic loop that flips to second
   type mid-run; JFR `jdk.Deoptimization` / `made not entrant` log
   captured and explained.
5. Intrinsic demo: `System.arraycopy` / `Integer.compareUnsigned`-style
   intrinsic vs hand loop; `-XX:+PrintIntrinsics` note.
6. Cold-vs-warm endpoint: one HTTP-ish handler measured at iteration
   1 vs 20k with tiered vs `-Xint` comparison table.

### Non-functional
- JMH correctness: no constant-folding, no DCE, forks ≥ 2, results
  JSON committed; re-run variance <10% documented.
- Artifacts: `compilation.log` excerpts, JFR `jdk.Compilation*`
  events, async-profiler flame diff (hot frame shrinks after warm).
- README: per-pair "compiler story" (5 lines each: profile → decision).
- Build: `mvn -Pjmh verify` reproduces everything offline.

## Starter Layout
```
src/jmh/java/com/lab44/bench/{DispatchBench,InlineBench,EscapeBench,
  IntrinsicBench,BranchBench}.java
scripts/run-jmh.sh  logs/compilation.log  jfr/jit.jfr
```

## Phases
### Week 1 — Harness + Pairs (4–5h)
- JMH skeleton + 5 pairs running with sane numbers.
- Deliverable: JSON results + obvious anomalies flagged.
### Week 2 — Compiler Proof (4–5h)
- PrintCompilation/inlining/escape/deopt evidence per pair.
- Deliverable: verdict report with log excerpts.

## Test Plan
- Sanity: `-Xint` run 5–20x slower than tiered (proves JIT matters).
- Stability: 3 re-runs, winning variant wins 3/3.
- DCE guard: Blackhole + `@State(Scope.Thread)` audit on each bench.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| JMH rigor | Forks/warmup/BH/error bars | Runs | Single-shot timing |
| Inlining | Log-proven verdict | Claimed | No logs |
| Escape/alloc | JFR alloc delta quantified | Noted | Ignored |
| Deopt | Captured + explained | Mentioned | Missing |
| Cold/warm | Tiered vs Xint table | Warm noted | Cold numbers only |

Pass ≥ 70. Stretch: `-XX:CompileCommand` to force/block inline and
show the delta; PerfAsm (`-XX:+UnlockDiagnosticVMOptions`) read of
one hot loop.

## Demo Checklist
- [ ] Live: cold run slow → warm run fast on same bench
- [ ] Point at inlining log line and translate it
- [ ] Show deopt event aligned with shape flip
- [ ] Flame graph before/after warm side by side

## Common Traps
Microbenchmark without JMH, `System.nanoTime` loops with DCE,
concluding from a single fork — all auto-fail.
