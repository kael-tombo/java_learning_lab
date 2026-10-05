# FLASHCARDS — Maps Deep

| # | Front | Back |
|---|---|---|
| 1 | HashMap bucket index? | hash & (cap−1) |
| 2 | Treeify threshold? | 8 |
| 3 | MIN_TREEIFY_CAPACITY? | 64 |
| 4 | Load factor default? | 0.75 |
| 5 | Resize effect? | capacity ×2, rehash |
| 6 | Null keys allowed? | one |
| 7 | TreeMap backing? | red-black tree |
| 8 | TreeMap get? | O(log n) |
| 9 | LinkedHashMap iteration? | insertion/access order |
| 10 | removeEldestEntry used for? | LRU eviction |
| 11 | ConcurrentHashMap Java 8 lock? | CAS + sync on head |
| 12 | CHM iterators? | weakly consistent |
| 13 | CHM nulls? | none |
| 14 | Bloom FPR formula? | (1−e^(−kn/m))^k |
| 15 | Bloom k*? | (m/n) ln2 |
| 16 | HashMap treeification trigger? | bucket ≥ 8 and cap ≥ 64 |
| 17 | Node color in TreeMap? | RB color flag |
| 18 | TreeMap null key? | generally no |
| 19 | LinkedHashMap.accessOrder? | true → LRU mode |
| 20 | HashMap collision resolution? | chaining/tree |
| 21 | HashMap resize keeps? | all entries |
| 22 | Hash collisions cause? | same index |
| 23 | TreeMap ceiling/floor? | O(log n) navigable |
| 24 | LinkedHashMap memory? | entries + linked list |
| 25 | CHM transfer on resize? | bucket-by-bucket |
| 26 | CHM null values? | no |
| 27 | HashMap grow copies? | nodes into new buckets |
| 28 | TreeMap subMap? | view |
| 29 | LinkedHashMap O(1) get? | yes |
| 30 | CHM O(1) get? | yes |
| 31 | HashMap putAll merging? | overwrites |
| 32 | computeIfAbsent semantics? | compute once, cache |
| 33 | merge remapping fn? | value1,value2 → new |
| 34 | TreeMap first/last ops? | first/lastKey O(log n) |
| 35 | HashMap iterator CME? | yes, on concurrent mod |
| 36 | IdentityHashMap? | == instead of equals |
| 37 | WeakHashMap? | gc entries |
| 38 | EnumMap? | array-backed |
| 39 | CHM forEach parallel? | yes with threshold |
| 40 | HashMap tree bin search? | binary by hash |
| 41 | TreeMap comparators equal(0) keys? | treat as same |
| 42 | LinkedHashMap iteration O(n) regardless of cap? | yes |
| 43 | HashMap allows same key diff value? | overwrite |
| 44 | CHM computeIfAbsent? | atomic |
| 45 | CHM size()? | O(n) legacy count |
| 46 | HashMap default capacity? | 16 |
| 47 | TreeMap vs ConcurrentSkipListMap? | CHM? concurrent ordered via skip list |
| 48 | Bloom in maps dir but not a Map? | yes, membership structure |
| 49 | LinkedHashMap.put order? | insertion |
| 50 | HashMap.putIfAbsent? | yes |
| 51 | HashMap.remove(key,value)? | CAS-like semantics |
| 52 | CHM mappingCount long vs size int? | mappingCount |
| 53 | HashMap.rehash on capacity change? | full |
| 54 | TreeMap null values? | allowed |
| 55 | LinkedHashMap null keys? | one |
| 56 | CHM null keys? | no |
| 57 | HashMap implements RandomAccess? | no |
| 58 | TreeMap descendingMap? | view |
| 59 | LinkedHashMap throughput vs HashMap? | slightly lower |
| 60 | When CHM vs synchronizedMap? | high concurrency |
