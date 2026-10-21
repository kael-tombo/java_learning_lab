## Front: What is a lock-free data structure?
Back: A concurrent structure guaranteeing system-wide progress without locks.

## Front: How does CAS work?
Back: Atomically compares memory to expected value, swaps if equal.

## Front: What is the ABA problem?
Back: Pointer changes A→B→A, CAS succeeds incorrectly. Solved with version counters.

## Front: What is ConcurrentHashMap?
Back: Thread-safe hash map using CAS and lock striping for high concurrency.
