# Solution: LRU Cache

## Data structure

```
HashMap<K, Node>  +  Doubly-linked list (sentinel head <-> tail)
```

- `HashMap` gives O(1) key lookup
- The list gives O(1) recency reordering and O(1) tail eviction
- Sentinel head/tail remove null-edge cases

## Core operations

- `get(k)`: lookup, move node to front, return value (or miss)
- `put(k, v)`: update or insert at front; while size > capacity, evict tail
- `evict()`: remove tail node and its map entry
- `moveToFront(node)`: unlink (handle prev/next) and prepend after sentinel

## Pitfalls solved here

- Unlinking must handle both neighbors; sentinel nodes simplify this
- A hit must not create a new node — update the existing one
- Eviction must remove the map entry too, or the map grows unbounded
- Capacity changes must drain the tail, not clear the map

## Run with

```bash
javac -d out $(find src -name '*.java')
java -cp out Main
```
