# Reflection: TreeMap / TreeSet

## What did you actually learn?
- Write the position rule from memory: color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1).
- Write the thresholds: identity is compareTo==0 (or comparator.compare==0), NOT equals(). When do they *not* apply?

## Where did you get surprised?
- Growth (compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first) vs your prior assumption — what changed?
- Null behavior (live bounded views: subMap/headMap/tailMap (+ Navigable variants); descendingMap reversed view) — did you predict it correctly before testing?

## Transfer check
- Given a new structure with the same shape (red-black tree of Entry nodes (TreeSet = TreeMap<E,Boolean> with PRESENT sentinel)), which invariant
  would you verify first, and how?
- Extra detail to retain: floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n).

## Calibration
- Rate 1-5: can you explain `getEntry/put/fixAfterInsertion/fixAfterDeletion/getSuccessor` at the field level without notes?
- If below 4: redo EXERCISES.md #1 and #6, then re-take QUIZ.md.

## One-line synthesis
- `java.util.TreeMap / java.util.TreeSet`: position via color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1), scale via compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first, iterate via
  NavigableSubMap view classes — everything else is commentary.
- Lab note (05-treemap-treeset/REFLECTION.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/REFLECTION.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/REFLECTION.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/REFLECTION.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/REFLECTION.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/REFLECTION.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/REFLECTION.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/REFLECTION.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
