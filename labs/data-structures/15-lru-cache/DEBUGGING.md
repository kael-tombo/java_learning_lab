# Debugging LRU Cache

## Common Issues

| Symptom | Cause |
|---------|-------|
| get returns wrong value | Node value not updated |
| get returns -1 for existing key | Node not in map or evicted incorrectly |
| Eviction removes wrong item | LinkedList order corrupted |
| NullPointerException | Sentinel node logic error |
| ConcurrentModificationException | Unsynchronized iteration |

## Print State

`java
void printCache() {
    Node cur = head.next;
    while (cur != tail) {
        System.out.print("[" + cur.key + ":" + cur.value + "] ");
        cur = cur.next;
    }
    System.out.println();
}
`
"@

System.Collections.Hashtable["REFACTORING.md"] = @"
# Refactoring LRU Cache

1. **Abstract eviction policy**: Strategy pattern for LRU, LFU, FIFO
2. **Generic types**: LRUCache<K, V>
3. **Listener callbacks**: Notify on eviction
4. **Statistics tracking**: Hit rate, miss rate
5. **Time-based expiration**: TTL in addition to LRU
6. **Persistent cache**: Back with database
7. **Distributed cache**: Consistent hashing + LRU nodes
