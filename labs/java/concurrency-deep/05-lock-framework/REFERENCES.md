# References: Lock Framework

## Books

- Brian Goetz et al., *Java Concurrency in Practice* (2006) — chapters 13–14:
  explicit locks, conditions, and AQS-based synchronizer design.
- Doug Lea, *Concurrent Programming in Java*, 2nd ed. (1999) — the pre-JSR-166
  design reasoning behind queued synchronizers.
- Scott Oaks, *Java Performance*, 2nd ed. — lock contention measurement with
  JMH and profilers.

## Papers

- Craig, Landin, Hagersten — CLH queue lock lineage behind AQS's
  predecessor-watching queue (spin → park adaptation by Lea).
- Mellor-Crummey & Scott (1991), "Algorithms for Scalable Synchronization on
  Shared-Memory Multiprocessors" — the queue-lock background AQS builds on.

## OpenJDK sources (authoritative for this lab)

- `java.base/java/util/concurrent/locks/AbstractQueuedSynchronizer.java`
  (JDK 23: `WAITING`/`COND`/`CANCELLED` + bitwise ops)
- `java.base/java/util/concurrent/locks/ReentrantLock.java`
  (`NonfairSync` barging CAS vs `FairSync` `hasQueuedThreads` check)
- `java.base/java/util/concurrent/locks/ReentrantReadWriteLock.java`
  (16/16-bit packing, `MAX_COUNT = 65535`)
- `java.base/java/util/concurrent/Semaphore.java`
- `java.base/java/util/concurrent/CountDownLatch.java`
- `java.base/java/util/concurrent/ArrayBlockingQueue.java`
  (canonical two-condition `notEmpty`/`notFull` client)

## Documentation

- `java.util.concurrent.locks` package javadoc — fairness, reentrancy, and
  condition semantics as specified (not just implemented).
- `Lock`, `Condition`, `ReadWriteLock` interface javadoc — the contracts every
  implementation must honor.
