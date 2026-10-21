# Code Deep Dive: LRUCache.java

## Implementation

The HashMap + Doubly Linked List implementation requires careful pointer management. The key design decisions are:

1. **Sentinel nodes**: Simplify edge cases (empty list, single element)
2. **Separate helper methods**: removeNode, addToHead, moveToHead
3. **Key stored in node**: Needed for map removal during eviction
4. **Capacity as final**: Cache size is fixed at construction

## Key Methods

`java
public int get(int key) {
    Node node = map.get(key);
    if (node == null) return -1;
    moveToHead(node);
    return node.value;
}

public void put(int key, int value) {
    Node node = map.get(key);
    if (node != null) {
        node.value = value;
        moveToHead(node);
    } else {
        node = new Node(key, value);
        map.put(key, node);
        addToHead(node);
        if (map.size() > capacity) evict();
    }
}
`
"@

System.Collections.Hashtable["STEP_BY_STEP.md"] = @"
# Step-by-Step: Implementing LRU Cache

1. Define Node class with key, value, prev, next
2. Initialize head and tail sentinel nodes
3. Initialize HashMap
4. Implement removeNode: prev.next = next; next.prev = prev
5. Implement addToHead: attach after head sentinel
6. Implement moveToHead: removeNode + addToHead
7. Implement get: check map, move to head, return value
8. Implement put: update or create, move to head, evict if needed
9. Implement LinkedHashMap version (simpler)
10. Test with capacity 1, 2, large
11. Add thread safety
