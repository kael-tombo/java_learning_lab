# Why It Matters: HashMap Internals

## Everyday impact
- Nearly every request path touches `java.util.HashMap` (caches, indexes, params, models).
  spreader `h ^ (h >>> 16)` folds high bits down is why those lookups stay flat as data grows.

## Cost impact
- resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0; default capacity 16, load factor 0.75. One presize decision at startup can remove the only
  latency spikes the structure ever produces.

## Correctness impact
- TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64; null key allowed once, hash 0, bucket 0. Getting either wrong silently corrupts lookups —
  entries that exist but never match.

## Concurrency impact
- fail-fast via modCount, ConcurrentModificationException. Choosing the wrong variant turns a fast map into a race log.

## Interview signal
- Stating spreader `h ^ (h >>> 16)` folds high bits down + TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64 + resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0 with the numbers (8/6/64,
  0.75/16, 1.5x/2x, RED=false/BLACK=true as applicable) separates recall
  from understanding. Extra credit: TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties.
- Lab note (01-hashmap-internals/WHY_IT_MATTERS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_MATTERS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_MATTERS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_MATTERS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_MATTERS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_MATTERS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_MATTERS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_MATTERS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/WHY_IT_MATTERS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
