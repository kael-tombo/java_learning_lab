# LinkedList Deep Dive — Theoretical Foundation

## Core Concept

`java.util.LinkedList<E>` is a **doubly-linked list of nodes** with `first`/`last`
sentinel handles and a `size` counter:

```java
static class Node<E> {
    E item;
    Node<E> next;
    Node<E> prev;
}
```

Every element costs one node allocation: on 64-bit HotSpot with compressed oops a
`Node` is a 12-byte header (8-byte mark word + 4-byte compressed class pointer)
plus 3 × 4-byte references = **24 bytes**, versus a single 4- or 8-byte reference
slot in ArrayList's backing array — a ~6× per-element overhead before counting
that the nodes themselves are scattered across the heap.

## The Two-Direction Trick

`get(index)` is O(n) — but not uniformly. The JDK's `node(index)` picks the closer end:

```java
if (index < (size >> 1)) { /* walk forward from first */ }
else                      { /* walk backward from last */ }
```

So `get(size-1)` is O(1) amortized-in-position, not O(n). Worst case (middle
element) is n/2 steps. This is why LinkedList *can* beat naive arrays for
`getLast()`-heavy access patterns — but the constant factor (pointer chasing,
cache misses per node) usually still loses to ArrayList's contiguous scan.

## Operation Costs

| Operation | LinkedList | ArrayList (amortized) |
|-----------|-----------|------------------------|
| addLast / offerLast | O(1) | O(1), O(n) on grow-copy |
| addFirst | O(1) | O(n) — shifts everything |
| get(i) | O(n/2) from nearer end | O(1) |
| add(i, e) | O(n/2) to reach + O(1) splice | O(n) to shift |
| remove(i) | O(n/2) to reach + O(1) unlink | O(n) to shift |
| removeFirst | O(1) | O(n) — shifts everything |

The crossover point people cite ("use LinkedList for frequent inserts") is
misstated: **position matters more than structure**. Appending mid-list is
O(n/2) in *both* lists; prepending is where LinkedList wins.

## Structural Invariants

1. `first.prev == null` and `last.next == null`.
2. For every node: `node.next.prev == node.prev.next == node` (doubly-linked
   consistency) — the JDK carries `// assert` comments checking this in
   `unlink`, left disabled in production builds.
3. `size` equals the node count; `modCount` increments on every structural change
   (add/remove/clear), not on element replacement.
4. If `size == 0`, both `first` and `last` are null — there is **no sentinel/
   dummy node**, which is why nearly every mutation has an explicit
   `if (first == null)` branch.

## Fail-Fast Iteration

Iterators remember `modCount` at creation (`expectedModCount`) and throw
`ConcurrentModificationException` on the next `next()` call if it drifted — same
best-effort heuristic as HashMap's. `ListIterator.set/remove` update
`expectedModCount` legitimately, which is why mutation must go *through* the
iterator, not the list.

## Deque Behavior

LinkedList implements `Deque<E>`, so it is both a queue (`offer/poll` at the
head) and a stack (`push/pop` are addFirst/removeFirst). This is the *structural*
reason to prefer it over `ArrayDeque`: ArrayDeque is a circular array (faster,
cache-friendlier) but **does not permit null elements**, and neither supports
indexed access at O(1) — so the choice is:

- need `get(i)` or nulls → LinkedList
- pure queue/stack, no nulls → ArrayDeque (better constant factors)
- indexed access + performance → ArrayList

## Why "LinkedList Is Faster for Insertion" Is Usually Wrong

The textbook claim assumes you *already hold the node or iterator*. With
`add(i, e)` you must first walk to position i — O(n/2) pointer-chasing steps,
each likely a cache miss. ArrayList's shift is O(n) but in contiguous memory
with hardware prefetching. Real benchmarks (JMH, warm JVM) show ArrayList
winning for most mixed workloads; LinkedList's advantage appears mainly for
`addFirst`/`removeFirst` at scale and when iterating with `ListIterator.add`
(where position is already held).

## Key Invariants (Summary)

- Doubly-linked symmetry: every interior node satisfies `prev.next == this ==
  next.prev`.
- Head/tail are null-terminated, never circular (unlike circular
  implementations in other libraries).
- `node(i)` chooses direction by `i < size >> 1` — the single optimization that
  makes LinkedList's index operations n/2 rather than n.
- Size and modCount are updated inside `link`/`unlink`, the two private methods
  through which every structural mutation flows.
