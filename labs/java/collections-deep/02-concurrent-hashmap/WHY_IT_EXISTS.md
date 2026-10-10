# Why It Exists: ConcurrentHashMap

`java.util.concurrent.ConcurrentHashMap` exists because one access pattern dominates real code: resolve a
position fast, then touch only that neighborhood.

- Arrays give O(1) indexing but fixed size; chains/links/trees (lock-striped hash table: buckets (not the map) are the locking unit)
  add growth without giving up the fast path (putVal rejects null key/value with NullPointerException).
- The 1998 Collections framework (Josh Bloch) needed a general map/list/set
  trio; `java.util.concurrent.ConcurrentHashMap` filled the slot its shape fits: lock-striped hash table: buckets (not the map) are the locking unit.
- Later pressure hardened it: hash-flooding forced spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative, multicore
  forced the concurrency split in volatile tabAt/casTabAt reads; Node.val/next volatile, large heaps forced sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer.

Without it you reimplement the same three ideas badly: position
(putVal rejects null key/value with NullPointerException), scale (sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer), null/ordering contract (counting via baseCount + CounterCell[] (LongAdder-style); sumCount() snapshot).
The JDK version just has the edge cases — TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap — already handled.
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_EXISTS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
