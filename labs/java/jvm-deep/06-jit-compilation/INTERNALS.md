# Internals: JIT Compilation

## Counters and the MDO

Each method owns a method-data object holding invocation and back-edge
counters plus type and branch profiles. Tier transitions read scaled
versions of these counters: `Tier3CompileThreshold=2000` and
`Tier4CompileThreshold=15000` weight raw counts by method size and tier
history, so small methods promote sooner than large ones.

## Tier encoding in the log

`PrintCompilation` prints one line per compile; the third column is the
tier (1-4) and `%` marks on-stack replacement for loop-heavy frames.
Seeing `HotLoop::burn 3` then `HotLoop::burn 4` is the normal promotion
sequence, not two compilers racing.

## Inlining budgets

C1 caps regular inlining at `C1MaxInlineSize=35` bytes. C2 allows 35
bytes for ordinary call sites and 325 bytes (`FreqInlineSize`) for hot
ones. Hotness here means tier-3/tier-4 invocation history, caller heat,
and call-site frequency — not source-level size alone.

## Escape analysis path

C2's `DoEscapeAnalysis` plus `EliminateAllocations` (both default true,
verified via `PrintFlagsFinal`) prove when an object never escapes its
allocating method or thread. Scalar replacement then dissolves the
object into registers or stack slots: no allocation, no GC pressure.

## Deoptimization mechanics

Speculative code embeds uncommon traps at each assumption. A trap builds
an interpreter frame from the compiled frame's live values (deoptimization
blob), resumes interpretation at the right bytecode, and flags the method
for recompile. Repeated traps on one site widen or drop the assumption.

## Diagnostic surface

`TraceDeoptimization` (needs `UnlockDiagnosticVMOptions`) logs each trap.
`PrintDeoptimizationDetails` does not exist in product builds — asking for
it fails startup, which is itself the lesson about develop-only flags.
