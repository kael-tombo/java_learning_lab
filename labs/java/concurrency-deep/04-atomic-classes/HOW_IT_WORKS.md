# How It Works: Atomic Classes

## The mechanism in one paragraph
Atomic Classes is lock-free read-modify-write via CAS: AtomicX, stamped references, and striped counters. The moving parts are `AtomicInteger.value` (volatile int) + `VALUE` field offset, Unsafe intrinsic `U.getAndAddInt` (= `lock cmpxchg` on x86), VarHandle-specified effects, CAS retry loop, (reference,stamp) pairs, `Striped64` cells + base with `@Contended` padding, driven through `compareAndSet/compareAndExchange/weakCompareAndSet`, `getAndIncrement/getAndAdd/getAndUpdate/accumulateAndGet`, `AtomicStampedReference/AtomicMarkableReference`, `LongAdder.increment/sum/sumThenReset`, `LongAccumulator`, `DoubleAdder`, implemented as described in `java.base/java/util/concurrent/atomic/AtomicInteger.java` (JDK 23), `Striped64.java` class javadoc, `VarHandle` specs, JSR-166 (2004, Doug Lea). Every RMW linearizes at the winning CAS; losers retry (lock-free: some thread progresses, yours may starve); functions passed to getAndUpdate re-execute on retry (side-effect-free only; expect repeated runs under contention); ABA needs identity freshness/stamps/marks; LongAdder.sum() is a fuzzy non-atomic snapshot; weakCompareAndSet is retry-loops-only; two atomics cannot transact (multi-variable invariants need a lock or single packed CAS).

## Step-by-step through the parts
1. **Name the operands.** Before reasoning, write down the exact objects/fields involved (which thread, which monitor, which field, which atomic). Most bugs are wrong-operand bugs.
2. **Trace one operation end to end.** Pick a single call from `compareAndSet/compareAndExchange/weakCompareAndSet`, `getAndIncrement/getAndAdd/getAndUpdate/accumulateAndGet`, `AtomicStampedReference/AtomicMarkableReference`, `LongAdder.increment/sum/sumThenReset`, `LongAccumulator`, `DoubleAdder` and follow it: JDK entry -> HotSpot primitive -> observable result. Use INTERNALS.md source paths to confirm each hop.
3. **Add the second thread.** Re-trace with two actors interleaved. Ask at each step: which edge orders these two actions? If none, you have a race; say so explicitly.
4. **Check the exits.** Every acquisition has a release path (including exceptions/interrupts/timeouts). Verify yours, then compare with COMMON_MISTAKES.md.
5. **Confirm empirically.** Run the STEP_BY_STEP.md commands (`jstack`, `javap -c`, `jshell`) and match output against the predicted tokens/bytecodes.

## Worked trace
- Start from README.md item 4: Every RMW linearizes at the winning CAS; losers retry (lock-free: some thread progresses, yours may starve); functions passed to getAndUpdate re-execute on retry (side-effect-free only; expect repeated runs under contention); ABA needs identity freshness/stamps/marks; LongAdder.sum() is a fuzzy non-atomic snapshot; weakCompareAndSet is retry-loops-only; two atomics cannot transact (multi-variable invariants need a lock or single packed CAS).
- Reproduce it with the smallest program in STEP_BY_STEP.md, then explain each line of output using the vocabulary of `AtomicInteger.value` (volatile int) + `VALUE` field offset, Unsafe intrinsic `U.getAndAddInt` (= `lock cmpxchg` on x86), VarHandle-specified effects, CAS retry loop, (reference,stamp) pairs, `Striped64` cells + base with `@Contended` padding.

## What people get wrong
- Skipping step 1 (reasoning about "the lock" or "the flag" without saying which object/field).
- Treating monitoring output as control input (thread states, fuzzy sums).
- Assuming edges that do not exist (different monitors, plain fields, element access through a volatile array reference).

## Next
- INTERNALS.md for source paths; MATH_FOUNDATION.md for the ordering rules in symbols.

## Second trace: the retry curve made visible
- Run the hand CAS loop (CODE_DEEP_DIVE.md snippet 1) at 1, 2, 8 writers with a failure counter: retries-per-success ≈ 1, ≈ 2, ≈ 8 — the E[A] ≈ N geometry from MATH_FOUNDATION.md as measured numbers.
- Swap the counter for `LongAdder` at 8+ writers with the same harness: per-thread retries collapse (hash spread over cells) while `sum()` at rest matches the exact total — striping traded for fuzz, exactness kept at quiescence.
- Push to 32 writers on one `AtomicLong`: per-commit CPU explodes while system commits stay ~flat (one CAS latency per commit) — the saturation signature that justifies every striping decision.
- Conclusion to write down: contention on one word burns CPU per thread for fixed system progress; cells buy progress back per writer at the price of fuzzy reads.

## API-choice map (fill from your runs)
- Single cold counter / sequence number: `AtomicLong.incrementAndGet` — one CAS, exact read, no cell overhead below ~2-4 writers.
- Hot metrics counter: `LongAdder.increment` + `sum()` for dashboards — striped writes, fuzzy reads, `sumThenReset` at quiet points.
- Max/min tracking: `LongAccumulator` with operator plus identity seed — same striping, extremum semantics, same fuzz caveat.
- Conditional update with witness: `compareAndExchange` — retry from the returned value, one fewer volatile read per failed lap.
- Loops-only micro-opt: `weakCompareAndSetVolatile` inside retry loops — spurious failure costs one lap; one-shot use is a correctness bug.
- History-sensitive link: `AtomicStampedReference` / `AtomicMarkableReference` — stamps/marks where ABA is structural, fresh allocation where GC covers it.

## ABA trace (Treiber sketch)
- Nodes A -> B with top = A: thread 1 reads top (A) and A.next (B), then stalls before its CAS.
- Thread 2 pops A, pops B, pushes A back (reuse): top = A again, but A.next now differs (or freed) — same value, different history.
- Thread 1's `compareAndSet(A, C)` succeeds on the wrong A: C links where B was expected — silent structural corruption, values all "correct".
- Stamped replay: each mutation bumped the stamp (0 -> 1 -> 2); thread 1's stale-stamp CAS is rejected — history rides along as an int, at one Pair allocation per access.

## Self-check
- Cover the map above and reproduce, from live runs, the rerun-ratio proof plus the stamped-rejection verdict — both from memory, then diffed against output.
