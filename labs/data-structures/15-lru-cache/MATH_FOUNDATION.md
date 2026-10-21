# Math Foundation of LRU Cache

## Analysis

The LRU cache achieves O(1) for both get and put by combining:
- HashMap for random access to nodes
- Doubly linked list for O(1) insertion/deletion

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| get | O(1) | O(1) per call |
| put | O(1) | O(capacity) total |
| evict | O(1) | O(1) |

## Cache Hit Ratio

The effectiveness of LRU depends on the access pattern. For workloads following Zipf distribution (common in web traffic), LRU achieves 80-99% hit rates with modest cache sizes.
