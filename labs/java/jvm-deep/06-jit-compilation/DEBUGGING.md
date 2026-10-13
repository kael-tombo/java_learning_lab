# Debugging: JIT Compilation

## Reading PrintCompilation

Run with `-XX:+PrintCompilation` and find your method name. The tier
column tells you how far it promoted: 3 means profiling C1, 4 means C2.
Absence of a line means the method never crossed 200 invocations (or its
back-edge equivalent) — call it more before concluding anything.

The `%` suffix marks on-stack replacement: a loop-heavy method swapped
implementations mid-iteration. Expect `%` variants on `burn()`-shaped
kernels; their absence on straight-line code is normal.

## Reading PrintInlining

Add `-XX:+UnlockDiagnosticVMOptions -XX:+PrintInlining` and grep for the
callee. `inline (hot)` confirms the JIT agreed the call was worth
dissolving. `too big` cites the size budget (`MaxInlineSize=35` vs
`FreqInlineSize=325`); `megamorphic` means the profile saw too many
receiver types to speculate on one.

## Tracing deoptimization

Add `-XX:+UnlockDiagnosticVMOptions -XX:+TraceDeoptimization` around the
suspect workload. Each trap line names the method and reason (unstable
class, failed null check, wrong receiver). A burst of traps after a
deploy points at a profile invalidation, not a regression in logic.

## Common failure signatures

No tier-4 line for a hot method: check `TieredStopAtLevel` (someone capped
it at 1) or code-cache fullness (compilation silently stops). Startup
failure mentioning `PrintDeoptimizationDetails`: that flag is develop-only
and absent from product builds — switch to `TraceDeoptimization`.

## Controlled experiments

Use `-XX:TieredStopAtLevel=1` to force C1-only and `=4` for full pipeline
(default). Never use `-Xint`/`-Xcomp` for tier questions: they replace the
pipeline instead of capping it. Change one flag, re-run the same probe,
diff the tier columns — that diff is the experiment result.

## JITWatch for the visual pass

Feed the compilation log plus sources to JITWatch
(github.com/AdoptOpenJDK/jitwatch) to see per-bytecode assembly and inline
trees when text logs stop being enough.
