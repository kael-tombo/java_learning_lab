# Performance

| Implementation | Enqueue | Dequeue | Memory |
|---------------|---------|---------|--------|
| CircularBuffer (overwrite) | O(1) | O(1) | O(N) |
| BlockingCircularBuffer | O(1) | O(1) | O(N) |
| LinkedList | O(1) | O(1) | O(N) + overhead |
| ArrayDeque | O(1) amor. | O(1) | O(N) |

Circular buffers have the best cache locality: sequential access pattern, contiguous memory.

For 10^7 operations:
- CircularBuffer: ~50ms
- LinkedList: ~200ms
- ArrayDeque: ~80ms
