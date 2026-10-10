# Flashcards: ArrayList Deep Dive

Q: What is `java.util.ArrayList` structurally?
A: resizable array: Object[] elementData + size, contiguous storage.

Q: State the position rule.
A: growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf.

Q: What are the tree/growth thresholds?
A: lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10.

Q: How does growth/rebalance work?
A: two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact).

Q: What are the null rules?
A: fastRemove nulls the freed slot (elementData[--size]=null) to avoid leaks.

Q: What is the default sizing / allocation behavior?
A: set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it.

Q: Which ops form the hot path?
A: add/get/set/remove/ensureCapacity/trimToSize.

Q: How do views/iterators behave?
A: SubList view + fail-fast Itr/ListItr; unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList.

Q: Name one extra invariant from the source.
A: MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves).

Q: Where is the authoritative behavior defined?
A: `java.util.ArrayList` + THEORY.md / CODE_DEEP_DIVE.md in this lab.
