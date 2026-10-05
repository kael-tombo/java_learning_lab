# EXERCISES — Sets Deep

1. Implement a hash set on top of your own small hash map (chaining).
2. Show that a broken hashCode corrupts HashSet membership.
3. Show that HashSet.add runs in O(1) average by counting hash map buckets.
4. Implement a TreeSet-like SortedSet with a BST (ignore balancing).
5. Trace TreeSet.floor/ceiling on a set of 5 ints.
6. Compare LinkedHashSet vs HashSet iteration order.
7. Use BitSet to implement a sieve of Eratosthenes up to n.
8. Implement a set union/intersect with BitSet (and/or).
9. Replace HashSet<Integer> with BitSet when domain is dense; measure.
10. Time TreeSet add vs HashSet add at n=100k.
11. Create a TreeSet with a custom comparator that reverses order.
12. Implement EnumSet vs boolean[] semantics parity test.
13. Demonstrate why a TreeSet rejects null keys.
14. Implement a Set.removeIf; compare with iterator.remove.
15. Pick a set for 5 workloads: feature flags, sorted IDs, insertion-order audit, dense index set, fast enum tests.
