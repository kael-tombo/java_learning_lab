# Performance: TreeMap / TreeSet

## Hot-path costs (`java.util.TreeMap`)
| Op | Cost | Notes |
|----|------|-------|
| lookup | O(1) hash / O(n/2) linked walk / O(log n) tree | per color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1) |
| insert | O(1) amortized / O(log n) tree | plus compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first |
| remove | same as insert | slot hygiene: floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n) |
| iteration | O(n) | NavigableSubMap view classes |

## Constants that dominate
- iteration ascending via on-the-fly successor links; fail-fast via modCount: first-touch allocation or default sizing decides L1/cache behavior.
- identity is compareTo==0 (or comparator.compare==0), NOT equals(): threshold crossings are the latency spikes in profiles.
- Pointer chasing (linked/tree) vs contiguous scan (array): contiguous wins
  per element by ~4-16x in cache misses even at equal big-O.

## Sizing guidance
- Known n up front: presize once (initialCapacity / ensureCapacity / sizeCtl
  equivalent) to skip the geometric copy series (compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first).
- Unknown n: accept amortized growth; call trimToSize/compact only after load.

## Concurrency cost
- unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them. Contended bucket/cell updates serialize; uncontended paths
  stay CAS-only or lock-free — see THEORY.md for the exact split.

## What to measure
- JMH put/get/remove at n = 10 / 10K / 1M; report p99, not just mean.
- GC logs during bulk load separate copy cost from collection pauses.
- Lab note (05-treemap-treeset/PERFORMANCE.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/PERFORMANCE.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
