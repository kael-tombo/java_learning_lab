# Internals: DCL Pattern

## What `volatile` compiles to here

The `instance` field's volatile read on the fast path emits an acquire
(load-load plus load-store ordering; on x86 a plain MOV with
compiler-level fencing, on ARM an acquire load). The volatile write
inside the lock emits release ordering. The HotSpot C2 compiler treats
these as memory barriers constraining reorderings that the pre-2004
model allowed across the allocate/init/publish sequence.

## Why the reorder was legal before JSR-133

`helper = new Helper()` lowers to allocation, field stores, and a
reference store. Under the old model, the reference store could become
visible before the field stores (write-write reorder) with no rule
against a reader observing the reference first. Post-JSR-133, the
release/acquire pair plus the monitor edges forbid exactly this
publication-ahead-of-construction shape — when the keyword is present.

## The monitor's two jobs

The `synchronized` block orders mutually (only one initializer runs the
recheck-to-write sequence at a time) and visibly (monitor exit hb later
monitor entry, so the recheck observes prior writes). DCL leans on both:
exclusion makes double-init avoidable; visibility makes the recheck
decisive. A recheck outside the lock would have neither.

## The local variable and the fence count

Reading `instance` once into `h` issues one acquire per call. Reading
it in both checks issues two — measurable at millions of calls per
second and semantically looser (check-then-act across two distinct
reads). C2 will not merge the two volatile reads for you (each is an
ordering point); the source shape is the optimization.

## Holder and enum at the JVM level

The holder's work happens in class initialization (`InstanceKlass`
init lock, JLS 12.4.2): recursive, single-threaded per class loader,
with failure semantics (failed init propagates `ExceptionInInitializer
Error`). Enum singletons add JVM-level constructor guards (reflective
`newInstance` throws) and serialization substitution (identity on
`readObject`). Both push correctness into mechanisms no user code can
mis-order.

## OpenJDK paths for the curious

- `src/hotspot/share/opto/memnode.cpp`, `library_call.cpp`: volatile
  and Unsafe fence emission.
- `src/hotspot/share/oops/instanceKlass.cpp`: class-init locking behind
  the holder idiom.
- `src/java.base/share/classes/java/lang/Enum.java` plus
  serialization code: enum identity guarantees.
