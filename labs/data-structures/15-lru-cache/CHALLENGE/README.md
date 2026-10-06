# Challenge: LRU Cache

## Goal

Implement a fixed-capacity LRU cache with O(1) `get`, `put`, and `evict`.

## Requirements

- HashMap from key to a doubly-linked node
- Sentinel head/tail to avoid null-pointer special cases
- `get` moves the node to the front (MRU)
- `put` inserts or updates, moves to front, evicts tail if over capacity
- Track hit/miss counts for a hit-rate query

## Stretch goals

1. `resize(newCapacity)` that drains the tail until within bounds
2. Concurrent access using striped locks or a bounded ConcurrentLinkedDeque
3. A fuzz test asserting: map size == list size, head == MRU, tail == LRU

## Run with

```bash
javac -d out $(find src -name '*.java')
java -cp out Main
```
