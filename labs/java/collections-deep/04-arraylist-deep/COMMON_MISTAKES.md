# Common Mistakes: ArrayList Deep Dive

## 1. Assuming the wrong cost model
- Mistake: treating every op as O(1) (or O(n)) regardless of structure.
- Reality: two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact); growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf. Measure with JMH before "optimizing".

## 2. Mutating during iteration directly
- Mistake: calling `list.remove(x)` / `map.remove(k)` inside a for-each loop.
- Fix: mutate through the iterator (`it.remove()`, `ListIterator.set`), or
  collect keys first. Note unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList.

## 3. Misusing equality vs ordering/identity
- Mistake: inconsistent `equals/hashCode` (hash structures) or comparator
  inconsistent with equals (sorted structures).
- Reality: lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10; MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves).

## 4. Ignoring null rules
- Mistake: storing null where it is banned, or relying on null-key lookup
  where it is allowed.
- Reality: fastRemove nulls the freed slot (elementData[--size]=null) to avoid leaks.

## 5. Forgetting views are live
- Mistake: assuming `SubList view + fail-fast Itr/ListItr` snapshots the data.
- Fix: copy (`new ArrayList<>(view)`) when you need stability.

## 6. Sharing without synchronization
- Mistake: publishing one instance across threads with no guard.
- Reality: unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList.

## 7. Presizing blindly or never
- Mistake: default-constructing for a known 1M-element load, or presizing tiny lists.
- Fix: size from measured load; see PERFORMANCE.md.
