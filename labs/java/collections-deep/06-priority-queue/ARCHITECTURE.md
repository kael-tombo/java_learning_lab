# Architecture: PriorityQueue

## Components

- `Object[] queue` — the heap itself. Index 0 is the min; slots
  `[size, queue.length)` are stale (nulled on removal to avoid leaks).
- `int size` — element count, `0 <= size <= queue.length`.
- `Comparator<? super E> comparator` — null means natural ordering.
- `int modCount` — fail-fast counter, bumped on every `offer`.

## Data flow: offer(e)

1. Null check first (unconditional NPE on null).
2. Grow if `size == queue.length` (`ArraysSupport.newLength`, +2 below 64
   else 50%).
3. Place at `queue[size]`, `siftUp(size)`: compare with
   `queue[(k-1) >>> 1]`, pull parents down until the slot fits.
4. `size++`, `modCount++`.

## Data flow: poll()

1. Empty → return null (`peek` likewise; `element()`/`remove()` throw).
2. Save `queue[0]`; move `queue[size-1]` to root, null the last slot.
3. `size--`, `siftDown(0)`: pull the smaller child up until the moved
   element fits. O(log n), in place, no allocation.

## Data flow: bulk build

`PriorityQueue(Collection)` copies elements then `heapify()` from
`(n >>> 1) - 1` down to 0 — O(n), cheaper than n offers at O(n log n).

## Boundaries

- Implements `Queue`, not `Deque`: no tail access, no indexed get.
- `contains`/`remove(Object)` are O(n) `equals` scans — ordering only
  positions elements; membership is brute force.
- Unsynchronized. For blocking/timed take, use `PriorityBlockingQueue`
  (same heap under a `ReentrantLock`).
