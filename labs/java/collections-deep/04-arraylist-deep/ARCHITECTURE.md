# Architecture: ArrayList Deep Dive

## Component map (`java.util.ArrayList`)
- Backing store: resizable array: Object[] elementData + size, contiguous storage.
- Entry/node type holds key, value (or item), plus structural links.
- Size counter maintained incrementally; views share the store (no copies).

## Write path
- Locate position (growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf).
- Mutate one slot/bin only; update size and modCount as specified in THEORY.md.
- Secondary work (two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact)) runs on the same path, never as a background copy.

## Read path
- Reads resolve position first, then dereference; unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList.
- View reads (SubList view + fail-fast Itr/ListItr) traverse the live store, so they observe later writes.

## Boundaries
- Public API (`add/get/set/remove/ensureCapacity/trimToSize`) is the contract; private helpers (link/unlink, fixAfter*,
  resize/transfer, treeify helpers) are free to change across JDK releases.
- Extra invariant: MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves).

## Failure handling
- Structural drift during iteration is detected best-effort (fail-fast) except
  where the class documents weak consistency (see THEORY.md).
- Capacity errors surface as OutOfMemoryError, never silent truncation.

## Evolution notes
- Lazy allocation keeps the empty-instance footprint near zero.
- Growth/rebalance work is amortized into the triggering write, not deferred.
- Review hook: re-read INTERNALS.md after any JDK upgrade; private member names drift.
