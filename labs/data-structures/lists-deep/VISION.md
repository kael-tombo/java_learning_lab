# VISION — Lists Deep

Vision: pick the right list/deque for the workload — usually ArrayList or ArrayDeque, rarely LinkedList, almost never Vector.

## Mental models
- ArrayList = growable array: O(1) random access, O(n) middle insert.
- LinkedList = chain of nodes: O(1) only at the ends with a pointer at hand.
- Vector = synchronized ArrayList, legacy.
- ArrayDeque = ring buffer: the modern default for stack/queue roles.
- Iteration with removal: the linked-list trap — only iteration with iterator.remove is safe.

## Decision table
| Workload | Pick |
|---|---|
| Most lists | ArrayList |
| Stack/queue/deque | ArrayDeque |
| Lots of middle ops | usually still ArrayList; measure first |
| Concurrent readers, rare writes | CopyOnWriteArrayList |
| LRU | LinkedHashMap |
| Legacy thread-safe | Vector (avoid) |

## Career path
- Shows up in: interviews, API design, performance debugging.
- Story: "I know why LinkedList loses on cache and allocation, and I default to ArrayDeque."

## Done when
- [ ] Trace amortized add
- [ ] Implement a reverse + Floyd cycle check
- [ ] Mini + real-world projects shipped
