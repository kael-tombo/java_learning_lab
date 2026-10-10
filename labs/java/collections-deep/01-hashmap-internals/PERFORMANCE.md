# Performance: HashMap Internals

## Hot-path costs (`java.util.HashMap`)
| Op | Cost | Notes |
|----|------|-------|
| lookup | O(1) hash / O(n/2) linked walk / O(log n) tree | per spreader `h ^ (h >>> 16)` folds high bits down |
| insert | O(1) amortized / O(log n) tree | plus resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0 |
| remove | same as insert | slot hygiene: TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties |
| iteration | O(n) | entrySet().iterator() EntryIterator |

## Constants that dominate
- default capacity 16, load factor 0.75: first-touch allocation or default sizing decides L1/cache behavior.
- TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64: threshold crossings are the latency spikes in profiles.
- Pointer chasing (linked/tree) vs contiguous scan (array): contiguous wins
  per element by ~4-16x in cache misses even at equal big-O.

## Sizing guidance
- Known n up front: presize once (initialCapacity / ensureCapacity / sizeCtl
  equivalent) to skip the geometric copy series (resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0).
- Unknown n: accept amortized growth; call trimToSize/compact only after load.

## Concurrency cost
- fail-fast via modCount, ConcurrentModificationException. Contended bucket/cell updates serialize; uncontended paths
  stay CAS-only or lock-free — see THEORY.md for the exact split.

## What to measure
- JMH put/get/remove at n = 10 / 10K / 1M; report p99, not just mean.
- GC logs during bulk load separate copy cost from collection pauses.
- Lab note (01-hashmap-internals/PERFORMANCE.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/PERFORMANCE.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
