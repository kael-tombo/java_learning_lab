# References: JIT Compilation

Real sources only. All flag defaults verified via `PrintFlagsFinal` on
JDK 23 in this lab.

- `java -XX:+UnlockDiagnosticVMOptions -XX:+PrintFlagsFinal -version` —
  primary source for every threshold in THEORY.md (`Tier3InvocationThreshold`,
  `Tier4InvocationThreshold`, `Tier3BackEdgeThreshold`, `Tier4BackEdgeThreshold`,
  `Tier3CompileThreshold`, `Tier4CompileThreshold`, `MaxInlineSize`,
  `FreqInlineSize`, `C1MaxInlineSize`, `TieredCompilation`).
- JEP 317: Experimental Java-Based JIT Compiler (JDK 10, Graal via JVMCI).
- JEP 410: Remove the Experimental AOT and JIT Compiler (JDK 17).
- OpenJDK HotSpot source: `src/hotspot/share/compiler/` (tiered policy,
  compilation queue), `src/hotspot/share/opto/` (C2), `src/hotspot/share/c1/`
  (C1), `src/hotspot/share/runtime/deoptimization.cpp` (uncommon traps).
- JITWatch: https://github.com/AdoptOpenJDK/jitwatch — visualizes
  `PrintCompilation`/`PrintInlining` logs against bytecode and assembly.
- `java.util.concurrent.ExecutorService.close()` (since 19): the modern
  structured-shutdown API; relevant because snippet harnesses that spawn
  compiler-observation subprocesses should release their executors via
  try-with-resources rather than manual shutdown.
- `-XX:+PrintCompilation -XX:+PrintInlining -XX:+PrintAssembly` (hsdis
  needed for the last) and `-XX:+UnlockDiagnosticVMOptions
  -XX:+TraceDeoptimization`: the supported observability flags used here.
- OpenJDK HotSpot `src/hotspot/share/runtime/javaCalls.cpp` and counter
  decay paths: the mechanism behind hotness as a moving average across
  safepoints rather than a monotonic latch.
- JEP 220 (modular run-time images, JDK 9): release-train context for the
  era in which tiered compilation became the unquestioned default.
- JITWatch source docs plus `PrintAssembly` (hsdis) output: the
  per-bytecode-to-native mapping that settles arguments text logs cannot
  (which check folded, which call dissolved, which loop unrolled).
