# Reflection: HashMap Internals

## What did you actually learn?
- Write the position rule from memory: spreader `h ^ (h >>> 16)` folds high bits down.
- Write the thresholds: TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64. When do they *not* apply?

## Where did you get surprised?
- Growth (resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0) vs your prior assumption — what changed?
- Null behavior (null key allowed once, hash 0, bucket 0) — did you predict it correctly before testing?

## Transfer check
- Given a new structure with the same shape (hash table with separate chaining over a Node[] table), which invariant
  would you verify first, and how?
- Extra detail to retain: TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties.

## Calibration
- Rate 1-5: can you explain `put(k,v)/get(k)/remove(k)` at the field level without notes?
- If below 4: redo EXERCISES.md #1 and #6, then re-take QUIZ.md.

## One-line synthesis
- `java.util.HashMap`: position via spreader `h ^ (h >>> 16)` folds high bits down, scale via resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0, iterate via
  entrySet().iterator() EntryIterator — everything else is commentary.
- Lab note (01-hashmap-internals/REFLECTION.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/REFLECTION.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/REFLECTION.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/REFLECTION.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/REFLECTION.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/REFLECTION.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/REFLECTION.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/REFLECTION.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
