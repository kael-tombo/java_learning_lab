# Common Mistakes with LRU Cache

1. **Not updating map on eviction**: Node removed from list but key stays in map
2. **Sentinel node confusion**: Treating sentinels as actual nodes
3. **Null pointer on empty cache**: Not checking head.next vs tail
4. **Doubly linked list pointer errors**: Prev/next not both updated
5. **Not updating size correctly**: Size mismatch between map and list
6. **LinkedHashMap ordering mode**: Must set accessOrder=true
7. **Integer overflow**: Cache capacity validation
8. **Thread safety**: Race conditions in concurrent access
