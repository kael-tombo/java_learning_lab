# THEORY — Sets Deep

## HashSet
- Backed by a HashMap with a DUMMY value; add/remove/contains O(1) average.
- Iteration order is unspecified (depends on hashes).
- One null allowed.

## TreeSet
- Backed by a TreeMap (red-black). O(log n).
- Iteration is sorted by natural order or comparator.
- Navigable API: floor/ceiling/headSet/subSet.
- No null elements (unless comparator handles null).

## LinkedHashSet
- HashSet + linked-list order of insertion. O(1) ops; iteration in insertion order.
- One null allowed.

## BitSet
- Packed bits; index i = word i/64, bit i%64.
- O(1) get/set, very dense, no per-element headers, but only indexes (not arbitrary objects).
- and/or/xor/not — bitwise set algebra in O(length/64).

## EnumSet
- Special case: all fields of an enum — backed by a long bit mask; very fast.

## Decision
| Workload | Pick |
|---|---|
| Unordered de-dup | HashSet |
| Sorted membership + navigation | TreeSet |
| Insertion-order iteration | LinkedHashSet |
| Dense small index universe | BitSet |
| Enum flags | EnumSet |
