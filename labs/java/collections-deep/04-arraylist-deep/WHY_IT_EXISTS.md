# Why It Exists: ArrayList Deep Dive

`java.util.ArrayList` exists because one access pattern dominates real code: resolve a
position fast, then touch only that neighborhood.

- Arrays give O(1) indexing but fixed size; chains/links/trees (resizable array: Object[] elementData + size, contiguous storage)
  add growth without giving up the fast path (growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf).
- The 1998 Collections framework (Josh Bloch) needed a general map/list/set
  trio; `java.util.ArrayList` filled the slot its shape fits: resizable array: Object[] elementData + size, contiguous storage.
- Later pressure hardened it: hash-flooding forced lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10, multicore
  forced the concurrency split in unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList, large heaps forced two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact).

Without it you reimplement the same three ideas badly: position
(growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf), scale (two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact)), null/ordering contract (fastRemove nulls the freed slot (elementData[--size]=null) to avoid leaks).
The JDK version just has the edge cases — MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves) — already handled.
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/WHY_IT_EXISTS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
