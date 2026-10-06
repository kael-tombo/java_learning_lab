# Mini Project: LRU Cache

## Goal

Build a small, self-contained LRU cache and demonstrate its behavior on a
short access trace.

## Scope

- `LruCache<K, V>` with capacity, get/put/evict, and size
- A demo `Main` that exercises a small key set and prints hit-rate and the
  eviction order
- No external dependencies — plain `java.util` collections are fine

## Suggested steps

1. Start from the reference structure (HashMap + doubly-linked list)
2. Implement get/put with move-to-front
3. Add eviction of the tail on overflow
4. Add hit/miss accounting and print a trace table

## Success criteria

- The trace table shows MRU at the front after every access
- Hit rate matches manual calculation
- Capacity is never exceeded

## Run with

```bash
javac -d out $(find src -name '*.java')
java -cp out Main
```
