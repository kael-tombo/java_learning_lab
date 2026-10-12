# References: Volatile Semantics

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
- JLS 17.4.5 (volatile write->read edge); JSR-133 change list for DCL correctness condition.
- `VarHandle` access-mode table (volatile vs acquire/release vs opaque) and array-element access.

## How to cite
- Prefer JLS section + javadoc + source path over any blog. Every claim in THEORY.md traces to one line above.

## Annotated: what to open first for visibility questions
- JLS 17.4.5 (volatile write -> read edge): the single arrow every publication argument cites — read the section, not summaries of it.
- JLS 17.4 (happens-before rules + transitivity): program order, monitor, lifecycle edges and their composition — the full chain vocabulary in one section.
- JLS 17.5 (final-field safety): why immutable payloads publish without volatile — the exception that simplifies config/state design.
- JLS 17.7 (word tearing): the permission that makes plain long/double reads unportable — one paragraph that ends all "works on my CPU" debates.
- Bill Pugh's JSR-133 FAQ: the DCL failure execution and the volatile fix narrated by the model’s co-author — the historical proof in plain words.
- Goetz et al., JCIP ch. 3 (sharing objects) and ch. 16 (memory model): safe-publication catalog, piggybacking, and the volatile-array trap as working rules.

## VarHandle and atomics entry points
- `VarHandle` access-mode table (plain vs opaque vs acquire/release vs volatile): the unbundled cost ladder beneath the `volatile` keyword — descend only profiler-driven.
- `VarHandle` array-element access (`getVolatile`/`setVolatile` over arrays): the per-element answer to the volatile-reference trap.
- `AtomicIntegerArray` javadoc: per-element volatile semantics via intrinsics — the shipped alternative to hand-rolled element fences.
- JSR-166 (Doug Lea, 2004): the per-action edge catalog (submit -> execute, countDown -> await) — transitivity applied to executors and synchronizers.

## Hardware notes (qualitative sources)
- x86 TSO descriptions (Intel SDM ordering chapter): loads-with-loads / stores-with-stores ordering that makes volatile reads nearly free — cite for cost intuition, never for correctness.
- ARMv8 barrier documentation (`dmb ish` semantics): why both volatile directions need explicit fences off x86 — the portability warning in vendor words.
