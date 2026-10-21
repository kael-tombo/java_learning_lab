# Math Foundation

## Capacity and Size

- capacity: fixed at construction
- size: number of elements currently stored
- Available space: capacity - size
- Empty: size == 0
- Full: size == capacity

## Pointer Relationships

- If head <= tail: elements from head to tail-1
- If head > tail: elements from head to capacity-1, and 0 to tail-1
- Number of elements = (tail - head + capacity) % capacity

## Performance

All operations: O(1)
Space: O(capacity)
