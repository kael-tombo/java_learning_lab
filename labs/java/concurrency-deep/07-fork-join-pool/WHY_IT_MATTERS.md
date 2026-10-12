# Why Fork-Join Matters

## Everyday code that depends on it

- Parallel streams (`collection.parallelStream()...`) — every bulk operation
  runs on the common pool.
- `CompletableFuture` `*Async` defaults — same pool, shared fate.
- `Arrays.parallelSort` / `parallelPrefix` / `parallelSetAll` — FJ-backed
  primitives.
- Hand-rolled `RecursiveTask` aggregations (sums, searches, tree walks) in
  data pipelines.

## The bug classes it removes

- Recursive-task deadlock: `join()`-helps means fork-then-join chains progress
  where a parking join would wedge.
- Dispatcher bottleneck: per-worker deques scale where a single shared queue
  contends.
- Unbalanced-tree idling: thieves drain busy deques, so skewed recursion still
  feeds all cores.

## The bug classes it introduces

- Common-pool squatting: a blocking FJ task (or parallel stream over I/O)
  silently shrinks every borrower's parallelism — one team's `read()` stalls
  another's pipeline.
- Threshold mis-sizing: millions of nano-tasks (churn) or dozens of giant
  tasks (idle cores) — both look like "FJ is slow."
- Leaked pools: non-daemon FJ workers hold the JVM open exactly like leaked
  thread pools.
- `ManagedBlocker` omission: parked-without-notice workers reduce effective
  parallelism with no error, only slower throughput.

## Interview-grade one-liners

- "Owner LIFO, thief FIFO — per worker deque."
- "`join()` helps before it parks."
- "Common parallelism is CPUs − 1; plain constructor is CPUs; cap 32767."
- "Blocking in tasks needs `ManagedBlocker` (compensation grows pool size
  past parallelism)."
- "Scoped pools close with try-with-resources since Java 19."
