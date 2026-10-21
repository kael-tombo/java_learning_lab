# Challenge: Concurrent Skip List

Implement a lock-free concurrent skip list supporting:
1. Thread-safe insert, delete, search
2. Fine-grained locking per node level
3. No global locks
4. Linearizability guarantees

## Constraints
- 16 concurrent threads
- 10^6 operations per second throughput
- No deadlocks
