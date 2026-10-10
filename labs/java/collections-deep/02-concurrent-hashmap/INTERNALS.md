# Internals: ConcurrentHashMap

Source: `java.util.concurrent.ConcurrentHashMap`. Field-level behavior verified in CODE_DEEP_DIVE.md.

## Store layout
- lock-striped hash table: buckets (not the map) are the locking unit.
- Size/capacity counters kept incrementally; writes lock only bucket head synchronized(f); empty-bin insert is pure CAS (casTabAt).

## Position computation
- Rule: putVal rejects null key/value with NullPointerException.
- Thresholds: spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative.

## Mutation mechanics
- Growth/rebalance: sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer.
- Slot hygiene: TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap.
- Null handling: counting via baseCount + CounterCell[] (LongAdder-style); sumCount() snapshot.

## Concurrency/visibility
- volatile tabAt/casTabAt reads; Node.val/next volatile.
- Hot path: putVal/merge/compute/putIfAbsent; views: weakly-consistent iterators (never throw CME).

## Invariants (must hold after every public op)
1. Position rule (putVal rejects null key/value with NullPointerException) resolves every live entry.
2. Size equals live-entry count; freed slots hold no stale refs.
3. Thresholds (spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative) trigger before the next op, never lazily skipped.
4. Growth (sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer) preserves all entries exactly once.
- Lab note (02-concurrent-hashmap/INTERNALS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/INTERNALS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/INTERNALS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/INTERNALS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
