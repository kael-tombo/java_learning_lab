# Architecture: Atomic Classes

## Components (real ones, not generic boxes)
1. **Program layer** — your code calling `compareAndSet/compareAndExchange/weakCompareAndSet`, `getAndIncrement/getAndAdd/getAndUpdate/accumulateAndGet`, `AtomicStampedReference/AtomicMarkableReference`, `LongAdder.increment/sum/sumThenReset`, `LongAccumulator`, `DoubleAdder`.
2. **JDK layer** — `AtomicInteger.value` (volatile int) + `VALUE` field offset, Unsafe intrinsic `U.getAndAddInt` (= `lock cmpxchg` on x86), VarHandle-specified effects, CAS retry loop, (reference,stamp) pairs, `Striped64` cells + base with `@Contended` padding.
3. **JVM/HotSpot layer** — scheduler, park/unpark primitives, monitor subsystem; sources in `java.base/java/util/concurrent/atomic/AtomicInteger.java` (JDK 23), `Striped64.java` class javadoc, `VarHandle` specs, JSR-166 (2004, Doug Lea).
4. **OS/hardware layer** — kernel threads, futexes/condition variables, cache coherence and fences.

## Structure
```
+------------------- program -------------------+
|  lock-free read-modify-write via CAS: AtomicX, stamped references, and striped counters                      |
+--------------- JDK (Atomic Classes) ----------------+
|  `AtomicInteger.value` (volatile int) + `VALUE` field offset, Unsafe intrinsic `U.getAndAddInt` (= `lock cmpxchg` on x86), VarHandle-specified effects, CAS retry loop, (reference,stamp) pairs, `Striped64` cells + base with `@Contended` padding   |
+----------- HotSpot / OS / hardware -----------+
|  threads, monitors, fences, schedulers        |
+-----------------------------------------------+
```

## Data flow
1. Application invokes one of: `compareAndSet/compareAndExchange/weakCompareAndSet`, `getAndIncrement/getAndAdd/getAndUpdate/accumulateAndGet`, `AtomicStampedReference/AtomicMarkableReference`, `LongAdder.increment/sum/sumThenReset`, `LongAccumulator`, `DoubleAdder`.
2. JDK maps the call onto `AtomicInteger.value` (volatile int) + `VALUE` field offset, Unsafe intrinsic `U.getAndAddInt` (= `lock cmpxchg` on x86), VarHandle-specified effects, CAS retry loop, (reference,stamp) pairs, `Striped64` cells + base with `@Contended` padding.
3. HotSpot/OS executes the primitive (thread state change, monitor op, fence, or CAS).
4. Observable effect returns: state token, mutual exclusion, visibility edge, or updated value.

## Key invariant
- Every RMW linearizes at the winning CAS; losers retry (lock-free: some thread progresses, yours may starve); functions passed to getAndUpdate re-execute on retry (side-effect-free only; expect repeated runs under contention); ABA needs identity freshness/stamps/marks; LongAdder.sum() is a fuzzy non-atomic snapshot; weakCompareAndSet is retry-loops-only; two atomics cannot transact (multi-variable invariants need a lock or single packed CAS).

## Failure modes at this layer
1. Misidentifying which component owns the state (e.g. wrong monitor object, wrong field, wrong atomic).
2. Assuming ordering that no edge provides (see MATH_FOUNDATION.md for the exact edges).
3. Confusing a monitoring signal (thread state, fuzzy sum) with a synchronization guarantee.

## Cross-references
- Mechanism: HOW_IT_WORKS.md. Sources: INTERNALS.md. Costs: PERFORMANCE.md.
