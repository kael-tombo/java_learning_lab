# Theory: LRU Cache

## Fundamentals

An LRU (Least Recently Used) cache is a data structure that stores a limited number of items and evicts the least recently used item when capacity is reached. It combines a hash map for O(1) lookups with a doubly linked list for O(1) insertion/deletion.

## Structure

LRU cache uses:
- **HashMap**: Maps keys to nodes O(1) access
- **Doubly Linked List**: Maintains access order
  - Most recently used: at the head
  - Least recently used: at the tail

## Operations

### get(key)
1. If key exists in map, move its node to head (most recently used)
2. Return value
3. Time: O(1)

### put(key, value)
1. If key exists, update value and move to head
2. If key doesn't exist:
   a. Create new node, add to head
   b. Add to hash map
   c. If over capacity, remove tail node (LRU item)
3. Time: O(1)

## LinkedHashMap Implementation

Java's LinkedHashMap provides a ready-made LRU cache:
`java
class LRUCache {
    private final LinkedHashMap<Integer, Integer> map;
    
    public LRUCache(int capacity) {
        map = new LinkedHashMap<>(capacity, 0.75f, true) {
            protected boolean removeEldestEntry(Map.Entry eldest) {
                return size() > capacity;
            }
        };
    }
}
`

## Comparison: LRU vs LFU

| Property | LRU | LFU |
|----------|-----|-----|
| Eviction Policy | Least recently used | Least frequently used |
| Access Pattern | Recent access matters | Frequency matters |
| Implementation | HashMap + DLL | HashMap + frequency list |
| Space Complexity | O(capacity) | O(capacity) |
| Time Complexity | O(1) | O(1) typical |
| Use Case | General caching | Repeated access patterns |
