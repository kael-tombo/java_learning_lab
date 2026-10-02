# Database Design Quiz

## Questions

1. **Multi-tenancy**: A SaaS platform has 10,000 small tenants (< 1GB each) and 50 large tenants (> 100GB each). Which architecture pattern minimizes cost while providing isolation for large tenants?

2. **Sharding**: You shard by `tenant_id` using hash-based sharding (`hash(tenant_id) % N`). A large tenant grows and causes a hot shard. What are two strategies to handle this without full resharding?

3. **Replication**: In a leader-follower PostgreSQL cluster with synchronous replication to 1 follower, what happens if the follower crashes? How does this differ from asynchronous replication?

4. **CAP/PACELC**: Classify each system: (a) Cassandra with QUORUM reads/writes, (b) MongoDB with default write concern, (c) Google Spanner, (d) DynamoDB with strong consistency reads.

5. **Distributed Transactions**: Compare 2PC vs Saga for a cross-shard order placement (Payment + Inventory + Shipping services). When would you choose each?

6. **Consistency Models**: A user updates their profile, then immediately reads it. They see stale data. Which consistency guarantee is violated? What minimum model ensures this doesn't happen?

7. **Schema Evolution**: You need to rename a column `email` → `email_address` in a 10TB table with zero downtime. Outline the 3-phase migration steps.

8. **Quorum Math**: A 5-node cluster uses `W=3, R=2`. Is this strongly consistent? What is the maximum number of node failures it can tolerate for reads? For writes?

9. **Consistent Hashing**: With 100 virtual nodes per physical node and 10 physical nodes, a node fails. Approximately what fraction of keys move? How does this compare to modulo hashing (`hash % N`)?

10. **Real-world Trade-off**: Design a database for a global chat application (WhatsApp-scale). Messages must be delivered in order per conversation. Choose: (a) strong consistency globally, (b) causal consistency per conversation, (c) eventual consistency with vector clocks. Justify your choice with latency/availability numbers.

---

## Answers

1. **Hybrid/Tiered architecture**: Small tenants share database/schema (cost-effective), large tenants get dedicated databases (isolation). The query proxy routes based on tenant tier.

2. **Strategies**: (a) **Split the hot tenant**: Give the large tenant its own dedicated shard (move from shared to dedicated), update shard map only for that tenant. (b) **Virtual nodes in consistent hashing**: Add more virtual nodes for that tenant to spread its load across multiple physical shards.

3. **Synchronous**: Writer blocks until follower acknowledges. If follower crashes, writes **halt** (unavailable) until follower recovers or is removed from sync set. **Asynchronous**: Writer continues; follower catches up later. Risk: **data loss** if leader fails before replicating.

4. **Classifications**:
   - (a) Cassandra QUORUM: **PC/EC** (majority quorum = consistency; in partition, chooses C)
   - (b) MongoDB default (w:1): **PA/EC** (writes to primary only; in partition, may lose writes for A)
   - (c) Spanner: **PC/EC** (Paxos + TrueTime; always consistent, latency cost)
   - (d) DynamoDB strong read: **PC/EC** (quorum read; consistent but higher latency)

5. **2PC**: Strong consistency, blocking, coordinator SPOF. Use when: short transactions, few participants, need atomicity (e.g., financial ledger). **Saga**: Eventual consistency, non-blocking, compensating actions. Use when: long-running, many services, can tolerate temporary inconsistency (e.g., order orchestration).

6. **Violated**: Read-your-writes consistency. **Minimum model**: **Read-your-writes** (or causal consistency, which subsumes it). Linearizability also works but is stronger than needed.

7. **3-Phase Migration**:
   - **Expand**: Add `email_address` column, dual-write to both columns
   - **Migrate**: Backfill `email_address` from `email` (batch, online)
   - **Contract**: Switch reads to `email_address`, stop writing `email`, drop `email` column

8. **Strong consistency**: Yes, `W + R = 5 > N = 5`. **Read tolerance**: `N - R = 3` failures. **Write tolerance**: `N - W = 2` failures.

9. **Consistent hashing**: ~1/10 = **10%** of keys move (only keys mapped to failed node's virtual nodes). **Modulo hashing**: ~100% of keys remap (all `hash % 10` change to `hash % 9`).

10. **Choice: (b) Causal consistency per conversation**. 
    - **Why**: Per-conversation ordering is required (causal), not global ordering. Causal consistency provides this with lower latency than linearizability.
    - **Latency**: ~50-100ms cross-region vs 200-300ms for global linearizability (Paxos).
    - **Availability**: Survives partitions within conversation shards.
    - **Vector clocks** track conversation causality; no global clock needed.