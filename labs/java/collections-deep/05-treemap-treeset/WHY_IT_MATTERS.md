# Why It Matters: TreeMap / TreeSet

## Everyday impact
- Nearly every request path touches `java.util.TreeMap / java.util.TreeSet` (caches, indexes, params, models).
  color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1) is why those lookups stay flat as data grows.

## Cost impact
- compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first; iteration ascending via on-the-fly successor links; fail-fast via modCount. One presize decision at startup can remove the only
  latency spikes the structure ever produces.

## Correctness impact
- identity is compareTo==0 (or comparator.compare==0), NOT equals(); live bounded views: subMap/headMap/tailMap (+ Navigable variants); descendingMap reversed view. Getting either wrong silently corrupts lookups —
  entries that exist but never match.

## Concurrency impact
- unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them. Choosing the wrong variant turns a fast map into a race log.

## Interview signal
- Stating color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1) + identity is compareTo==0 (or comparator.compare==0), NOT equals() + compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first with the numbers (8/6/64,
  0.75/16, 1.5x/2x, RED=false/BLACK=true as applicable) separates recall
  from understanding. Extra credit: floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n).
- Lab note (05-treemap-treeset/WHY_IT_MATTERS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_MATTERS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_MATTERS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_MATTERS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_MATTERS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_MATTERS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_MATTERS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_MATTERS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_MATTERS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
