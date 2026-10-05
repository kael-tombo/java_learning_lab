# LRU Cache (HashMap + Doubly-Linked List) - Lab

*O(1) get/put with eviction.*

Core idea: An LRU cache pairs a HashMap (key->node) with a doubly-linked list in recency order; every hit relocates the node to the front, eviction pops the tail.

## Operations

| Operation | Contract | Cost |
|---|---|---|
| `get(k)` | lookup + move-to-front | O(1) |
| `put(k,v)` | insert/update + move-to-front | O(1) |
| `evict()` | remove tail node + map entry | O(1) |
| `moveToFront(node)` | unlink + prepend (sentinel heads) | O(1) |
| `resize(cap)` | drain tail while over capacity | O(1) amort. |
| `hitRate()` | hits/(hits+misses) | O(1) |

## Invariants

- map size == list size always
- head.next is MRU, tail.prev is LRU
- every successful access makes the key MRU
- capacity is never exceeded after put returns

## Repo map

- `THEORY.md` - operations, invariants, complexity
- `EXERCISES.md` - implement from scratch + traces
- `CODE_DEEP_DIVE.md` - Java implementation + pitfalls
- `MINI_PROJECT.md` / `REAL_WORLD_PROJECT.md` - build + production use-case

## Run (Java 17+)

```bash
javac -d out $(find src -name '*.java')
java -cp out Main
```

## Success criteria

- get/put proven O(1); eviction order correct under fuzz.
- Hit-rate measured on a realistic trace; can state when LRU loses to LFU/FIFO.
