# Theory: Concurrent Data Structures

## Fundamentals

Concurrent data structures allow multiple threads to access and modify shared data safely. They are essential for multi-core programming. There are two main approaches: lock-based and lock-free.

## Lock-Free vs Lock-Based

### Lock-Based
- Use mutexes, semaphores, read-write locks
- Simple to implement correctly
- Risk of deadlock, priority inversion
- Performance degrades with contention

### Lock-Free
- Use CAS (Compare-And-Swap) operations
- No blocking, guaranteed progress
- Harder to implement correctly
- Handle the ABA problem
- Better scalability

## CAS (Compare-And-Swap)
An atomic instruction: if current == expected, set current = newValue and return true; otherwise return false.

## Java Concurrent Utilities

- ConcurrentHashMap: Lock-striped hash table
- CopyOnWriteArrayList: Snapshot iterator, thread-safe
- ConcurrentLinkedQueue: Lock-free FIFO queue
- AtomicInteger/Long/Reference: CAS-based atomic variables
