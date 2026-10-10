# Common Mistakes: TreeMap / TreeSet

## 1. Assuming the wrong cost model
- Mistake: treating every op as O(1) (or O(n)) regardless of structure.
- Reality: compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first; color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1). Measure with JMH before "optimizing".

## 2. Mutating during iteration directly
- Mistake: calling `list.remove(x)` / `map.remove(k)` inside a for-each loop.
- Fix: mutate through the iterator (`it.remove()`, `ListIterator.set`), or
  collect keys first. Note unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them.

## 3. Misusing equality vs ordering/identity
- Mistake: inconsistent `equals/hashCode` (hash structures) or comparator
  inconsistent with equals (sorted structures).
- Reality: identity is compareTo==0 (or comparator.compare==0), NOT equals(); floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n).

## 4. Ignoring null rules
- Mistake: storing null where it is banned, or relying on null-key lookup
  where it is allowed.
- Reality: live bounded views: subMap/headMap/tailMap (+ Navigable variants); descendingMap reversed view.

## 5. Forgetting views are live
- Mistake: assuming `NavigableSubMap view classes` snapshots the data.
- Fix: copy (`new ArrayList<>(view)`) when you need stability.

## 6. Sharing without synchronization
- Mistake: publishing one instance across threads with no guard.
- Reality: unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them.

## 7. Presizing blindly or never
- Mistake: default-constructing for a known 1M-element load, or presizing tiny lists.
- Fix: size from measured load; see PERFORMANCE.md.
