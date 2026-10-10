# Why Lock-Free Queues Matter

## Where CLQ shows up

- **Executor internals**: `ThreadPoolExecutor` with a CLQ-backed handoff
  (e.g. `newCachedThreadPool` uses `SynchronousQueue`; many custom pools
  use CLQ) — task submission never blocks the submitter.
- **Event pipelines / logging**: producer threads enqueue log events or
  metrics; a drainer batch-polls. No producer ever waits on the consumer.
- **Work stealing**: ForkJoin-style schedulers park per-worker deques, but
  cross-thread spillover queues are routinely CLQ — lock-free steal/push
  keeps thieves moving.

## What goes wrong with the alternatives

`Collections.synchronizedList(new LinkedList<>())` as a queue: every
offer/poll takes one monitor; under 32 producers throughput collapses to
~1/lock-hold plus context switches, and iterators throw CME on concurrent
drain. `LinkedBlockingQueue` fixes blocking semantics but keeps two locks
— better, still serialized. CLQ removes the ceiling where blocking isn't
wanted.

## Interview signal

Expect: "what are the linearization points?", "why can tail lag behind
head?", "why is size() O(n)?", "how does poll avoid returning an element
twice?". All four answers live in this directory: two CASes, hints-not-
authority, chain-walk counting, exactly-one-CAS-winner.
## Choosing across the queue shelf

- Never-block handoff, unbounded OK → CLQ (this lab).
- Must wait for work (`take`) or bound memory → `LinkedBlockingQueue`
  (two locks, conditions) or `ArrayBlockingQueue` (one lock, fixed array).
- Direct handoff, zero capacity → `SynchronousQueue` (rendezvous).
- Ordered + concurrent + blocking → `PriorityBlockingQueue` / `DelayQueue`.

Default application code toward the blocking queues (backpressure and
waiting are usually wanted); reserve CLQ for paths where any blocking is
a correctness or tail-latency problem — and keep `size()` out of them.
