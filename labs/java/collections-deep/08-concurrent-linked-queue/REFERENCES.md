# References: ConcurrentLinkedQueue

- OpenJDK source:
  `src/java.base/share/classes/java/util/concurrent/ConcurrentLinkedQueue.java`
  — offer/poll CAS paths, slack updates, self-link reclaim.
- Michael & Scott, "Simple, Fast, and Practical Non-Blocking and Blocking
  Concurrent Queue Algorithms", *PODC 1996* — the algorithm, lagging
  pointers, correctness argument.
- Goetz et al., *Java Concurrency in Practice* (2006), Ch. 5 — concurrent
  collections, weakly consistent iterators, size() caveats.
- Lea, *Concurrent Programming in Java* (2nd ed.) + JSR 166 (Java 5, 2004)
  — the package CLQ shipped in.
- Herlihy & Shavit, *The Art of Multiprocessor Programming* (2nd ed.),
  Ch. 10 "Linked Lists: The Role of Locking" / lock-free structures —
  linearization points, lock-free vs wait-free progress.
- OpenJDK siblings: `LinkedBlockingQueue.java`, `SynchronousQueue.java`,
  `ArrayBlockingQueue.java` — when blocking/bounds replace lock-freedom.
## Javadoc and source entry points

- `java.util.concurrent.ConcurrentLinkedQueue` — offer/poll/peek contracts,
  weakly-consistent iterator clause, size() NOT-constant-time warning.
- `java.util.concurrent.LinkedBlockingQueue` / `SynchronousQueue` /
  `ArrayBlockingQueue` — the blocking/bounded alternatives and when each
  replaces CLQ.
- `java.lang.invoke.VarHandle` (`compareAndSet`, weak ordered writes) —
  the CAS spelling the queue is built on since JDK 9.

## Further reading

- Michael & Scott, PODC 1996 — the paper: lagging pointers, correctness
  argument, blocking companion algorithm.
- Herlihy & Shavit, Ch. 10 — linearization, lock-freedom vs wait-freedom,
  ABA across structures.
- *Java Concurrency in Practice*, Ch. 5 — using concurrent queues, size
  caveats, producer/consumer patterns.
