# THEORY — Maps Deep

## HashMap
- Buckets array of Node<K,V>. Index = hash(key) & (cap-1).
- Collision: same bucket index → linked list, until TREEIFY_THRESHOLD (8) with cap ≥ 64 → red-black subtree.
- Load factor 0.75; resize doubles capacity and rehashes each node.
- If a key's hashCode()==0 or the bucket spreads, prefix order in buckets shifts.
- Only one null key (maps to bucket 0).

## TreeMap
- Red-black tree; put/get/remove O(log n); preserves sorted iteration and navigable views (floor/ceiling/subMap).
- No null keys (natural ordering); a comparator that accepts null can allow null.

## LinkedHashMap
- HashMap + doubly-linked list of entries in insertion order (or access order with `accessOrder=true`).
- Same O(1) ops; iteration is O(n) regardless of capacity.
- removeEldestEntry hook for LRU-style eviction.

## ConcurrentHashMap
- Java 8+: CAS on bucket head; head node becomes a small synchronization point; treeified bins use find/spread tricks with checkpoint nodes (ForwardingNode during resize, transfer of buckets).
- No null keys/values; weakly consistent iterators.
- Bulk ops: forEach/reduce with parallelism threshold.

## Bloom filter
- See data-structures-advanced: false positives possible, false negatives none; no deletion; sizing via m/n and k.

## Decision
| Workload | Pick |
|---|---|
| General unordered map | HashMap |
| Ordered iteration / range views | TreeMap |
| Insertion-order iteration / LRU | LinkedHashMap |
| Concurrent unordered map | ConcurrentHashMap |
| Fast "maybe present" membership | Bloom filter |
