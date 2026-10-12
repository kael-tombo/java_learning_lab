# Why Fork-Join Exists

## The fixed-pool ceiling

`ThreadPoolExecutor` with a shared queue works for independent tasks but not
for *recursive* ones: a worker that forks 100 subtasks then `join()`s them
parks while its own children wait in a global queue behind unrelated work.
Central dispatch becomes the bottleneck; naive fork-then-join deadlocks or
idles cores on unbalanced recursion.

## The work-stealing answer (Java 7)

`ForkJoinPool` (Doug Lea, JSR-166 follow-through, Java 7) gives each worker
its own deque: push/pop locally (LIFO — hot subtasks first), steal remotely
(FIFO — coarse chunks, few steals). No central dispatcher; unbalanced trees
still saturate cores. `join()` helps — a waiting worker executes instead of
parking — so the natural recursive shape makes progress by construction.

## What each verb solves

- `fork()`: queue a subtask without blocking (own deque if worker, shared
  submission queue if outsider).
- `join()`: await a result while helping — the deadlock-avoidance mechanism.
- `invoke()`: fork + join from outside the pool (the entry point).
- `ManagedBlocker`: the escape hatch when a task must block (I/O, latches) —
  the pool compensates so parallelism survives.
- `awaitQuiescence`: FJ-specific drain ("no active tasks") for fork-only,
  never-joined workloads.

## What it deliberately does not do

- Not for blocking-heavy work: threads-per-task (or virtual threads) beat
  stealing when tasks mostly wait — FJ assumes CPU-bound divisibility.
- Not for tiny work: task objects + queue ops dwarf sub-microsecond leaves —
  a plain loop wins.
- No ordering: steals reorder execution freely; pipelines needing sequence
  must enforce it explicitly.
