# How It Works: HashMap Internals

`java.util.HashMap` is a hash table with separate chaining over a Node[] table.

## Lookup
1. Compute position per spreader `h ^ (h >>> 16)` folds high bits down.
2. Walk the local structure (chain / links / tree descent) using the
   identity rule in TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64.
3. Return the entry or null/absent per null key allowed once, hash 0, bucket 0.

## Insert
1. Resolve position; handle the empty-store fast path (default capacity 16, load factor 0.75).
2. Splice/link/rotate the node in; update size.
3. Run growth/rebalance work (resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0) when its threshold trips.

## Remove
1. Locate as in lookup; unlink and patch neighbors/parents.
2. Clear the freed slot or rebalance (TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties).
3. Views (entrySet().iterator() EntryIterator) observe the removal immediately.

## Iteration
- Order follows the structure (insertion-neutral, index order, or sorted),
  and fail-fast via modCount, ConcurrentModificationException.

## Worked trace
- Insert 3 small keys: store allocates per default capacity 16, load factor 0.75, each key resolves via
  spreader `h ^ (h >>> 16)` folds high bits down, size becomes 3, no growth yet (resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0 not tripped).
- Core calls exercised: put(k,v)/get(k)/remove(k).
- Lab note (01-hashmap-internals/HOW_IT_WORKS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/HOW_IT_WORKS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
