# Why It Exists: TreeMap / TreeSet

`java.util.TreeMap / java.util.TreeSet` exists because one access pattern dominates real code: resolve a
position fast, then touch only that neighborhood.

- Arrays give O(1) indexing but fixed size; chains/links/trees (red-black tree of Entry nodes (TreeSet = TreeMap<E,Boolean> with PRESENT sentinel))
  add growth without giving up the fast path (color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1)).
- The 1998 Collections framework (Josh Bloch) needed a general map/list/set
  trio; `java.util.TreeMap / java.util.TreeSet` filled the slot its shape fits: red-black tree of Entry nodes (TreeSet = TreeMap<E,Boolean> with PRESENT sentinel).
- Later pressure hardened it: hash-flooding forced identity is compareTo==0 (or comparator.compare==0), NOT equals(), multicore
  forced the concurrency split in unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them, large heaps forced compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first.

Without it you reimplement the same three ideas badly: position
(color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1)), scale (compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first), null/ordering contract (live bounded views: subMap/headMap/tailMap (+ Navigable variants); descendingMap reversed view).
The JDK version just has the edge cases — floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n) — already handled.
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/WHY_IT_EXISTS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
