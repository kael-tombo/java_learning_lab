# Architecture: ConcurrentHashMap

## Component map (`java.util.concurrent.ConcurrentHashMap`)
- Backing store: lock-striped hash table: buckets (not the map) are the locking unit.
- Entry/node type holds key, value (or item), plus structural links.
- Size counter maintained incrementally; views share the store (no copies).

## Write path
- Locate position (putVal rejects null key/value with NullPointerException).
- Mutate one slot/bin only; update size and modCount as specified in THEORY.md.
- Secondary work (sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer) runs on the same path, never as a background copy.

## Read path
- Reads resolve position first, then dereference; volatile tabAt/casTabAt reads; Node.val/next volatile.
- View reads (weakly-consistent iterators (never throw CME)) traverse the live store, so they observe later writes.

## Boundaries
- Public API (`putVal/merge/compute/putIfAbsent`) is the contract; private helpers (link/unlink, fixAfter*,
  resize/transfer, treeify helpers) are free to change across JDK releases.
- Extra invariant: TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap.

## Failure handling
- Structural drift during iteration is detected best-effort (fail-fast) except
  where the class documents weak consistency (see THEORY.md).
- Capacity errors surface as OutOfMemoryError, never silent truncation.

## Evolution notes
- Lazy allocation keeps the empty-instance footprint near zero.
- Growth/rebalance work is amortized into the triggering write, not deferred.
- Review hook: re-read INTERNALS.md after any JDK upgrade; private member names drift.
