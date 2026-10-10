# Reflection: ConcurrentHashMap

## What did you actually learn?
- Write the position rule from memory: putVal rejects null key/value with NullPointerException.
- Write the thresholds: spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative. When do they *not* apply?

## Where did you get surprised?
- Growth (sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer) vs your prior assumption — what changed?
- Null behavior (counting via baseCount + CounterCell[] (LongAdder-style); sumCount() snapshot) — did you predict it correctly before testing?

## Transfer check
- Given a new structure with the same shape (lock-striped hash table: buckets (not the map) are the locking unit), which invariant
  would you verify first, and how?
- Extra detail to retain: TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap.

## Calibration
- Rate 1-5: can you explain `putVal/merge/compute/putIfAbsent` at the field level without notes?
- If below 4: redo EXERCISES.md #1 and #6, then re-take QUIZ.md.

## One-line synthesis
- `java.util.concurrent.ConcurrentHashMap`: position via putVal rejects null key/value with NullPointerException, scale via sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer, iterate via
  weakly-consistent iterators (never throw CME) — everything else is commentary.
- Lab note (02-concurrent-hashmap/REFLECTION.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/REFLECTION.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/REFLECTION.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/REFLECTION.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/REFLECTION.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/REFLECTION.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/REFLECTION.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/REFLECTION.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
