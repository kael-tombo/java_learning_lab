# Visual Guide — Time Ordering

## Lamport Clock Flow
`
P1: [1] tick -> [2] send ---> P2: max(0,2)+1 = [3]
P2: [1] tick -> [2] send ---> P3: max(3,2)+1 = [4]
`

## Happens-Before
`
P1: e1 --m1--> e2 --m2--> e3
             |        |
             v        v
P2: e4 ----------> e5 --> e6
`

## Vector Clock Convergence
`
P1: [3,2,1] --send--> P2: [2,4,1] -> P2 merges: [3,4,1]
P1: [3,4,1] <--ack--- P2: [3,4,1]
`
"@

W "INTERNALS.md" @"
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
