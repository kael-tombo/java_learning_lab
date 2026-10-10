# Common Mistakes: ConcurrentLinkedQueue

## 1. Offering null

`offer(null)` throws NPE — null marks dequeued nodes. Audit producers for
nullable values; map "absent" to a sentinel object, not null.

## 2. Branching on size()/isEmpty() in hot paths

`if (!q.isEmpty()) q.poll()` races: another thread polls first, you get
null anyway. `size() == 0` is equally non-binding. Poll and null-check the
result — the single-atomic way.

## 3. Expecting blocking take()

`poll()` returns null on empty; there is no `take()`. Busy-spinning on
poll burns cores. Need waiting? `LinkedBlockingQueue.take()` with
conditions is the structure, not a spin loop.

## 4. Assuming iteration reflects a moment

Weakly consistent iterators may show some concurrent inserts and miss
others — never a snapshot. Snapshot needs (drain to list, external lock,
or a COW structure).

## 5. Treating poll order as globally timestamped

FIFO holds at linearization points, not at call-site wall time: offer A
started-before B can linearize after B. "Started first ⇒ dequeued first"
is false under concurrency.

## 6. Using remove(Object) as a fast cancel

`remove` is an O(n) CAS-per-node walk — fine occasionally, a throughput
killer as a cancellation mechanism per task. Prefer per-task state flags
checked at poll.

## 7. Forgetting nodes cost memory per element

Each offer allocates a Node; allocation rate bounds producer throughput
and pressures young-gen GC. For primitive-heavy fan-in, batch or use
array-backed queues.
