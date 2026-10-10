# Common Mistakes: HashMap Internals

## 1. Assuming the wrong cost model
- Mistake: treating every op as O(1) (or O(n)) regardless of structure.
- Reality: resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0; spreader `h ^ (h >>> 16)` folds high bits down. Measure with JMH before "optimizing".

## 2. Mutating during iteration directly
- Mistake: calling `list.remove(x)` / `map.remove(k)` inside a for-each loop.
- Fix: mutate through the iterator (`it.remove()`, `ListIterator.set`), or
  collect keys first. Note fail-fast via modCount, ConcurrentModificationException.

## 3. Misusing equality vs ordering/identity
- Mistake: inconsistent `equals/hashCode` (hash structures) or comparator
  inconsistent with equals (sorted structures).
- Reality: TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64; TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties.

## 4. Ignoring null rules
- Mistake: storing null where it is banned, or relying on null-key lookup
  where it is allowed.
- Reality: null key allowed once, hash 0, bucket 0.

## 5. Forgetting views are live
- Mistake: assuming `entrySet().iterator() EntryIterator` snapshots the data.
- Fix: copy (`new ArrayList<>(view)`) when you need stability.

## 6. Sharing without synchronization
- Mistake: publishing one instance across threads with no guard.
- Reality: fail-fast via modCount, ConcurrentModificationException.

## 7. Presizing blindly or never
- Mistake: default-constructing for a known 1M-element load, or presizing tiny lists.
- Fix: size from measured load; see PERFORMANCE.md.
