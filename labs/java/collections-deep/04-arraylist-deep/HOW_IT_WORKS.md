# How It Works: ArrayList Deep Dive

`java.util.ArrayList` is a resizable array: Object[] elementData + size, contiguous storage.

## Lookup
1. Compute position per growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf.
2. Walk the local structure (chain / links / tree descent) using the
   identity rule in lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10.
3. Return the entry or null/absent per fastRemove nulls the freed slot (elementData[--size]=null) to avoid leaks.

## Insert
1. Resolve position; handle the empty-store fast path (set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it).
2. Splice/link/rotate the node in; update size.
3. Run growth/rebalance work (two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact)) when its threshold trips.

## Remove
1. Locate as in lookup; unlink and patch neighbors/parents.
2. Clear the freed slot or rebalance (MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)).
3. Views (SubList view + fail-fast Itr/ListItr) observe the removal immediately.

## Iteration
- Order follows the structure (insertion-neutral, index order, or sorted),
  and unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList.

## Worked trace
- Insert 3 small keys: store allocates per set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it, each key resolves via
  growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf, size becomes 3, no growth yet (two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact) not tripped).
- Core calls exercised: add/get/set/remove/ensureCapacity/trimToSize.
- Lab note (04-arraylist-deep/HOW_IT_WORKS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/HOW_IT_WORKS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
