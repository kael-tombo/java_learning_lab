# Phaser — References

## Normative sources

- OpenJDK source: `java.base/share/classes/java/util/concurrent/Phaser.java`
  (JDK 23) — authoritative for packed state, the arrive vs
  arriveAndAwaitAdvance return paths, registration CAS, and tiering.
- `Phaser` javadoc (JDK 7+) — the seven-verb contract, `onAdvance`
  protocol, arrival/advance return asymmetry, and termination semantics.
- Java Language Specification, Ch. 17 (Threads and Locks) — happens-before
  and volatile/parking foundations the phaser builds on.

## Books

- Brian Goetz et al., *Java Concurrency in Practice* (Addison-Wesley, 2006)
  — Ch. 5 on latches/barriers and Ch. 8 on phased task coordination; the
  baseline vocabulary Phaser extends.
- Doug Lea, *Concurrent Programming in Java* (2nd ed., Addison-Wesley,
  1999) — design background for JSR-166 synchronization components.

## Related JDK classes (contrast)

- `java.util.concurrent.CyclicBarrier` — fixed-gang reunion, barrier
  action, `BrokenBarrierException` on breakage.
- `java.util.concurrent.CountDownLatch` — one-shot countdown gate.
- `java.util.concurrent.ForkJoinPool` / `RecursiveAction` — task
  parallelism often combined with phased barriers in solvers.

## Concepts to read next

- Bulk-synchronous-parallel (BSP) model — supersteps and barrier
  synchronization as Phaser's theoretical ancestor.
- Arrival-tree / combining-tree barriers — the HPC lineage behind tiering.
- JMH barrier benchmarks — methodology for PERFORMANCE.md's per-phase
  latency measurements.

## Javadoc entry points

- `arrive()` / `arriveAndAwaitAdvance()` — the two return conventions.
- `arriveAndDeregister()` / `bulkRegister(int)` — dynamic membership.
- `onAdvance(int, int)` / `forceTermination()` — termination control.
