# Mental Models: TreeMap / TreeSet

## 1. Slots plus overflow
Think of `java.util.TreeMap / java.util.TreeSet` as numbered slots plus an overflow strategy: red-black tree of Entry nodes (TreeSet = TreeMap<E,Boolean> with PRESENT sentinel).
Position first (color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1)), then resolve the few items that share it.

## 2. Thresholds as tripwires
identity is compareTo==0 (or comparator.compare==0), NOT equals() — each is a tripwire that converts a cheap shape into a
scalable one (compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first). Below the wire, linear scan is fine; above it,
you pay for structure once and save on every later op.

## 3. Views as windows, not photos
`NavigableSubMap view classes` is a window into the live store. Writing through the
window writes the room. Copy when you need a photo.

## 4. Nulls as contract, not accident
live bounded views: subMap/headMap/tailMap (+ Navigable variants); descendingMap reversed view. The rule exists so "absent" stays distinguishable from
"present" under the class's concurrency/ordering guarantees.

## 5. Growth cost as rent
iteration ascending via on-the-fly successor links; fail-fast via modCount; compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first. You pay rent (copies/rotations) rarely and in bulk;
steady-state ops stay cheap. Presizing is paying a year up front.

## 6. The extra gear
floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n). That detail is what separates a passing interview answer
from one that matches `java.util.TreeMap`.
- Lab note (05-treemap-treeset/MENTAL_MODELS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/MENTAL_MODELS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/MENTAL_MODELS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/MENTAL_MODELS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
