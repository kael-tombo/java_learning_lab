# Architecture of Concurrent Data Structures

## Design Patterns

1. **Lock Striping**: Partition data, lock per partition
2. **Copy-on-Write**: Snapshot semantics for iteration
3. **Read-Write Lock**: Multiple readers, exclusive writer
4. **Lock-Free**: CAS-based, no blocking

## Integration

`
Application
  → Service Layer (thread-safe)
    → ConcurrentHashMap (cache)
    → ConcurrentLinkedQueue (work queue)
    → LockFreeStack (pool)
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# Exercises: Concurrent Data Structures

## Beginner
1. Implement thread-safe counter with AtomicInteger
2. Implement synchronized stack and benchmark
3. Use ConcurrentHashMap as a cache

## Intermediate
4. Implement Treiber lock-free stack
5. Implement Michael-Scott lock-free queue
6. Implement ConcurrentHashSet
7. Add backoff to CAS operations

## Advanced
8. Implement lock-free linked list
9. Implement elimination-diffraction stack
10. Benchmark lock-free vs lock-based
11. Implement read-write lock from primitives
