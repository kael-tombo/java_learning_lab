# MATH_FOUNDATION — Sets Deep

## HashSet is HashMap
HashSet stores elements as keys in a HashMap with a shared DUMMY value. add/get behave as the underlying map does → expected O(1), resize amortized O(1), load factor 0.75.

## TreeSet is TreeMap
Backed by a red-black tree, so the height is ≤ 2 log(n+1), giving O(log n) add/contains/remove and O(log n) navigation (floor/ceiling).

## BitSet packing
N indices are stored in ⌈N/64⌉ long words → N/64 memory vs N entries. Word-parallel operations (and/or/xor) run in O(words), which is 64× faster per element than hashing.

## LinkedHashSet
Same O(1) as HashSet, plus a doubly-linked order list. Iteration order equals insertion order; extra O(1) per insert/remove for the list pointers.

## EnumSet
Ordinal space of an enum is dense in [0, |E|), so the set is a bitmask; with one or a few long words, operations are O(1).

## Checklist
- [ ] State expected O(1) for HashSet
- [ ] State TreeSet O(log n) from RB height
- [ ] State BitSet word density advantage
- [ ] State LinkedHashSet ordering cost
