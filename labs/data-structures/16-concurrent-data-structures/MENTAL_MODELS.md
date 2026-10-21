# Mental Models for Concurrent Data Structures

## 1. The Traffic Intersection Model

- Lock-based: Traffic light (one direction goes, others wait)
- Lock-free: Roundabout (cars yield but never fully stop)
- CAS: Like checking if the parking spot is still empty before backing in

## 2. The Optimistic vs Pessimistic Model

- Pessimistic (lock-based): Assume collision will happen, prevent it
- Optimistic (lock-free): Assume collision won't happen, detect and retry

## 3. The Atomic Transaction Model

Each CAS operation is like a mini database transaction: it reads, modifies, and writes atomically. If another thread interfered, the transaction aborts and retries.
