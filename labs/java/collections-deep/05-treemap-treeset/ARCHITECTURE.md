# Architecture: TreeMap / TreeSet

## Component map (`java.util.TreeMap`)
- Backing store: red-black tree of Entry nodes (TreeSet = TreeMap<E,Boolean> with PRESENT sentinel).
- Entry/node type holds key, value (or item), plus structural links.
- Size counter maintained incrementally; views share the store (no copies).

## Write path
- Locate position (color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1)).
- Mutate one slot/bin only; update size and modCount as specified in THEORY.md.
- Secondary work (compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first) runs on the same path, never as a background copy.

## Read path
- Reads resolve position first, then dereference; unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them.
- View reads (NavigableSubMap view classes) traverse the live store, so they observe later writes.

## Boundaries
- Public API (`getEntry/put/fixAfterInsertion/fixAfterDeletion/getSuccessor`) is the contract; private helpers (link/unlink, fixAfter*,
  resize/transfer, treeify helpers) are free to change across JDK releases.
- Extra invariant: floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n).

## Failure handling
- Structural drift during iteration is detected best-effort (fail-fast) except
  where the class documents weak consistency (see THEORY.md).
- Capacity errors surface as OutOfMemoryError, never silent truncation.

## Evolution notes
- Lazy allocation keeps the empty-instance footprint near zero.
- Growth/rebalance work is amortized into the triggering write, not deferred.
- Review hook: re-read INTERNALS.md after any JDK upgrade; private member names drift.
