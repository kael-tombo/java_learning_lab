# StampedLock — References

## Normative sources

- OpenJDK source: `java.base/share/classes/java/util/concurrent/locks/StampedLock.java`
  (JDK 23) — authoritative for `tryOptimisticRead`/`validate` expressions,
  conversion branches, and both views' `newCondition()` refusal.
- `StampedLock` javadoc (JDK 8+) — the three obligations (side-effect-free
  optimism, inconsistency-intolerant calls, stamp recycling/guessability),
  non-reentrancy warning, and ~1-year recycling bound.
- Java Language Specification, Ch. 17 (Threads and Locks) — happens-before,
  volatile semantics, and why the load fence in `validate` is required.

## Books

- Brian Goetz et al., *Java Concurrency in Practice* (Addison-Wesley, 2006)
  — Ch. 13 on explicit locks and read-write lock trade-offs; the baseline
  StampedLock improves on for read-mostly state.
- Doug Lea, *Concurrent Programming in Java* (2nd ed., Addison-Wesley,
  1999) — design background for JSR-166 locks and queues.

## Related JDK classes (contrast)

- `java.util.concurrent.locks.ReentrantReadWriteLock` — reentrant,
  condition-capable predecessor; upgrade deadlocks (lab 05).
- `java.util.concurrent.locks.ReentrantLock` — owner-tracked, condition
  supporting; the fallback when reentrancy or `await`/`signal` is needed.
- `java.util.concurrent.locks.Lock` — the interface `asReadLock()` /
  `asWriteLock()` adapt stamps to.

## Concepts to read next

- Optimistic concurrency control (database literature) — validate-at-commit
  as the ancestor of sample-then-validate.
- Sequence locks (seqlocks) — kernel version-counter reads around writers.
- JMH samples for lock microbenchmarks — methodology for PERFORMANCE.md's
  crossover measurement.

## Javadoc entry points

- `tryOptimisticRead()` / `validate(long)` — sampling and checking.
- `tryConvertToWriteLock(long)` — conditional upgrade and its 0 return.
- `asReadLock()` / `asWriteLock()` — Lock interop without conditions.
