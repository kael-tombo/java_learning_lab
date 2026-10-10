# How It Works: ConcurrentHashMap

`java.util.concurrent.ConcurrentHashMap` is a lock-striped hash table: buckets (not the map) are the locking unit.

## Lookup
1. Compute position per putVal rejects null key/value with NullPointerException.
2. Walk the local structure (chain / links / tree descent) using the
   identity rule in spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative.
3. Return the entry or null/absent per counting via baseCount + CounterCell[] (LongAdder-style); sumCount() snapshot.

## Insert
1. Resolve position; handle the empty-store fast path (writes lock only bucket head synchronized(f); empty-bin insert is pure CAS (casTabAt)).
2. Splice/link/rotate the node in; update size.
3. Run growth/rebalance work (sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer) when its threshold trips.

## Remove
1. Locate as in lookup; unlink and patch neighbors/parents.
2. Clear the freed slot or rebalance (TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap).
3. Views (weakly-consistent iterators (never throw CME)) observe the removal immediately.

## Iteration
- Order follows the structure (insertion-neutral, index order, or sorted),
  and volatile tabAt/casTabAt reads; Node.val/next volatile.

## Worked trace
- Insert 3 small keys: store allocates per writes lock only bucket head synchronized(f); empty-bin insert is pure CAS (casTabAt), each key resolves via
  putVal rejects null key/value with NullPointerException, size becomes 3, no growth yet (sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer not tripped).
- Core calls exercised: putVal/merge/compute/putIfAbsent.
- Lab note (02-concurrent-hashmap/HOW_IT_WORKS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/HOW_IT_WORKS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
