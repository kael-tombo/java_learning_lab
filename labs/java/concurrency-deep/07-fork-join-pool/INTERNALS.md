# Fork-Join Internals

## Deque discipline

Each worker deque supports three ops: owner push (tail), owner pop (tail,
LIFO), thief steal (head, FIFO). Push/pop share one end so the owner never
contends with itself; steals take the far end so thief and owner rarely
collide. A steal that finds the deque down to one element races the owner pop
— resolved by CAS, loser retries elsewhere.

## Join-helping (`join` shape)

```text
join(task):
  if task done -> return result
  if current thread is FJ worker:
    while task incomplete:
      pop own deque (LIFO) -> execute it   // HELP first
      try steal from random victim -> execute
      if nothing found -> park (await task signal)
  else (outsider): park until task signals
```

Helping is why fork-then-immediately-join works: the waiter drains its own
children instead of idling. `Thread.join()` has no such step — the names are
false friends.

## Task lifecycle states

ForkJoinTask moves NEW → (forked: queued in a deque) → SIGNAL/completing →
NORMAL (value) / EXCEPTIONAL (throwable) / CANCELLED. `join()` rethrows the
recorded throwable; `invoke()` = `fork()` + `join()` with the same rethrow.

## Submission paths

- Worker `fork()`: push to own deque (cheapest path, no contention).
- Outsider `fork()`/`execute()`: shared submission queue, workers drain it
  when local deques and steals come up empty.
- `invoke()` from outside: submit + join with helping disabled for the outer
  wait (the caller is not a worker) — it parks while workers drain.

## Compensation (`ManagedBlocker` internals)

`managedBlocker(b)`: if `b.isReleasable()` return immediately; else register
the block, optionally add a spare thread (pool size grows past parallelism),
run `b.block()`, deregister. The spare preserves throughput while the worker
parks — `getPoolSize() > getParallelism()` afterwards is the expected
footprint, not a leak.

## Quiescence vs termination

`awaitQuiescence(t)`: returns when no worker has active tasks (forks without
joins may still exist as queued work — quiescent means idle, not empty of
futures). `awaitTermination(t)`: returns when the pool actually shut down
after `shutdown()`. Quiescence is for fork-only event shapes; termination is
for lifecycle management.

## Common-pool construction (source-verified)

Parallelism from the `common.parallelism` property defaulting to CPUs − 1;
`asyncMode=false`; never terminates (`shutdown` on the common pool is
ignored-ish by design). Size it at JVM startup — no API call reverts it.
