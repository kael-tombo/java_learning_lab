# Internals: HashMap Internals

Source: `java.util.HashMap`. Field-level behavior verified in CODE_DEEP_DIVE.md.

## Store layout
- hash table with separate chaining over a Node[] table.
- Size/capacity counters kept incrementally; default capacity 16, load factor 0.75.

## Position computation
- Rule: spreader `h ^ (h >>> 16)` folds high bits down.
- Thresholds: TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64.

## Mutation mechanics
- Growth/rebalance: resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0.
- Slot hygiene: TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties.
- Null handling: null key allowed once, hash 0, bucket 0.

## Concurrency/visibility
- fail-fast via modCount, ConcurrentModificationException.
- Hot path: put(k,v)/get(k)/remove(k); views: entrySet().iterator() EntryIterator.

## Invariants (must hold after every public op)
1. Position rule (spreader `h ^ (h >>> 16)` folds high bits down) resolves every live entry.
2. Size equals live-entry count; freed slots hold no stale refs.
3. Thresholds (TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64) trigger before the next op, never lazily skipped.
4. Growth (resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0) preserves all entries exactly once.
- Lab note (01-hashmap-internals/INTERNALS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/INTERNALS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/INTERNALS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/INTERNALS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
