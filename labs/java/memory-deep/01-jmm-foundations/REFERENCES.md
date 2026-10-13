# References: JMM Foundations

## Normative sources (read these first)

- JLS 17.4 (Memory Model): happens-before rules (17.4.5), sequential
  consistency for correctly synchronized programs (17.4.3-17.4.5),
  causality requirements (17.4.8). The definitions every demo encodes.
- JLS 17.5 (final fields): freeze semantics — preview of lab 04; read
  the freeze rule now so the latch/lock edges below are not confused
  with constructor safety.
- JSR-133 (Java Community Process): the 2004 specification rewrite by
  Jeremy Manson and Bill Pugh with the concurrency group (Doug Lea and
  others). "The Java Memory Model" paper (Manson, Pugh, Adve; POPL
  2005) is the archival version.
- JVMS 8.14 / JLS 17.4.4 (synchronization actions): which operations
  count as synchronization (locks, volatiles, thread actions) — the
  closed set optimizations must respect.

## Books and guides

- Brian Goetz et al., *Java Concurrency in Practice* (2006): chapters
  3 (visibility) and 16 (the JMM) — the practitioner companion to
  JSR-133; the latch/lock/start guidance here follows its ordering.
- Doug Lea, *JSR-133 Cookbook for Compiler Writers*: how hb edges lower
  to barriers per platform — the bridge from this lab to lab 03.
- Jeremy Manson, "Semantics of Multithreaded Java" (PhD
  dissertation, Maryland, 2004): causality formalization behind 17.4.8.

## OpenJDK sources (JDK 9+ layout, stable paths)

- `src/java.base/share/classes/java/lang/Thread.java`: start/join plus
  interruption and aliveness methods carrying hb edges.
- `src/java.base/share/classes/java/util/concurrent/CountDownLatch.java`:
  the documented countDown/await edge used in `LatchEdge`.
- `src/java.base/share/classes/java/util/concurrent/FutureTask.java` and
  `.../locks/AbstractQueuedSynchronizer.java`: further library edges
  (task completion, lock handoff) on the same volatile/CAS skeleton.
- `src/java.base/share/classes/java/lang/invoke/VarHandle.java`: access
  modes (plain/opaque/acquire/release/volatile) formalizing edge
  strength — full treatment in lab 03.

## Testing and tooling

- OpenJDK jcstress (`github.com/openjdk/jcstress`): litmus-test
  harness; the correct way to turn any exercise-1/2 breakage into a
  histogram instead of an anecdote.
- Aleksey Shipilev, "Close Encounters of The Java Memory Model Kind":
  the canonical talk on JMM testing practice with jcstress.
