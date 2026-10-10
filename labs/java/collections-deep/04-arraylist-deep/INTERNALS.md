# Internals: ArrayList Deep Dive

Source: `java.util.ArrayList`. Field-level behavior verified in CODE_DEEP_DIVE.md.

## Store layout
- resizable array: Object[] elementData + size, contiguous storage.
- Size/capacity counters kept incrementally; set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it.

## Position computation
- Rule: growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf.
- Thresholds: lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10.

## Mutation mechanics
- Growth/rebalance: two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact).
- Slot hygiene: MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves).
- Null handling: fastRemove nulls the freed slot (elementData[--size]=null) to avoid leaks.

## Concurrency/visibility
- unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList.
- Hot path: add/get/set/remove/ensureCapacity/trimToSize; views: SubList view + fail-fast Itr/ListItr.

## Invariants (must hold after every public op)
1. Position rule (growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf) resolves every live entry.
2. Size equals live-entry count; freed slots hold no stale refs.
3. Thresholds (lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10) trigger before the next op, never lazily skipped.
4. Growth (two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact)) preserves all entries exactly once.
- Lab note (04-arraylist-deep/INTERNALS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/INTERNALS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/INTERNALS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/INTERNALS.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
