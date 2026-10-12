# Internals: Atomic Classes

## Primary sources (read these, not blogs)
- `java.base/java/util/concurrent/atomic/AtomicInteger.java` (JDK 23), `Striped64.java` class javadoc, `VarHandle` specs, JSR-166 (2004, Doug Lea)
- `java.lang.Thread`, `java.lang.Object` (wait/notify), `java.util.concurrent.locks.LockSupport`
- `java.util.concurrent.atomic.*`, `java.lang.invoke.VarHandle` specifications

## What the source shows
1. **Data structures:** `AtomicInteger.value` (volatile int) + `VALUE` field offset, Unsafe intrinsic `U.getAndAddInt` (= `lock cmpxchg` on x86), VarHandle-specified effects, CAS retry loop, (reference,stamp) pairs, `Striped64` cells + base with `@Contended` padding.
2. **Entry points:** `compareAndSet/compareAndExchange/weakCompareAndSet`, `getAndIncrement/getAndAdd/getAndUpdate/accumulateAndGet`, `AtomicStampedReference/AtomicMarkableReference`, `LongAdder.increment/sum/sumThenReset`, `LongAccumulator`, `DoubleAdder`.
3. **Memory effects** are specified in JLS 17.4 / VarHandle javadoc; the machine code is fences or `lock`-prefixed instructions selected by the JIT per platform.

## How to verify locally (JDK 17+)
```
javap -c -p YourClass.class     # look for monitorenter/monitorexit, volatile AccessFlags, Unsafe/VarHandle calls
jstack <pid>                    # Thread.State tokens + 'waiting to lock' / 'parking' lines
jcmd <pid> Thread.print         # same as jstack via diagnostic command
java -XX:+PrintFieldLayout -version  # field layout when reasoning about padding/contention
```

## Lab-specific source notes
- Every RMW linearizes at the winning CAS; losers retry (lock-free: some thread progresses, yours may starve); functions passed to getAndUpdate re-execute on retry (side-effect-free only; expect repeated runs under contention); ABA needs identity freshness/stamps/marks; LongAdder.sum() is a fuzzy non-atomic snapshot; weakCompareAndSet is retry-loops-only; two atomics cannot transact (multi-variable invariants need a lock or single packed CAS).

## Implementation details that are safe to rely on
1. Only the specified semantics (JLS/VarHandle/javadoc contracts), never the machine code shape.
2. Lock levels, inflation/deflation, cell growth, and fence selection are adaptive — semantics stay fixed while tactics change.
3. Thread-state tokens and stack-trace parentheticals (`on object monitor`, `parking`, `sleeping`) are the stable diagnostic surface.

## What not to do
- Do not branch application logic on `getState()` output or fuzzy sums; both are observations, not synchronization.
- Do not depend on timing, fairness, or scheduling order; none is specified.
