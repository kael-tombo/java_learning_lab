# Database Design Flashcards

## Multi-Tenancy

**Q: What are the four multi-tenant database patterns?**
**A:** 1) Shared DB/Shared Schema, 2) Shared DB/Separate Schemas, 3) Separate Databases, 4) Hybrid/Tiered

**Q: When does the hybrid model shine?**
**A:** Many small tenants + few large tenants. Small share resources; large get isolation.

**Q: What component routes queries in a multi-tenant system?**
**A:** Query proxy/router — extracts tenant_id, consults shard map, forwards to correct shard.

**Q: What is a "noisy neighbor" problem?**
**A:** One tenant's heavy load degrades performance for others sharing the same resources.

---

## Sharding

**Q: Range vs Hash sharding — key difference?**
**A:** Range preserves order (good for range scans); Hash distributes uniformly (good for write balance).

**Q: What is the resharding problem with hash sharding?**
**A:** `hash % N` changes when N changes → all keys potentially remap.

**Q: How does consistent hashing solve resharding?**
**A:** Maps keys and nodes to a ring; only keys near the failed/added node move (~1/N fraction).

**Q: What are virtual nodes (vnodes)?**
**A:** Multiple ring positions per physical node. Improves load balance and reduces skew.

**Q: Directory-based sharding — pros/cons?**
**A:** Pros: Flexible, easy rebalance. Cons: Metadata service is SPOF; extra lookup hop.

---

## Replication

**Q: Sync vs Async replication — tradeoff?**
**A:** Sync = strong consistency, higher latency, writes block on follower failure. Async = low latency, potential data loss.

**Q: Semi-synchronous replication?**
**A:** Leader waits for at least 1 follower ack (not all). Balance of durability and latency.

**Q: Multi-leader conflict resolution strategies?**
**A:** Last-write-wins (timestamp), CRDTs (mergeable types), application-specific logic, vector clocks.

**Q: Leaderless (Dynamo) — quorum condition for strong consistency?**
**A:** `W + R > N` where W=write quorum, R=read quorum, N=replication factor.

**Q: What is hinted handoff?**
**A:** Temporarily store writes for unreachable node; replay when it recovers.

**Q: Anti-entropy / Merkle trees?**
**A:** Background repair: compare subtree hashes to detect and sync divergent data.

---

## Distributed Transactions

**Q: 2PC phases?**
**A:** 1) Prepare (participants promise to commit), 2) Commit/Abort (coordinator decides).

**Q: Why does 2PC block?**
**A:** Participants hold locks after "prepared" until coordinator decides. If coordinator fails, they wait indefinitely.

**Q: Saga pattern — two coordination styles?**
**A:** Choreography (event-driven, decentralized) vs Orchestration (central coordinator directs flow).

**Q: What is a compensating transaction?**
**A:** Inverse operation to undo a step (e.g., `refund()` compensates `charge()`).

**Q: Calvin/Spanner approach — key idea?**
**A:** Deterministic transaction ordering via consensus (Paxos/Raft) + synchronized clocks (TrueTime) or pre-sequencing.

---

## Consistency & PACELC

**Q: Linearizability vs Sequential consistency?**
**A:** Linearizability respects **real-time** order; Sequential only respects **program** order per process.

**Q: Causal consistency — what metadata is needed?**
**A:** Vector clocks or dependency tracking (causal history).

**Q: PACELC extends CAP how?**
**A:** Adds the **Else** case: **E**lse (no partition) → tradeoff **L**atency vs **C**onsistency.

**Q: Classify: PA/EL, PC/EC, PA/EC, PC/EL**
**A:** 
- PA/EL: DynamoDB (available in partition, low latency else)
- PC/EC: Spanner, MongoDB (consistent in partition, consistent else)
- PA/EC: Cassandra (available in partition, consistent else)
- PC/EL: Rare (consistent in partition, low latency else — contradictory)

**Q: Read-your-writes — why does it matter for UX?**
**A:** User sees their own write immediately. Without it, "save then view" shows stale data → confusion.

---

## Schema Evolution

**Q: Backward vs Forward compatibility?**
**A:** Backward: new code reads old data. Forward: old code reads new data.

**Q: Safe changes for backward compatibility?**
**A:** Add optional field, add default value, add enum value.

**Q: Unsafe changes?**
**A:** Remove field, change type, rename field, make optional required.

**Q: Expand-Migrate-Contract pattern?**
**A:** 1) Expand schema (add), 2) Migrate data (dual-write/backfill), 3) Contract (remove old).

---

## Mathematical Foundations

**Q: Quorum formula for strong consistency?**
**A:** `W + R > N`

**Q: With N=5, what W,R gives strongest consistency?**
**A:** W=3, R=3 (majority both sides) or W=5, R=1 (write-all) etc.

**Q: Availability vs Consistency in quorum?**
**A:** Higher W/R = more consistency, less availability (need more nodes up).

**Q: Consistent hashing load balance with k vnodes?**
**A:** Variance ~ O(log N) with k vnodes per node; more vnodes = better balance.