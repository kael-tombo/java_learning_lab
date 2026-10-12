# Internals: Volatile Semantics

## Primary sources (read these, not blogs)
- JLS 17.4 (happens-before), 17.5 (final-field safety), 17.7 (word tearing), JSR-133 (2004 memory-model rewrite), `VarHandle.java` (Java 9)
- `java.lang.Thread`, `java.lang.Object` (wait/notify), `java.util.concurrent.locks.LockSupport`
- `java.util.concurrent.atomic.*`, `java.lang.invoke.VarHandle` specifications

## What the source shows
1. **Data structures:** volatile field access (JLS 17.4.5), program-order/monitor/lifecycle edges, StoreLoad fences (`xchg`+`lock` on x86, `dmb ish` on ARMv8), safe-publication piggybacking, `VarHandle` access modes.
2. **Entry points:** `volatile` field read/write, double-checked locking with volatile, `AtomicIntegerArray`/VarHandle array-element volatile access, `VarHandle.getAcquire/setRelease/getOpaque` (contrast).
3. **Memory effects** are specified in JLS 17.4 / VarHandle javadoc; the machine code is fences or `lock`-prefixed instructions selected by the JIT per platform.

## How to verify locally (JDK 17+)
```
javap -c -p YourClass.class     # look for monitorenter/monitorexit, volatile AccessFlags, Unsafe/VarHandle calls
jstack <pid>                    # Thread.State tokens + 'waiting to lock' / 'parking' lines
jcmd <pid> Thread.print         # same as jstack via diagnostic command
java -XX:+PrintFieldLayout -version  # field layout when reasoning about padding/contention
```

## Lab-specific source notes
- Volatile gives visibility + access atomicity (incl. long/double) but NOT compound-action atomicity (volatile++ races: read-modify-write in three steps); DCL is correct only with volatile (or holder idiom/enum singleton); transitivity A->B->C chains edges; volatile reads are near-free on x86 (TSO) while writes need a fence, both directions need fences on ARM (qualitative only); volatile arrays cover the reference, never the elements.

## Implementation details that are safe to rely on
1. Only the specified semantics (JLS/VarHandle/javadoc contracts), never the machine code shape.
2. Lock levels, inflation/deflation, cell growth, and fence selection are adaptive — semantics stay fixed while tactics change.
3. Thread-state tokens and stack-trace parentheticals (`on object monitor`, `parking`, `sleeping`) are the stable diagnostic surface.

## What not to do
- Do not branch application logic on `getState()` output or fuzzy sums; both are observations, not synchronization.
- Do not depend on timing, fairness, or scheduling order; none is specified.
