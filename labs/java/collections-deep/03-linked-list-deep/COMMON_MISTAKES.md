# Common Mistakes: LinkedList Deep Dive

## 1. Assuming the wrong cost model
- Mistake: treating every op as O(1) (or O(n)) regardless of structure.
- Reality: no sentinel node: size==0 means first==last==null, every mutation branches on null; node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last. Measure with JMH before "optimizing".

## 2. Mutating during iteration directly
- Mistake: calling `list.remove(x)` / `map.remove(k)` inside a for-each loop.
- Fix: mutate through the iterator (`it.remove()`, `ListIterator.set`), or
  collect keys first. Note unsynchronized; structural change must flow through link/unlink (size+modCount).

## 3. Misusing equality vs ordering/identity
- Mistake: inconsistent `equals/hashCode` (hash structures) or comparator
  inconsistent with equals (sorted structures).
- Reality: Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs); doubly-linked symmetry: node.next.prev == node.prev.next == node.

## 4. Ignoring null rules
- Mistake: storing null where it is banned, or relying on null-key lookup
  where it is allowed.
- Reality: fail-fast iterators via modCount/expectedModCount; ListIterator.set/remove legal.

## 5. Forgetting views are live
- Mistake: assuming `ListItr / DescendingIterator` snapshots the data.
- Fix: copy (`new ArrayList<>(view)`) when you need stability.

## 6. Sharing without synchronization
- Mistake: publishing one instance across threads with no guard.
- Reality: unsynchronized; structural change must flow through link/unlink (size+modCount).

## 7. Presizing blindly or never
- Mistake: default-constructing for a known 1M-element load, or presizing tiny lists.
- Fix: size from measured load; see PERFORMANCE.md.
