# How Circular Buffers Work

## Pointer Arithmetic

`
head = 0, tail = 0, size = 0:  [ | | | ]
head = 0, tail = 3, size = 3:  [A|B|C| ]
head = 1, tail = 4, size = 3:  [ |B|C|D] (A consumed, D added)
`

## Wrap Around

When pointers reach the end, they wrap using modulo:
`
head = (head + 1) % capacity
tail = (tail + 1) % capacity
`

## Implementation

`java
public boolean offer(T value) {
    if (isFull()) return false;
    buffer[tail] = value;
    tail = (tail + 1) % capacity;
    size++;
    return true;
}

public T poll() {
    if (isEmpty()) return null;
    T value = (T) buffer[head];
    head = (head + 1) % capacity;
    size--;
    return value;
}
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# Internals of Circular Buffers

## Memory Layout

The buffer is a contiguous array. Pointers are integers used as array indices. Wrapping is achieved with modulo arithmetic (or bitwise AND if capacity is a power of 2).

## Optimizations

Using power-of-2 capacity enables fast wrapping:
`
// Instead of: i = (i + 1) % capacity
i = (i + 1) & (capacity - 1);  // only works if capacity is power of 2
`

## Thread Safety

For single-producer single-consumer (SPSC):
- No locks needed if using volatile for head/tail
- Memory barriers ensure visibility

For multi-producer multi-consumer (MPMC):
- CAS operations on head/tail
- Lock-based synchronized access
