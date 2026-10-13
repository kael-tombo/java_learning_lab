# Common Mistakes: JIT Compilation

## 1. Calling tier 3 "C2"

Tier 3 is C1 with full profiling; C2 exists only at tier 4. The confusion
comes from assuming higher numbers mean the server compiler earlier.
Check the log's tier column against THEORY: `burn 3` is still C1.

## 2. Quoting folklore thresholds

Tables listing 1500/10000-style invocation thresholds describe no current
default. The measured values are 200 (tier 3) and 5000 (tier 4) for
invocations, 60000/40000 for back-edges, from `PrintFlagsFinal` on JDK 23.
Read the flags; do not memorize blogs.

## 3. Benchmarking cold code

Timing the first thousand iterations measures the interpreter and C1, not
the system under test. Warm past 5000+ invocations first, or your "result"
is off by the ~29x gap snippet 4 demonstrates.

## 4. Using develop-only flags

`-XX:+PrintDeoptimizationDetails` fails on product builds because it was
never compiled in. The supported spelling is `-XX:+UnlockDiagnosticVMOptions
-XX:+TraceDeoptimization`. One letter of difference, one working JVM.

## 5. Treating -Xint as a tier control

`-Xint` disables the entire compiler pipeline; `TieredStopAtLevel` caps it.
Using `-Xint` to ask "what would C1-only do" answers a different question
(no compilation at all) and confounds the experiment.

## 6. Expecting inlining of large or megamorphic callees

A 400-byte method will not inline at a lukewarm site (past
`FreqInlineSize=325`), and a site with many receiver types will not
speculate on one. The fix is smaller, hotter, more monomorphic call
shapes — not another flag.

## 7. Sharing probe sources across snippets by reference

Copying one `PROBE` constant between files creates a hidden compile-order
dependency. This lab duplicates each probe per snippet so any single file
compiles standalone; follow the same rule in your own experiments.
