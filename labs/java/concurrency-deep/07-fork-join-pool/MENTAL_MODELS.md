# Mental Models: Fork-Join

## 1. Potluck tables, not a buffet line

Each worker has its own table (deque) piled with dishes (tasks). It eats from
the top of its own pile (LIFO — freshest first). Idle guests steal whole
platters from the *bottom* of someone else's pile (FIFO — biggest portion per
trip). No central server, no line — the party balances itself.

## 2. `join()` as helping, not waiting

`Thread.join()` is sitting by the phone. FJ `join()` is waiting at a barn
raising: while your beam isn't ready, you hammer someone else's. By the time
your beam arrives, the barn is closer to done because of you. Code that
"waits" in FJ still works — that is the design, not luck.

## 3. Threshold as bite size

Too small (grains of rice): you spend longer reaching for food than eating —
task-object + queue-op overhead. Too large (whole watermelons): three guests
eat, five watch — idle cores. Bite size (1–10µs leaves, hundreds per worker)
keeps every mouth fed with minimal reaching.

## 4. The common pool as a shared elevator

Parallel streams, CF defaults, and your `RecursiveTask` all ride one elevator
sized CPUs − 1. One passenger holding the door (blocking I/O) slows every
rider — and the elevator never goes out of service (no shutdown). Freight
(blocking work) takes the service elevator (own pool).

## 5. `ManagedBlocker` as calling in a substitute

A worker that must nap (block) phones the office (`managedBlocker`); the
office sends a substitute so headcount holds (pool size > parallelism). Napping
without calling in reads as "on duty" — the crew is short and nobody knows.

## 6. asyncMode as kitchen order

LIFO kitchens fire the newest ticket first (fresh work hottest — recursive
splits). FIFO kitchens fire the oldest first (fair wait — independent events).
The common pool is a LIFO kitchen; `newWorkStealingPool` runs FIFO. Pick by
menu (workload shape), not by review stars.

## 7. Compensation size as receipt

`getPoolSize() > getParallelism()` is the receipt for a substitute: 2→3 with
one blocker means exactly one spare on duty. No receipt (size == parallelism
with blocked workers) means someone napped without calling in.
