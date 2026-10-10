# Debugging: ConcurrentLinkedQueue

## Lost or duplicated elements

First suspect: wrapping poll in `isEmpty()` checks or catching the result
poorly — duplicates cannot come from `casItem` (exactly one winner per
node). Reproduce single-threaded: drain and count; then add threads. If
single-threaded counts mismatch, the bug is caller-side bookkeeping, not
the queue.

## Unexpected null from poll on a "non-empty" queue

`isEmpty()` said false, `poll()` returned null — a racing consumer won.
Log linearization order, not call order: the queue was empty *at your
poll's linearization instant*. Fix the protocol (null-tolerant drain
loops), not the queue.

## Consumer spins at 100% CPU

Poll-in-a-tight-loop on empty. Replace with `LinkedBlockingQueue.take()`,
or park with `LockSupport.parkNanos` + backoff between drain attempts.
Profile to confirm: hot frame will be your spin, not `poll` internals.

## size() disagrees with reality

Expected — it walks a moving chain. Never assert exact size across
threads; assert quiescent size (all producers joined, then count) or track
membership with separate atomic counters incremented at linearization.

## Apparent memory leak (chain won't shrink)

Dummies await head-swing + GC; a straggler thread pinning an old node
keeps its *successors* reachable until it moves (self-links bound this:
only the suffix from the straggler's node stays). Thread dumps showing a
parked walker inside poll/iterator explain retention — nudge or join it.

## Verifying FIFO in tests

Single producer + single consumer, offer 1..N then drain: must be exact
order. Multi-producer tests assert *set* equality + per-producer order
preservation, never global wall-clock order.
