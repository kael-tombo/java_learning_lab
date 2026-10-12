# History: Fork-Join Pool

## Cilk and work-stealing (1994–1999)

MIT's Cilk (Blumofe, Joerg, Kuszmaul, Leiserson and colleagues) introduced
work-stealing schedulers for multithreaded divide-and-conquer. Blumofe–
Leiserson (1999) proved the expected-time bound O(T₁/P + T∞) for randomized
stealing — the theoretical license for every later implementation, including
this pool's owner-LIFO/thief-FIFO deque discipline.

## JSR-166 extra and Java 7 (2011)

Doug Lea implemented `ForkJoinPool` alongside the Java 7 fork/join framework
(`ForkJoinTask`, `RecursiveTask`, `RecursiveAction`). Java 7 gave the verbs
(`fork`/`join`/`invoke`), join-helping (waiters execute instead of parking),
and `ManagedBlocker` compensation for blocking tasks.

## The common pool (Java 8, 2014)

Java 8 made one shared instance the default engine for parallel streams and
`CompletableFuture` `*Async` stages: parallelism CPUs − 1, `asyncMode=false`,
configurable via `java.util.concurrent.ForkJoinPool.common.*` properties,
never shutting down. Sharing one pool fused three features' performance fate
— the "blocking stream stalls CF" incidents date from here.

## Refinement (Java 8–18)

`CountedCompleter` covered non-tree (DAG) fan-ins; `awaitQuiescence` served
fork-only event shapes; `commonPool` factory/handler properties matured.
`Executors.newWorkStealingPool()` offered `asyncMode=true` pools for
independent-task workloads.

## Lifecycle modernization (Java 19, 2023)

`ExecutorService` gained `close()` (JEP 453 neighborhood, virtual-threads
era): `ForkJoinPool` became try-with-resources-compatible
(`close()` = shutdown + await). Scoped pools finally had a one-line
discipline — leak reports for ad-hoc FJ pools dropped accordingly.

## What endures

The deque asymmetry and join-helping are unchanged since Java 7; the common-
pool sizing (CPUs − 1, cap 32767) is stable across versions. Threshold sizing
(`2n/t` arithmetic) outlives every API addition — new features change entry
points, never the granularity math.
