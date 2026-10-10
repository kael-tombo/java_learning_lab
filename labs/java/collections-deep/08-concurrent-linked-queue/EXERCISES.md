# Exercises: ConcurrentLinkedQueue

## 1. FIFO single-threaded proof

Offer 1..10_000, drain, assert exact order. Then interleave offers/polls
(single thread) and assert the drain matches a `LinkedList` reference
queue op-for-op.

## 2. Exactly-once under contention

4 producers × 25k unique ints, 4 consumers draining into a concurrent set.
Join all; assert set size == 100k (no loss, no dup — the `casItem`
guarantee) with `assert q.isEmpty()` quiescent.

## 3. Observe lagging tail

Via reflection (`--add-opens java.base/java.util.concurrent=ALL-UNNAMED`)
read `head`/`tail` after bursts: show tail ≠ last node, and tail
sometimes behind head after drains. Confirm offers still land correctly.

## 4. size() staleness demo

Producer offers continuously while a sampler calls `size()`; log
size-then-drain-count mismatches. Then assert quiescent size (producers
joined) is exact — the only moment size is trustworthy.

## 5. Null + weak-iterator probes

Assert `offer(null)` throws NPE. Create iterator, concurrently offer 1k
elements, drain the iterator: assert no CME and all pre-existing elements
visited (new ones may/may not appear).

## 6. Spin-vs-block benchmark

Time: (a) CLQ poll-spin drain, (b) `LinkedBlockingQueue.take()` drain for
a bursty producer (10 bursts, 10k each, 100ms gaps). Compare consumer CPU
time — spinning burns cores between bursts; blocking parks.
