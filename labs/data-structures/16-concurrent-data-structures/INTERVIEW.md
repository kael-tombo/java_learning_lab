# Interview Questions: Concurrent Data Structures

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| (No dedicated LeetCode problems — system design focus) | — | Google, Meta, Amazon, Microsoft, Oracle | Thread-safe design / lock-free |

## NeetCode Reference
Not in NeetCode. Concurrent data structures are primarily system design interview topics.

## Company-Specific Questions

### Google
- Design a thread-safe LRU cache — compare synchronized, ReentrantLock, and ConcurrentHashMap approaches
- How does ConcurrentHashMap achieve high concurrency? Explain the internal segmentation (Java 7) and CAS + bins (Java 8+)
- Design a lock-free bounded queue for a producer-consumer pattern (ring buffer with CAS)
- What is the ABA problem in lock-free data structures and how do you solve it?

### Microsoft
- Compare synchronized blocks, ReentrantLock, ReadWriteLock, and StampedLock — when to use each
- Implement a thread-safe stack using CAS (Treiber's stack algorithm)
- How does CopyOnWriteArrayList work and when is it appropriate?
- Design a concurrent hash map from scratch without using Java's concurrent utilities

### Meta
- Design a concurrent work-stealing queue (how ForkJoinPool works internally)
- How would you implement a scalable counter using LongAdder (striped counter pattern)?
- What is false sharing and how does padding (Contended annotation) prevent it?
- Design a thread-safe bounded buffer with blocking operations

### Amazon
- Design a distributed counter for tracking product views (dynamo-style CRDT counters)
- How would you implement a concurrent key-value store for high throughput?
- What is optimistic locking and how does CAS compare to pessimistic locking?

### Apple
- How does Grand Central Dispatch (GCD) use queues for concurrency? Compare with Java's ExecutorService
- Design a lock-free linked list using Harris's algorithm (logical deletion with mark bits)
- What memory ordering guarantees does volatile provide in Java?

### Oracle
- Explain the `java.util.concurrent` package hierarchy — which classes solve which problems?
- How does `ForkJoinPool` differ from `ThreadPoolExecutor`? When would you use each?
- What is the difference between `CountDownLatch`, `CyclicBarrier`, and `Phaser`?
- How does `CompletableFuture` enable asynchronous programming without explicit thread management?

## Real Production Scenarios

- **Scenario 1: Web Server Request Processing** — A web server uses a thread pool (`ThreadPoolExecutor`) with a `ConcurrentHashMap` of session data. Each request handler updates session state. Writes use `ConcurrentHashMap.replace()` (CAS). Session expiration uses a scheduled executor with a delay queue.

- **Scenario 2: Real-Time Trading System** — A trading platform processes thousands of orders per second using lock-free data structures (`ConcurrentLinkedDeque`, `AtomicLong` for sequence numbers, `LongAdder` for latency histograms). The core matching engine is single-threaded (queue-per-core pattern) to avoid locks entirely.

- **Scenario 3: Log Aggregation Service** — A distributed logging service collects logs from many producers into a `LinkedBlockingQueue`. A set of consumer threads batch-processes logs and writes to disk. The bounded queue provides backpressure — producers block when the queue is full, preventing OOM.

## Interview Tips

- Time varies by operation: CAS is O(1) but retries on contention; blocking queue put/take are O(1) in best case; ConcurrentHashMap get is O(1) average (lock-free)
- Space: thread-safe structures add overhead: ConcurrentHashMap has more segments/bins, CopyOnWriteArrayList duplicates on write
- Common patterns: CAS retry loop, read-write lock for read-heavy workloads, striped locking to reduce contention
- Always distinguish: thread-safe ≠ lock-free. Thread-safe can use locks; lock-free guarantees progress by at least one thread
- The `volatile` keyword guarantees visibility but not atomicity (except for long/double)
- `AtomicInteger`, `AtomicLong`, `AtomicReference` — CAS-based atomic updates for single variables

## Java-Specific Considerations

- `ConcurrentHashMap<K,V>` — CAS-based bin updates (Java 8+), lock-free reads, internal `TreeNode` for heavily collided bins
- `ConcurrentLinkedQueue<E>` / `ConcurrentLinkedDeque<E>` — lock-free, non-blocking, CAS-based, infinite (no capacity bound)
- `CopyOnWriteArrayList<E>` / `CopyOnWriteArraySet<E>` — thread-safe, snapshot iterator, full array copy on mutation — read-optimized
- `LinkedBlockingQueue<E>` — optionally bounded, lock-based (ReentrantLock on put and take), fair mode available
- `ArrayBlockingQueue<E>` — bounded, fixed-size array, single lock (or two-condition), optional fairness
- `PriorityBlockingQueue<E>` — unbounded, binary heap, ReentrantLock + Condition, growth cost O(n) on resize
- `SynchronousQueue<E>` — zero-capacity handoff, each put must wait for take (and vice versa)
- `LongAdder` (Java 8+) — striped counter, high throughput under contention, prefers `sum()` over `longValue()` for accuracy
- `ForkJoinPool` — work-stealing thread pool, `RecursiveTask`/`RecursiveAction` for divide-and-conquer parallelism
- `StampedLock` (Java 8+) — optimistic read lock (not blocking), supports conversion between read and write locks
- `Exchanger<V>` — rendezvous point for two threads to swap objects
- `Phaser` — flexible barrier, replaces `CountDownLatch` + `CyclicBarrier`, supports dynamic party registration
- `CompletableFuture<T>` — async computation with callbacks, combinable (thenApply, thenCompose, allOf, anyOf)
