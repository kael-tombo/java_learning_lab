# README — JIT Compilation

Hot bytecode runs on the interpreter first; hot methods get compiled to
native code in tiers. This lab makes that pipeline visible and measurable.

## What you will observe [measured]

- `burn()` compiles at tier 3 (~200 invocations) then tier 4 C2 (~5000).
- `TieredStopAtLevel=1` keeps the program correct with no tier-4 compiles.
- A 3-byte `tiny()` callee inlines once hot (see `PrintInlining` output).
- `-Xint` vs default JIT differs by well over 3x on loop-heavy integer work
  (~29x in the reference run; ratio-based assertion tolerates machine noise).
- `PrintFlagsFinal` reads pin `Tier4InvocationThreshold=5000`,
  `MaxInlineSize=35`, `FreqInlineSize=325`, `TieredCompilation=true`.

## Tier model (THEORY.md)

Tiers 0-4. Tier 3 is C1 *with* full profiling; C2 exists only at tier 4.
Thresholds: Tier3Invocation 200, Tier4Invocation 5000, Tier3BackEdge 60000,
Tier4BackEdge 40000, Tier3Compile 2000, Tier4Compile 15000.
`CompileThreshold=10000` is the non-tiered path only.

## Key flags

`-XX:+PrintCompilation`, `-XX:+PrintInlining`,
`-XX:+UnlockDiagnosticVMOptions -XX:+TraceDeoptimization`,
`-XX:TieredStopAtLevel={1..4}`, `-Xint` (diagnostic contrast only).

## Files

THEORY.md is the threshold table. CODE_DEEP_DIVE.md holds the five runnable
probes. HOW_IT_WORKS.md traces one method birth to C2. DEBUGGING.md shows
how to read the logs. PERFORMANCE.md explains warmup discipline.

## Exit criteria

You can predict which tier a method reaches, read an inline decision, and
explain a deoptimization as uncommon-trap plus recompile without quoting
folklore thresholds.

## Threshold pocket reference

Tier 3 entry: 200 invocations / 60000 back-edges. Tier 4 entry: 5000 /
40000. Compile scalers: 2000 / 15000. Non-tiered fallback:
`CompileThreshold=10000`. Inline budgets: 35 regular, 325 hot (C1 caps at
35). Keep this card beside every log you read in this lab.
