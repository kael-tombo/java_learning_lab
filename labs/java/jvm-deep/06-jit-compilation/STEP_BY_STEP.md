# Step by Step: JIT Compilation

1. Compile the `HotLoop` probe with `javac` into a temp directory so the
   experiment never pollutes the repo.
2. Launch it with `-XX:+PrintCompilation` and 300,000 calls to `burn(200)`.
3. Grep the log for `HotLoop::burn`. Confirm a tier-3 line appears first.
4. Confirm a tier-4 line appears later. The method crossed 200 then 5000
   invocations exactly as THEORY predicts.
5. Re-run with `-XX:TieredStopAtLevel=1`. Confirm output still prints the
   correct total but no tier-4 line exists anywhere.
6. Swap to the `InlineMe` probe (500,000 calls to 3-byte `tiny`). Run with
   `-XX:+UnlockDiagnosticVMOptions -XX:+PrintInlining`.
7. Find the `tiny` inline line. Note it cites hotness plus small size.
8. Run `LoopWork` under `-Xint`, record milliseconds. Run again with the
   default pipeline, record milliseconds. Confirm the JIT run is faster by
   more than 3x.
9. Query `-XX:+UnlockDiagnosticVMOptions -XX:+PrintFlagsFinal -version` and
   verify `TieredCompilation=true`, `DoEscapeAnalysis=true`,
   `Tier4InvocationThreshold=5000`, `MaxInlineSize=35`.
10. Pick one threshold, change it deliberately (for example
    `-XX:Tier4InvocationThreshold=500`), re-run step 2, and watch tier 4
    arrive earlier in the log order.
11. Cross-check the back-edge path: run a single-call loop-heavy probe and
    confirm `%` (on-stack replacement) variants appear, proving promotion
    can trip mid-loop rather than only at method entry.
12. Negative control: pass `-XX:+PrintDeoptimizationDetails` once, watch
    startup fail, and record why product builds reject it — then use
    `TraceDeoptimization` for the real deoptimization trace.
13. Capture one `PrintInlining` line for a hot callee and annotate which
    budget it passed (size under 35/325, hotness past tier thresholds) —
    the decision made legible in a single annotated line for your notes.
