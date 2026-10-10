# Architecture: HashMap Internals

## Component map (`java.util.HashMap`)
- Backing store: hash table with separate chaining over a Node[] table.
- Entry/node type holds key, value (or item), plus structural links.
- Size counter maintained incrementally; views share the store (no copies).

## Write path
- Locate position (spreader `h ^ (h >>> 16)` folds high bits down).
- Mutate one slot/bin only; update size and modCount as specified in THEORY.md.
- Secondary work (resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0) runs on the same path, never as a background copy.

## Read path
- Reads resolve position first, then dereference; fail-fast via modCount, ConcurrentModificationException.
- View reads (entrySet().iterator() EntryIterator) traverse the live store, so they observe later writes.

## Boundaries
- Public API (`put(k,v)/get(k)/remove(k)`) is the contract; private helpers (link/unlink, fixAfter*,
  resize/transfer, treeify helpers) are free to change across JDK releases.
- Extra invariant: TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties.

## Failure handling
- Structural drift during iteration is detected best-effort (fail-fast) except
  where the class documents weak consistency (see THEORY.md).
- Capacity errors surface as OutOfMemoryError, never silent truncation.

## Evolution notes
- Lazy allocation keeps the empty-instance footprint near zero.
- Growth/rebalance work is amortized into the triggering write, not deferred.
- Review hook: re-read INTERNALS.md after any JDK upgrade; private member names drift.
