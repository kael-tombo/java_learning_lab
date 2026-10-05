# EXERCISES — Maps Deep

1. Implement a small hash map with chaining and a load-factor trigger.
2. Trace how resize rehashes nodes into new bucket indices.
3. Explain what happens when a bucket exceeds 8 nodes but capacity < 64.
4. Implement a simple TreeMap using a BST (ignore balancing); observe depth.
5. Time TreeMap vs HashMap for 100k inserts and iterations.
6. Build a LinkedHashMap-style order tracker using a DL list + map.
7. Implement an LRU via LinkedHashMap.removeEldestEntry.
8. Read Java 8 ConcurrentHashMap.put source; trace CAS on head.
9. Compare ConcurrentHashMap vs Collections.synchronizedMap concurrency.
10. Build a Bloom filter; sweep k and measure FPR.
11. Show why HashMap allows only one null key.
12. Implement merge/computeIfAbsent using a HashMap.
13. Demonstrate Iterator.remove vs keySet removal.
14. Create a workload that would treeify a bucket; observe get latency.
15. Pick a map for 5 workloads: unicast cache, leaderboard, insertion-log, concurrent counter store, de-dup filter.
