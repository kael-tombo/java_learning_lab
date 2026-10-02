# Database Design Theory

## Multi-Tenant Database Architectures

### Patterns

| Pattern | Description | Pros | Cons |
|---------|-------------|------|------|
| **Shared Database, Shared Schema** | Single DB, all tenants share tables with tenant_id column | Low resource usage, simple operations | Noisy neighbor, limited customization |
| **Shared Database, Separate Schemas** | Single DB instance, each tenant has own schema | Better isolation, some customization | Schema management complexity |
| **Separate Databases** | Each tenant gets dedicated DB instance | Full isolation, customizable | High resource overhead, ops complexity |
| **Hybrid (Tiered)** | Small tenants share, large tenants get dedicated | Cost-effective, scales with tenant | Routing complexity |

### Routing Layer
A **query proxy** parses tenant_id from connection/query and routes to appropriate shard:
```
Client → Proxy (tenant_id extraction) → Shard Map → Target DB
```

**Shard Map**: Configuration store (etcd, ZooKeeper, Consul) mapping tenant_id → shard_id.

---

## Sharding Strategies

### 1. Range-Based Sharding
- Shard by key ranges (e.g., tenant_id 1-1000 → shard 1)
- **Pros**: Efficient range queries, ordered data
- **Cons**: Hot spots on sequential writes, rebalancing difficult

### 2. Hash-Based Sharding
- `shard_id = hash(key) % N`
- **Pros**: Uniform distribution, simple
- **Cons**: No range queries, resharding requires data movement

### 3. Directory-Based Sharding
- Lookup service maps key → shard
- **Pros**: Flexible, supports custom logic, easy rebalancing
- **Cons**: Additional lookup latency, metadata service is SPOF

### 4. Consistent Hashing
- Ring-based mapping with virtual nodes
- **Pros**: Minimal data movement on node changes
- **Cons**: More complex, requires virtual nodes for balance

---

## Replication Patterns

### Leader-Follower (Primary-Backup)
```
Writes → Leader → Replicates to Followers
Reads  → Followers (eventual) or Leader (strong)
```
- **Sync**: Strong consistency, higher latency
- **Async**: Lower latency, potential data loss on failover
- **Semi-sync**: Balance (e.g., MySQL semi-sync, PostgreSQL sync rep)

### Multi-Leader
- Multiple nodes accept writes
- **Conflict resolution**: Last-write-wins, CRDTs, application logic
- **Use case**: Multi-region, offline-first

### Leaderless (Dynamo-style)
- Quorum reads/writes: `W + R > N`
- **Hinted handoff** for temporary failures
- **Anti-entropy** (Merkle trees) for repair

---

## Distributed Transactions

### Two-Phase Commit (2PC)
```
Phase 1 (Prepare): Coordinator asks all participants to prepare
Phase 2 (Commit): If all ready, coordinator sends commit; else abort
```
- **Blocking**: Participants hold locks until coordinator decides
- **Single point of failure**: Coordinator

### Three-Phase Commit (3PC)
- Adds "pre-commit" phase to reduce blocking
- Still not truly non-blocking in async networks

### Saga Pattern
- Sequence of local transactions with compensating actions
- **Choreography**: Events trigger next step
- **Orchestration**: Central coordinator directs flow
- **Trade-off**: Eventual consistency, no isolation

### Calvin/Spanner Approach
- Deterministic ordering via Paxos/Raft + TrueTime
- **Spanner**: Paxos + TrueTime (bounded clock uncertainty)
- **Calvin**: Pre-processed deterministic transaction log

---

## Consistency Models in Practice

| Model | Guarantees | Latency | Use Case |
|-------|------------|---------|----------|
| **Linearizable** | Real-time order, single copy illusion | High | Banking, inventory |
| **Sequential** | Program order per process | Medium | Most apps |
| **Causal** | Cause-effect preserved | Medium | Collaboration |
| **Read Your Writes** | Own writes visible | Low | User-facing |
| **Monotonic Reads** | Time doesn't go backward | Low | Cache layers |
| **Eventual** | Converges if no new writes | Lowest | Analytics, feeds |

---

## PACELC Theorem
Extends CAP:
- **P**artition → tradeoff between **A**vailability and **C**onsistency (CAP)
- **E**lse (no partition) → tradeoff between **L**atency and **C**onsistency

| System | PACELC Classification |
|--------|----------------------|
| DynamoDB | PA/EC |
| Cassandra | PA/EL |
| MongoDB | PC/EC |
| Spanner | PC/EC (with TrueTime) |
| Raft-based | PC/EC |

---

## Schema Evolution

### Backward Compatibility
- New schema reads old data
- Add optional fields, never remove required

### Forward Compatibility
- Old schema reads new data
- Ignore unknown fields

### Zero-Downtime Migration Pattern
1. **Expand**: Add new column/table (compatible)
2. **Migrate**: Backfill data (dual-write)
3. **Contract**: Remove old column (after switch)

---

## Key Mathematical Foundations

### Quorum Calculations
```
N = total replicas
W = write quorum
R = read quorum
Strong consistency: W + R > N
Availability: W < N, R < N
Latency: minimize max(W, R)
```

### Consistent Hashing
```
Hash space: 0 to 2^m - 1
Virtual nodes per physical node: k
Expected load balance: O(log N) variance
```

### CAP/PACELC Formalization
```
CAP: In presence of P, choose A or C
PACELC: if P then (A vs C) else (L vs C)
```

---

## References
- "Designing Data-Intensive Applications" - Martin Kleppmann
- "Database Internals" - Alex Petrov
- "The CALVIN Paper" - Thomson et al.
- "Spanner: Google's Globally-Distributed Database" - Corbett et al.
- "PACELC Theorem" - Daniel Abadi