# Architecture: LinkedList Deep Dive

## Component map (`java.util.LinkedList`)
- Backing store: doubly-linked list of Node{item,next,prev} with first/last handles and size.
- Entry/node type holds key, value (or item), plus structural links.
- Size counter maintained incrementally; views share the store (no copies).

## Write path
- Locate position (node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last).
- Mutate one slot/bin only; update size and modCount as specified in THEORY.md.
- Secondary work (no sentinel node: size==0 means first==last==null, every mutation branches on null) runs on the same path, never as a background copy.

## Read path
- Reads resolve position first, then dereference; unsynchronized; structural change must flow through link/unlink (size+modCount).
- View reads (ListItr / DescendingIterator) traverse the live store, so they observe later writes.

## Boundaries
- Public API (`linkFirst/linkLast/linkBefore + unlink/unlinkFirst/unlinkLast`) is the contract; private helpers (link/unlink, fixAfter*,
  resize/transfer, treeify helpers) are free to change across JDK releases.
- Extra invariant: doubly-linked symmetry: node.next.prev == node.prev.next == node.

## Failure handling
- Structural drift during iteration is detected best-effort (fail-fast) except
  where the class documents weak consistency (see THEORY.md).
- Capacity errors surface as OutOfMemoryError, never silent truncation.

## Evolution notes
- Lazy allocation keeps the empty-instance footprint near zero.
- Growth/rebalance work is amortized into the triggering write, not deferred.
- Review hook: re-read INTERNALS.md after any JDK upgrade; private member names drift.
