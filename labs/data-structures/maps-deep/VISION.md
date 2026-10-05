# VISION — Maps Deep

Vision: pick HashMap vs TreeMap vs LinkedHashMap vs ConcurrentHashMap vs Bloom by the access pattern, ordering needs, and concurrency.

## Mental models
- HashMap = hashed buckets of chains/trees: O(1) average.
- TreeMap = red-black tree: O(log n) and sorted views.
- LinkedHashMap = HashMap + access-order list: insertion/LRU iteration.
- ConcurrentHashMap = per-bucket CAS: thread-safe O(1) average.
- Bloom = bitset with k hashes: "maybe present" membership.

## Decision table
| Workload | Pick |
|---|---|
| Unordered general | HashMap |
| Sorted iteration / range views | TreeMap |
| Insertion-order iteration or LRU | LinkedHashMap |
| Concurrent unordered map | ConcurrentHashMap |
| Fast de-dup/membership | Bloom |

## Career path
- Shows up in: interviews, caches, concurrent services.
- Story: "I know when I reach for a TreeMap vs a HashMap, and I design caches with LinkedHashMap access order."

## Done when
- [ ] Explain load factor + treeification
- [ ] Explain ConcurrentHashMap bucket locking
- [ ] Mini + real-world projects shipped
