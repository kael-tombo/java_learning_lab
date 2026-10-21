# Internals — Time Ordering

## Lamport Clock
- 4 bytes int counter (or 8 bytes long)
- AtomicInteger for lock-free increment
- LOCK CMPXCHG on x86

## Vector Clock (Array)
- int[] with bounds checking
- System.arraycopy() for cloning
- Cache-friendly sequential access

## Vector Clock (Map)
- HashMap<Integer,Integer> for sparse storage
- ConcurrentHashMap for thread safety
- Higher per-op cost, lower memory for large clusters

## HLC State Machine
- State: (physicalTime, logicalCounter)
- tick(): compare physical time, increment or reset
- receive(): triple-max of physical times, logical tie-breaking

## Causal Broadcast Buffer
- PriorityQueue ordered by vector clock
- Delivery condition: V[j] == local[j]+1 AND all k: V[k] <= local[k]
- Periodic cleanup of stale messages
