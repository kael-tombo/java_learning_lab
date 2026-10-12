# References: Fork-Join Pool

## Books

- Brian Goetz et al., *Java Concurrency in Practice* (2006) — task-execution
  frameworks (ch. 6–8); pre-FJ background for why work-stealing was needed.
- Doug Lea, *Concurrent Programming in Java*, 2nd ed. (1999) — fork/join
  design roots from the JSR-166 author.
- Maurice Herlihy & Nir Shavit, *The Art of Multiprocessor Programming*
  (2nd ed.) — work-stealing analysis and deque design.

## Papers

- Robert Blumofe & Charles Leiserson, "Scheduling Multithreaded Computations
  by Work Stealing" (JACM 1999) — the O(T₁/P + T∞) bound behind FJ scheduling.
- Doug Lea, "A Java Fork/Join Framework" (CPP 2000) — the design paper for
  the framework that became `java.util.concurrent.ForkJoinPool`.
- MIT Cilk project papers (1994–1998, Blumofe et al.) — the work-stealing
  lineage (Cilk → FJ).

## OpenJDK sources (authoritative for this lab)

- `java.base/java/util/concurrent/ForkJoinPool.java` — deques, stealing,
  common-pool sizing (`common.parallelism`, `MAX_CAP = 0x7fff`),
  `ManagedBlocker` compensation, `awaitQuiescence`.
- `java.base/java/util/concurrent/ForkJoinTask.java` — states, `fork`/`join`/
  `invoke`, exception recording.
- `java.base/java/util/concurrent/RecursiveTask.java` /
  `RecursiveAction.java` / `CountedCompleter.java`.
- `java.base/java/util/concurrent/CompletableFuture.java` — the main common-
  pool borrower (default `*Async` executor).

## Documentation

- `ForkJoinPool` class javadoc — parallelism, factory, handler, `asyncMode`,
  `managedBlock`, quiescence semantics.
- `ForkJoinTask` javadoc — fork/join/invoke contracts and exception behavior.
- `ExecutorService.close()` (Java 19+) javadoc — try-with-resources lifecycle.
