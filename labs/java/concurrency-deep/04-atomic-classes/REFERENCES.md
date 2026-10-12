# References: Atomic Classes

## Books
- Brian Goetz et al., *Java Concurrency in Practice* (2006) — safe publication, visibility vs atomicity, wait/notify idioms, atomic vs lock guidance.
- Joshua Bloch, *Effective Java* (3rd ed.) — Item 3 (enum singleton vs DCL), synchronization and lazy-initialization guidance.
- Doug Lea, *Concurrent Programming in Java* (1999) — monitor and lock-free foundations behind JSR-166.

## Specifications and FAQs
- JLS 17.4 (memory model / happens-before), 17.1 (synchronization), 17.5 (final-field safety), 17.7 (non-atomic long/double).
- JSR-133 FAQ by Bill Pugh (memory-model rationale, DCL fix). JSR-166 (Doug Lea, 2004, java.util.concurrent).
- JEP 374 (biased locking retirement, JDK 15), JEP 444 (virtual threads, Java 21), JEP 193 (VarHandle, Java 9).

## Source and docs
- OpenJDK JDK 23: `java.base/java/lang/Thread.java`, `java.base/java/lang/Object.java` (wait/notify), `java.base/java/util/concurrent/atomic/*`, `java.base/java/util/concurrent/atomic/Striped64.java` (cell javadoc), `java.base/java/lang/invoke/VarHandle.java`.
- HotSpot: `objectMonitor.cpp`, `synchronizer.cpp`, `markWord.hpp`, `thread.cpp`.
- `javap -c`, `jstack`, `jcmd Thread.print`, JFR `jdk.JavaMonitorEnter` documentation.

## Lab-specific entry points
- `AtomicInteger` JDK 23 source (`value`, `VALUE` offset, `U.getAndAddInt`); `compareAndSet/compareAndExchange/weakCompareAndSet` javadoc.
- `AtomicStampedReference/AtomicMarkableReference`, `LongAdder/LongAccumulator/DoubleAdder` javadoc; `Striped64` class javadoc (`@Contended` cells).

## How to cite
- Prefer JLS section + javadoc + source path over any blog. Every claim in THEORY.md traces to one line above.

## Annotated: what to open first for CAS questions
- `AtomicInteger` JDK 23 source (`value`, `VALUE` offset, `U.getAndAddInt`): the one-intrinsic implementation — read the method bodies, not summaries, for the lock-free claim.
- `compareAndSet` / `compareAndExchange` / `weakCompareAndSet` javadoc: boolean verdict vs witness value vs spurious-failure loops-only — the three-way contract in vendor words.
- Goetz et al., JCIP ch. 15 (atomic variables and nonblocking synchronization): CAS loops, ABA, and the atomic-vs-lock decision rule as working guidance.
- Doug Lea, *Concurrent Programming in Java* (1999), lock-free chapters: the Treiber-stack lineage behind every ABA discussion — old notation, current hazard.
- JSR-166 (Doug Lea, 2004): the `java.util.concurrent.atomic` package rationale — why volatiles-with-CAS shipped as the RMW answer.

## Striped-counter sources
- `Striped64` class javadoc: cell hashing, demand growth, `@Contended` padding — the design doc living above the code.
- `LongAdder` / `LongAccumulator` / `DoubleAdder` javadoc: `sum()` fuzz, `sumThenReset()` quiescence, identity seeds — the exactness caveats in one place each.
- `AtomicStampedReference` / `AtomicMarkableReference` javadoc: pair-CAS semantics plus stamp/mark discipline — the ABA fix API surface.
- `VarHandle` specs (`compareAndSet`, `getAndAdd`, access modes): the supported vocabulary above Unsafe mechanics — cite for memory-effect claims.

## Hardware and measurement notes
- x86 `lock cmpxchg` semantics (Intel SDM): single-instruction atomic RMW behind every uncontended number — cite for mechanism, never as a timing promise.
- ARM LL-SC semantics (reservation-based): why weak CAS may fail spuriously — the vendor paragraph behind the loops-only rule.
- JMH samples for writer sweeps (1/2/8/32): the harness shape that finds each machine's crossover — copy the shape, not anyone's knee value.
