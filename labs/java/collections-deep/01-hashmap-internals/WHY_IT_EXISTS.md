# Why It Exists: HashMap Internals

`java.util.HashMap` exists because one access pattern dominates real code: resolve a
position fast, then touch only that neighborhood.

- Arrays give O(1) indexing but fixed size; chains/links/trees (hash table with separate chaining over a Node[] table)
  add growth without giving up the fast path (spreader `h ^ (h >>> 16)` folds high bits down).
- The 1998 Collections framework (Josh Bloch) needed a general map/list/set
  trio; `java.util.HashMap` filled the slot its shape fits: hash table with separate chaining over a Node[] table.
- Later pressure hardened it: hash-flooding forced TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64, multicore
  forced the concurrency split in fail-fast via modCount, ConcurrentModificationException, large heaps forced resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0.

Without it you reimplement the same three ideas badly: position
(spreader `h ^ (h >>> 16)` folds high bits down), scale (resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0), null/ordering contract (null key allowed once, hash 0, bucket 0).
The JDK version just has the edge cases — TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties — already handled.
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_EXISTS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
