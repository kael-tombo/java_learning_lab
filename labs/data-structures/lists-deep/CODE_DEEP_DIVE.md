# CODE_DEEP_DIVE — Lists Deep

## ArrayList source notes
- `private transient Object[] elementData;` + `private int size;`
- `add` → `add(E e)` calls `add(size, e)`; `add(index, e)` uses `System.arraycopy(elementData, index, elementData, index+1, size - index)`.
- `grow` uses `Arrays.copyOf` then `newLength = oldLength + (oldLength >> 1)`.
- Iterators created via `itr = new Itr()` capture `expectedModCount = modCount`; every `next/checkForComodification` throws on mismatch.

Pitfall: using `subList` view after structural change outside the view throws ISE.

## LinkedList source notes
- Node fields: `item`, `next`, `prev`.
- `addFirst(x)` sets `x.next = first; x.prev = null; first.prev = x; first = x;` with a null-first branch.
- `remove(Node x)` unlinks via prev/next.
- Iterator.next walks next pointers; remove unlinks that same node.

Pitfall: calling `iterator.remove` before `next` → IllegalStateException.

## Vector
- `synchronized` on get/addElement/etc.
- `capacityIncrement` used when growing; default 2×.
Pitfall: prefer ArrayList + `Collections.synchronizedList` only if you need legacy.

## Fail-fast vs weakly consistent
- ArrayList/LinkedList/Vector/HashMap: fail-fast (throw CME).
- CopyOnWriteArrayList/ConcurrentHashMap: weakly consistent iterators (snapshot).

## ArrayDeque
- Circular `Object[] elements`; `head`/`tail` indices.
- Rejects null (so peek vs poll indices distinguish empty).

## LinkedList pitfalls in benchmarks
- New node per element → many allocations → GC pressure.
- Neighbor-node cache locality is poor; ArrayDeque wins even in deque roles.

## LRU
- `LinkedHashMap` with `accessOrder=true`, override `removeEldestEntry` → O(1) hit/evict.
- Hand-rolled: HashMap<K, Node> + doubly-linked list.
