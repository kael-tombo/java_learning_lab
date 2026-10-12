# References: Thread Lifecycle

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
- `Thread.State` javadoc (six values, monitoring-only clause), `start/join/sleep/setDaemon/interrupt` javadoc.
- `LockSupport.park/parkNanos` javadoc (silent interrupt return, preserved status).

## How to cite
- Prefer JLS section + javadoc + source path over any blog. Every claim in THEORY.md traces to one line above.

## Annotated: what to open first for lifecycle questions
- `Thread.State` javadoc: the six values plus the monitoring-only clause — the two facts every dump reading depends on; read before any dump.
- `Thread.start/join/sleep` javadoc: single-use start, join's publication edge, sleep's interrupt contract — behavior triples in one place.
- `LockSupport` javadoc (park/unpark): silent interrupt return plus preserved status — the paragraph that explains every "park ignored my interrupt" report.
- JLS 17.4 (lifecycle edges): `start()` happens-before thread actions, thread actions happen-before `join()` return — why post-join reads are safe without volatile.
- Goetz et al., JCIP ch. 7 (task cancellation): interrupt policies per mechanism — pairs with this lab's interrupt matrix when designing shutdown.
- JEP 444 (virtual threads): same-state reporting plus unmount-on-park and the `synchronized`-pinning limitation — the whole virtual-thread dump story in one JEP.

## Javadoc entry points (exact methods)
- `Thread.getState/isAlive/interrupt/interrupted/setDaemon`, `Object.wait/notify/notifyAll`, `LockSupport.park/parkNanos/unpark`, `Thread.join/sleep` overloads.
- Read overloads separately: timed vs untimed variants choose TIMED_WAITING vs WAITING — the timeout parameter is the state parameter.

## Dumping and event tools
- `jstack -l <pid>`: adds lock-owner lines (`- locked <0x...>`) that turn BLOCKED clusters into holder hunts.
- `jcmd <pid> Thread.print`: the scriptable equivalent; the `-l` flag mirrors `jstack -l` for owner info.
- JFR `jdk.JavaMonitorEnter` / `jdk.JavaMonitorWait`: timestamped contention events for rates, not just snapshots.
- JFR `jdk.VirtualThreadPinned` (21+): counts `synchronized`-pinning episodes per stack — the pinning fix-list generator.
