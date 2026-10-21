# Distributed Locks - Interview Preparation

> Key interview questions about distributed lock implementations.

---

## Core Interview Questions

### Q1: What is the difference between optimistic and pessimistic locking?
**Answer**: Optimistic: assume no conflict, validate at commit (CAS, conditional writes). Better for low contention. Pessimistic: acquire lock, prevent others from modifying. Better for high contention. Distributed systems often use optimistic locking (DynamoDB conditional writes) due to network overhead.

### Q2: How does Redis Redlock work and what are its criticisms?
**Answer**: Redlock: acquire lock on majority (N/2+1) of N Redis nodes. Set key with TTL. If majority acquired within timeout, lock held. Criticisms: relies on synchronized clocks (impossible), no fencing tokens, network delays can break safety, Martin Kleppmann's analysis shows it's not safe.

### Q3: What is a "leader lease" and how does it differ from a lock?
**Answer**: Leader lease: time-bound leadership assignment. Holder is guaranteed leader for lease duration. Unlike locks (mutual exclusion), leases include time bound. Used in Raft: leader maintains lease via periodic heartbeats. If lease expires, new leader can be elected.

### Q4: How do you implement distributed locks using a database?
**Answer**: PostgreSQL advisory locks (pg_advisory_lock), MySQL GET_LOCK(), DynamoDB conditional writes (attribute_not_exists on lock item), ZooKeeper ephemeral sequential zNodes. Database locks are simpler but lower throughput than dedicated lock services.

### Q5: What is the "split-brain" problem in distributed locking?
**Answer**: Two nodes simultaneously believe they hold the same lock. Caused by network partitions, GC pauses, clock skew. Prevention: fencing tokens, lease-based locks with bounded clock drift, consensus-based lock services (ZooKeeper, etcd).

## Company-Specific Focus

| Company | Locking Focus |
|---------|--------------|
| Google | "Chubby lock service for GFS/Bigtable" |
| Amazon | "DynamoDB conditional writes as locks" |
| Redis | "Redlock vs ZooKeeper - safety comparison" |
| Apache | "Curator recipes for ZooKeeper locking" |

## LeetCode Connections

| Problem | # | Locking Concept |
|---------|---|----------------|
| The Dining Philosophers | 1226 | Deadlock prevention |
| Print FooBar Alternately | 1115 | Mutex with ordering |
| Print Zero Even Odd | 1116 | State machine lock |
| H2O Generation | 1117 | Barrier synchronization |

## System Design Connections

- **Design a Distributed Task Executor**: Lock tasks to prevent double execution
- **Design a Leader Election System**: Lease-based lock for leader
- **Design a Resource Manager**: Distributed lock for resource access
- **Design a Rate Limiter**: Lock for atomic counter updates

> **Key Insight**: Understand the Redlock controversy. Discuss fencing tokens as the defense against stale lock holders.