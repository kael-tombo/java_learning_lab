# History: JIT Compilation

Confident facts only; no invented dates or attributions.

## HotSpot: two compilers

HotSpot shipped with two JIT compilers: C1 (client, fast compile, light
optimization, quick startup) and C2 (server, slow compile, aggressive
speculative optimization). For years users chose with `-client`/`-server`.

## Tiered compilation

Tiered compilation (tiers 0-4, interpreter plus two C1 profiling levels
feeding C2) unified the two compilers into one adaptive pipeline. Tier 3
— C1 with full branch and type profiling — exists to give C2 trustworthy
data. The modern JDK runs tiered by default (`TieredCompilation=true`),
with `TieredStopAtLevel` as the experimental cap.

## Thresholds as measurements, not lore

Older documentation quoted single `CompileThreshold`-style numbers from
the non-tiered era. Under tiering the operative knobs are the four
measured here (`Tier3InvocationThreshold=200`,
`Tier4InvocationThreshold=5000`, plus the 60000/40000 back-edge pair and
the 2000/15000 compile-threshold scalers). `CompileThreshold=10000`
survives only for the non-tiered path.

## Graal: JEP 317 and JEP 410

JEP 317 (JDK 10) introduced the experimental Java-based Graal compiler
through JVMCI (`-XX:+UnlockExperimentalVMOptions -XX:+UseJVMCICompiler`).
JEP 410 (JDK 17) removed that experimental OpenJDK integration; Graal
continues as the JIT inside GraalVM distributions, not stock OpenJDK.

## What did not change

The deoptimization contract has been stable throughout: speculative code
plus uncommon traps plus interpreter fallback. New compilers changed
which speculations fire, never the rule that a failed speculation resumes
correctly in the interpreter.

## Tiering as the settled default

The `-client`/`-server` split survives only as history: modern launches
run tiered unless capped, and `TieredStopAtLevel` exists precisely so
experiments can revisit the old single-compiler behavior on demand. The
`CapTiers` probe (correct output, zero tier-4 lines under level 1) is the
executable version of that history — one flag recovering the client-only
past for comparison.
