# Common Mistakes: ConcurrentHashMap

## 1. Assuming the wrong cost model
- Mistake: treating every op as O(1) (or O(n)) regardless of structure.
- Reality: sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer; putVal rejects null key/value with NullPointerException. Measure with JMH before "optimizing".

## 2. Mutating during iteration directly
- Mistake: calling `list.remove(x)` / `map.remove(k)` inside a for-each loop.
- Fix: mutate through the iterator (`it.remove()`, `ListIterator.set`), or
  collect keys first. Note volatile tabAt/casTabAt reads; Node.val/next volatile.

## 3. Misusing equality vs ordering/identity
- Mistake: inconsistent `equals/hashCode` (hash structures) or comparator
  inconsistent with equals (sorted structures).
- Reality: spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative; TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap.

## 4. Ignoring null rules
- Mistake: storing null where it is banned, or relying on null-key lookup
  where it is allowed.
- Reality: counting via baseCount + CounterCell[] (LongAdder-style); sumCount() snapshot.

## 5. Forgetting views are live
- Mistake: assuming `weakly-consistent iterators (never throw CME)` snapshots the data.
- Fix: copy (`new ArrayList<>(view)`) when you need stability.

## 6. Sharing without synchronization
- Mistake: publishing one instance across threads with no guard.
- Reality: volatile tabAt/casTabAt reads; Node.val/next volatile.

## 7. Presizing blindly or never
- Mistake: default-constructing for a known 1M-element load, or presizing tiny lists.
- Fix: size from measured load; see PERFORMANCE.md.
