# Why It Exists: Atomic Classes

## The problem before the mechanism
Shared-memory threads interleave arbitrarily: without lock-free read-modify-write via CAS: AtomicX, stamped references, and striped counters, every multi-threaded program is a pile of races — stale reads, torn updates, lost signals, deadlocks misdiagnosed. Developers needed a specified, implementable contract rather than folklore about "flushes" and "luck".

## What this mechanism contributes
- A precise vocabulary: `AtomicInteger.value` (volatile int) + `VALUE` field offset, Unsafe intrinsic `U.getAndAddInt` (= `lock cmpxchg` on x86), VarHandle-specified effects, CAS retry loop, (reference,stamp) pairs, `Striped64` cells + base with `@Contended` padding.
- Specified operations: `compareAndSet/compareAndExchange/weakCompareAndSet`, `getAndIncrement/getAndAdd/getAndUpdate/accumulateAndGet`, `AtomicStampedReference/AtomicMarkableReference`, `LongAdder.increment/sum/sumThenReset`, `LongAccumulator`, `DoubleAdder`.
- A verifiable implementation: `java.base/java/util/concurrent/atomic/AtomicInteger.java` (JDK 23), `Striped64.java` class javadoc, `VarHandle` specs, JSR-166 (2004, Doug Lea).
- The guarantee: Every RMW linearizes at the winning CAS; losers retry (lock-free: some thread progresses, yours may starve); functions passed to getAndUpdate re-execute on retry (side-effect-free only; expect repeated runs under contention); ABA needs identity freshness/stamps/marks; LongAdder.sum() is a fuzzy non-atomic snapshot; weakCompareAndSet is retry-loops-only; two atomics cannot transact (multi-variable invariants need a lock or single packed CAS).

## What it deliberately does not do
- It does not make all concurrent code correct — compound actions, multi-variable invariants, and cross-monitor assumptions stay the programmer's job (see COMMON_MISTAKES.md).
- It does not promise fairness, timing, or performance levels — only the semantics in THEORY.md.
- It does not replace higher-level tools (executors, concurrent collections, structured concurrency) for task management.

## The alternative and why it loses
Ad-hoc reasoning ("it worked in testing", "sleep fixes it", "one more null check") passes demos and fails under load, on ARM, or after a JIT upgrade. The specified mechanism fails loudly at review time instead of silently in production.

## Bottom line
Atomic Classes exists so that ordering, exclusion, or atomicity claims can be checked against a written contract and its sources — not against machine behavior on one laptop.

## Before atomics: the lock-or-race dilemma
- Single-variable counters had two bad options: `synchronized` (monitor enter/exit, possible park, BLOCKED under contention) or plain/volatile increments (torn or lost updates) — no middle tool for the most common RMW shape.
- `volatile++` looked like a third option and was a trap: full visibility of every step with no atomicity across steps — lost updates with fresh reads, the worst confidence profile (looks correct in light tests).
- Lock-free algorithm papers (Treiber stacks, CLQ lineage) needed CAS exposed to Java: without it, every nonblocking structure stayed a C++ exhibit rather than a shipping queue.

## What JSR-166 contributed (and what it refused)
- Contributed: per-variable lock-free RMW (`getAndIncrement`, `compareAndSet`) with volatile memory effects — one instruction commits, losers retry, no monitor exists to contend.
- Contributed: the loop pattern plus functional pre-writes (`getAndUpdate`) with the purity contract stated — re-execution is normal, so side effects are excluded by specification.
- Contributed: stamped/markable references for ABA-structural links and striped counters for hot metrics — the hazard and the hotspot each got their own tool.
- Refused: multi-variable transactions (two atomics still expose intermediates — locks or packing own that), fairness across retries (lock-free promises system progress, never per-thread turns), and exact striped reads (`sum()` stays fuzzy by design).

## Why Unsafe-then-VarHandle layering
- Unsafe intrinsics (`U.getAndAddInt` on the `VALUE` offset) reach the silicon instruction (`lock cmpxchg`) with no call overhead — the mechanism layer, fast and unsupported.
- VarHandle specifications (`compareAndSet`, `getAndAdd`, access modes) state the memory effects in supported vocabulary — the contract layer programs are written against.
- The split lets the JVM re-lower the same contract per CPU (x86 CAS vs ARM LL-SC loops, weak-vs-strong) without changing source semantics — portability lives in the layering.

## The alternative, priced
- `synchronized` per increment: correct, but monitor costs plus parking under contention for a one-instruction job — contention-shaped overhead on counter-shaped work.
- `volatile` counters: benchmark-fast because update-losing — every "win" bills as drift, billed per production month, not per benchmark run.
- Hand-rolled `sun.misc.Unsafe` CAS outside the atomic classes: same instruction, zero specified effects — the next JDK re-lowering breaks you silently; `VarHandle`/atomic classes carry the specification.
