# References: Synchronized Internals

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
- JVMS monitorenter/monitorexit specification (exception-table pairing).
- JDK-8256425 (biased locking removal); `UseBiasedLocking` unrecognized-option behavior on JDK 23.

## How to cite
- Prefer JLS section + javadoc + source path over any blog. Every claim in THEORY.md traces to one line above.

## Annotated: what to open first for monitor questions
- JVMS monitorenter/monitorexit section: the pairing rule plus the exception-table mechanism — the spec behind snippet 1's `javap -c` output.
- Goetz et al., JCIP ch. 2 (thread safety) and ch. 14 (explicit locks): guard design, alien-method danger, and the synchronized-vs-Lock decision table in one place.
- Bloch, *Effective Java* Item 82 (thread safety levels) plus Item 78 (synchronization): documenting what your monitor actually protects, and where volatile/atomic suffice instead.
- Doug Lea, *Concurrent Programming in Java* (1999), monitor chapters: condition-variable discipline (while-loops, notifyAll defaults) that predates and predicts the modern idioms.
- JLS 17.1 (synchronization) then 17.4 (happens-before): ownership-checked wait/notify first, the unlock -> lock edge second — mechanism before memory.

## Version and removal records
- JEP 374 (JDK 15): biased-locking disable-by-default rationale with the measurements that motivated retirement — cite for "why bias is gone".
- JDK-8256425 (JDK 18): the removal record; JDK 23 `Unrecognized VM option 'UseBiasedLocking'` behavior is the live confirmation (CODE_DEEP_DIVE.md snippet 2).
- JEP 444 (Java 21): virtual-thread pinning by `synchronized` documented as the interaction to watch — the current pinning story in one JEP.

## HotSpot source map
- `objectMonitor.cpp` / `synchronizer.cpp`: inflation, `_cxq`/`_EntryList`/`_WaitSet` handling, deflation paths.
- `markWord.hpp`: the 64-bit header layout (hash, age, lock bits) and the state-transition comments.
- `thread.cpp` plus `jstack`/`jcmd Thread.print` output: how BLOCKED vs WAITING tokens are printed from the same states this lab forces.
