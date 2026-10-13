# Architecture: JIT Compilation

## Pipeline stages

Interpreter (tier 0) executes everything first and owns the counters:
invocation counts per entry, back-edge counts per loop. No compiled code
exists yet; branch and type profiles accumulate here.

C1 (tiers 1-3) compiles fast with low overhead. Tier 1 skips profiling,
tier 2 keeps invocation counters only, tier 3 gathers full branch and
type profiles. Output is correct but modestly optimized native code.

C2 (tier 4) consumes the profiles from tiers 0-3 and emits speculative,
heavily optimized code: inlining, escape analysis, loop transforms,
range-check elimination. Every speculation carries a deoptimization path.

## Data flow

Bytecode plus profiles flow forward (interpreter -> C1 -> C2). Guard
failures flow backward (compiled frame -> uncommon trap -> interpreter ->
recompile with weaker assumptions). The queue between profiler and
compilers is asynchronous: hotness only schedules a compile task.

## Where state lives

Counters live in the method data object (MDO). Profiles (receiver types,
branch frequencies, call targets) live alongside it. Compiled artifacts
live in the code cache (`ReservedCodeCacheSize=240M` measured). When the
cache fills, compilation stops and code stays interpreted.

## Control points

`TieredCompilation` enables the pipeline. `TieredStopAtLevel` caps it for
experiments (1 = C1 only, 4 = full C2). `PrintCompilation` exposes the
third-column tier per compile. `PrintInlining` exposes per-callsite
decisions against `MaxInlineSize=35` / `FreqInlineSize=325`.

## Failure modes

Stale profiles after class redefinition force deoptimization. Code-cache
exhaustion silently freezes optimization. Over-aggressive speculation on
megamorphic call sites recompiles repeatedly instead of settling.
