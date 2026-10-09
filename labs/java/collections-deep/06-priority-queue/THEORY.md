# PriorityQueue Deep Dive — Theoretical Foundation

## Core Concept

`java.util.PriorityQueue<E>` is a **binary min-heap** stored in a plain
`Object[] queue` — no node objects, no pointers. The parent of index k is
`(k - 1) >>> 1`, children are `2k+1` and `2k+2`. The array *is* the tree:
element 0 is always the minimum (under natural ordering or the supplied
comparator).

It implements `Queue`, not `Deque`: **no peek-last, no iteration in sorted
order, no push/pop at both ends**. Those belong to `PriorityBlockingQueue`'s
cousin operations or `TreeMap.firstKey`.

## The Two Sift Operations

Insertion (`offer`/`add`) calls `siftUp`:

```java
while (k > 0) {
    int parent = (k - 1) >>> 1;
    if (key.compareTo((T) es[parent]) >= 0) break;   // heap property restored
    es[k] = es[parent];                              // pull parent down
    k = parent;
}
es[k] = key;
```

Removal (`poll`) replaces the root with the **last** element, sets
`size--`, then `siftDown` from index 0: take the smaller child, pull it up,
continue. Both are O(log n) with no allocation — the element moves *within* the
array, never out of it.

`heapify()` (used when building from a collection) starts at
`(n >>> 1) - 1` and walks down to 0 — the last non-leaf node. Building n
elements this way is **O(n)**, not O(n log n): the sum of subtree heights
Σ n/2^(h+1) · h converges to 2n. This is the standard Floyd build-heap result.

## Growth: +2 Below 64, Then 50%

```java
int newCapacity = ArraysSupport.newLength(oldCapacity,
        minCapacity - oldCapacity,
        oldCapacity < 64 ? oldCapacity + 2 : oldCapacity >> 1);
```

A fresh `PriorityQueue()` **eagerly allocates `Object[11]`** —
`DEFAULT_INITIAL_CAPACITY = 11`, and the constructor rejects
`initialCapacity < 1` with `IllegalArgumentException` (kept "for 1.5
compatibility", per the source comment). Small arrays grow by `oldCapacity + 2`
(about doubling: 11 → 24 → 50), then switch to the same 1.5× factor ArrayList
uses once capacity reaches 64. The `< 64` special case avoids over-allocating
for tiny heaps.

## Operation Costs

| Operation | Cost | Notes |
|-----------|------|-------|
| offer / add | O(log n) | siftUp |
| poll | O(log n) | siftDown from root |
| peek | O(1) | `queue[0]` |
| contains(Object) | O(n) | linear scan of the array |
| remove(Object) | O(n) find + O(log n) sift | indexOf + shrink-replace |
| iterator | O(n) | **unordered** — internal heap order, not sorted |
| toArray / addAll(collection) | O(n) | addAll does heapify, O(n) |

The trap row is **iteration**: users expect sorted output and get heap order
(e.g. `[1, 3, 2, 7, 4, 5]` for a 7-element queue). Sorted output requires
draining via repeated `poll()` — O(n log n) total — or copying and sorting.

## PriorityQueue Is Not Thread-Safe

`PriorityQueue` is unsynchronized; its documented sibling,
`PriorityBlockingQueue`, adds a `ReentrantLock` around every operation —
same heap, O(log n) still, but contention serializes writers while `peek`
takes the lock briefly (it must: a concurrent `poll` could empty the array
underneath).

Fail-fast iterators apply (modCount checks) — `ConcurrentModificationException`
on structural change during iteration, best-effort like the rest of
java.util.

## Null and Ordering Rules

- **Null is banned**: `offer(null)` throws NPE immediately — comparing null
  against the root is meaningless under both natural and custom ordering.
  (Contrast: LinkedList/ArrayList accept null; HashMap accepts one null key.)
- Natural ordering requires `Comparable` — failure appears at first insertion
  (`ClassCastException` inside `compareTo`), not at construction.
- A supplied `Comparator` decides everything; `null` elements remain banned
  even if the comparator could handle them — the check is unconditional.
- **No equality-based semantics**: `remove(Object)`/`contains` use `equals`,
  but *duplicates by equals are all retained* — the queue keeps as many copies
  as you offer, since heap ordering only cares about compareTo position.
  `remove(one)` removes the first array-slot match, which may not be the
  "first" logically.

## Why poll() Is O(log n) and Not O(n)

Removing the root would naively require shifting the whole array (as an
ArrayList would). The heap trick: move the *last* element to the root (O(1)),
then sift it down — at most log₂ n swaps, each comparing two array slots
that are cache-adjacent (children of k are 2k+1, 2k+2 — same or next cache
line for small k). This locality is why PriorityQueue beats a sorted-array
approach for mixed insert/remove workloads.

## Selection Sort vs Heap: The HeapSelect Note

Two `poll()` calls do **not** give the second-smallest element in O(1) — they
destructively rebuild the heap each time. For "top k" queries, `stream.sorted()
.limit(k)` (which uses a bounded priority queue internally) is the idiom;
for repeated single-min queries, keep the queue alive.

## Key Invariants

1. For every index k > 0: `queue[(k-1)>>>1]` compares ≤ `queue[k]` (min-heap
   property) after every completed public operation.
2. `0 ≤ size ≤ queue.length`; slots `[size, length)` hold stale references —
   `poll` and `remove` null them out to avoid leaking.
3. `queue[0]` is the minimum iff `size > 0` — `element()` throws
   `NoSuchElementException` on empty rather than returning null.
4. `modCount` increments on every `offer` (verified: unconditional, right after
   the null check), on `poll` of a non-empty queue, and on `clear`/`removeAt` —
   so any structural change is visible to an outstanding iterator.
