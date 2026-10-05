# VISION — Queue & Stack Deep

Vision: use ArrayDeque for LIFO/FIFO, PriorityQueue for dispatch by priority, blocking variants for producer-consumer — and avoid legacy Stack/Vector.

## Mental models
- Stack = last-in-first-out → think recursion, undo.
- Queue = first-in-first-out → think BFS, task FIFO.
- PriorityQueue = "always peek the min" → keep a heap.
- Blocking queue = a queue that knows how to sleep/wake producers.

## Decision table
| Workload | Pick |
|---|---|
| LIFO stack | ArrayDeque |
| FIFO queue | ArrayDeque |
| Priority dispatch | PriorityQueue |
| Bounded work queue | ArrayBlockingQueue |
| Unbounded MP/MC | ConcurrentLinkedQueue |
| Legacy | Stack/Vector (avoid) |

## Career path
- Shows up in: interviews, concurrency, schedulers.
- Story: "I model work as queues; I tune between ArrayDeque, PQ, and blocking queues."

## Done when
- [ ] Implement a balanced-parentheses check
- [ ] Explain why PriorityQueue iterator is unordered
- [ ] Mini + real-world projects shipped
