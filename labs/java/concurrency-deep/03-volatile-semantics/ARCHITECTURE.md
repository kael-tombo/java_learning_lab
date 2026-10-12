# Architecture: Volatile Semantics

## Components (real ones, not generic boxes)
1. **Program layer** — your code calling `volatile` field read/write, double-checked locking with volatile, `AtomicIntegerArray`/VarHandle array-element volatile access, `VarHandle.getAcquire/setRelease/getOpaque` (contrast).
2. **JDK layer** — volatile field access (JLS 17.4.5), program-order/monitor/lifecycle edges, StoreLoad fences (`xchg`+`lock` on x86, `dmb ish` on ARMv8), safe-publication piggybacking, `VarHandle` access modes.
3. **JVM/HotSpot layer** — scheduler, park/unpark primitives, monitor subsystem; sources in JLS 17.4 (happens-before), 17.5 (final-field safety), 17.7 (word tearing), JSR-133 (2004 memory-model rewrite), `VarHandle.java` (Java 9).
4. **OS/hardware layer** — kernel threads, futexes/condition variables, cache coherence and fences.

## Structure
```
+------------------- program -------------------+
|  the Java Memory Model happens-before edges for volatile fields: visibility, ordering, and limits                      |
+--------------- JDK (Volatile Semantics) ----------------+
|  volatile field access (JLS 17.4.5), program-order/monitor/lifecycle edges, StoreLoad fences (`xchg`+`lock` on x86, `dmb ish` on ARMv8), safe-publication piggybacking, `VarHandle` access modes   |
+----------- HotSpot / OS / hardware -----------+
|  threads, monitors, fences, schedulers        |
+-----------------------------------------------+
```

## Data flow
1. Application invokes one of: `volatile` field read/write, double-checked locking with volatile, `AtomicIntegerArray`/VarHandle array-element volatile access, `VarHandle.getAcquire/setRelease/getOpaque` (contrast).
2. JDK maps the call onto volatile field access (JLS 17.4.5), program-order/monitor/lifecycle edges, StoreLoad fences (`xchg`+`lock` on x86, `dmb ish` on ARMv8), safe-publication piggybacking, `VarHandle` access modes.
3. HotSpot/OS executes the primitive (thread state change, monitor op, fence, or CAS).
4. Observable effect returns: state token, mutual exclusion, visibility edge, or updated value.

## Key invariant
- Volatile gives visibility + access atomicity (incl. long/double) but NOT compound-action atomicity (volatile++ races: read-modify-write in three steps); DCL is correct only with volatile (or holder idiom/enum singleton); transitivity A->B->C chains edges; volatile reads are near-free on x86 (TSO) while writes need a fence, both directions need fences on ARM (qualitative only); volatile arrays cover the reference, never the elements.

## Failure modes at this layer
1. Misidentifying which component owns the state (e.g. wrong monitor object, wrong field, wrong atomic).
2. Assuming ordering that no edge provides (see MATH_FOUNDATION.md for the exact edges).
3. Confusing a monitoring signal (thread state, fuzzy sum) with a synchronization guarantee.

## Cross-references
- Mechanism: HOW_IT_WORKS.md. Sources: INTERNALS.md. Costs: PERFORMANCE.md.
