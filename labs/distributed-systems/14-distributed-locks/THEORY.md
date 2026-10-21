# Theory of Distributed Locks

## 1. Why Distributed Locks?

In a single system, mutexes protect shared memory. In distributed systems, we need to protect shared resources (files, databases, services) across network boundaries.

## 2. Properties of Distributed Locks

- **Mutual exclusion**: Only one process holds the lock at a time
- **Deadlock freedom**: Locks are eventually released (even if holder crashes)
- **Fault tolerance**: System continues operating despite node failures
- **Reentrancy**: Same process can re-acquire its own lock
- **Fairness**: Locks granted in request order (or best-effort)

## 3. Redis Redlock Algorithm

Redlock acquires locks from N independent Redis nodes (typically 5):
1. Get current time
2. Acquire lock on all N nodes with short timeout
3. If acquired on majority (N/2 + 1) and total time < TTL, lock is held
4. Release lock on all nodes (even failed attempts)

### Concerns
- Relies on synchronized clocks
- Not safe under asynchronous networks
- Performance degrades with many nodes

## 4. ZooKeeper Locks

Using ephemeral sequential znodes:
1. Create ephemeral sequential znode under lock path
2. Get all children of lock path
3. If own znode is lowest sequence: lock acquired
4. Otherwise: watch next-lower znode and wait

### Properties
- No clock synchronization needed
- Fair (FIFO ordering)
- Crash-safe (ephemeral znodes auto-delete)

## 5. Lease-Based Locking

A lease grants a lock for a limited time period:
- Holder must renew before lease expires
- If holder crashes, lease expires automatically
- Provides bounded lock duration

## 6. Fencing Tokens

A fencing token is a monotonically increasing number:
- Each lock acquisition gets a unique token
- Resource side checks token validity
- Prevents stale lock holders from accessing resource

## 7. Common Problems

- **Split-brain**: Two processes both think they hold the lock
- **Clock skew**: Inconsistent timeouts across nodes
- **GC pauses**: Long garbage collections cause lease expiration
- **Network partitions**: Inability to communicate with lock service
