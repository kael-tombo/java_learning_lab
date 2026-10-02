# Database Design Exercises

## Exercise 1: Multi-Tenant Architecture Design (Design Task)

**Scenario**: Build a database layer for a B2B SaaS platform with:
- 50,000 small tenants (< 500MB each)
- 500 medium tenants (500MB - 50GB)
- 50 large tenants (> 50GB, up to 2TB)
- Requirements: SQL queries, ACID per tenant, horizontal scaling, < 10ms p99 latency

**Tasks**:
1. Draw the architecture diagram showing: query proxy, shard map, database tiers
2. Define the shard map data structure (tenant_id → shard_id, tier info)
3. Write the routing logic pseudocode for the proxy
4. Design the migration procedure for a tenant growing from medium → large tier
5. How do you enforce per-tenant resource limits (connections, QPS, storage)?

**Deliverable**: Architecture document + pseudocode + migration runbook

---

## Exercise 2: Sharding Strategy Comparison (Analysis Task)

**Given**: A `orders` table with 100TB, growing 10TB/month. Access patterns:
- 80% queries: `WHERE tenant_id = ? AND order_date > ?` (recent orders per tenant)
- 15% queries: `WHERE customer_id = ?` (cross-tenant customer lookup)
- 5% queries: Analytics scans over date ranges

**Compare three strategies**:
1. Hash sharding on `tenant_id`
2. Range sharding on `order_date` (monthly partitions)
3. Composite: Hash on `tenant_id`, sub-partition by `order_date`

For each, analyze:
- Write distribution / hot spots
- Query routing complexity
- Cross-shard query cost
- Resharding difficulty
- Best/worst case latency

**Deliverable**: Comparison table + recommendation with justification

---

## Exercise 3: Replication Topology Design (Design Task)

**Scenario**: Global e-commerce with 3 regions (US-East, EU-West, AP-Southeast). Requirements:
- Write latency < 50ms p99 in home region
- Read latency < 20ms p99 globally
- RPO = 0 (no data loss), RTO < 30s
- Survive single region outage

**Design a replication topology** using PostgreSQL. Specify:
- Leader placement per shard
- Sync/async configuration per replica
- Failover procedure (automated vs manual)
- How you handle split-brain prevention
- Read routing for low-latency global reads

**Bonus**: How would this change if using CockroachDB or Spanner?

---

## Exercise 4: Distributed Transaction Implementation (Code Task)

**Implement** a Saga orchestrator for cross-shard order placement:

```java
// OrderSagaOrchestrator.java
public class OrderSagaOrchestrator {
    // TODO: Implement
    // Steps: 1) Reserve Inventory, 2) Charge Payment, 3) Create Shipping Label
    // Compensations: Release Inventory, Refund Payment, Void Shipping
}
```

**Requirements**:
- Persist saga state (pending, completed, compensating, failed)
- Idempotent step execution (retry safe)
- Timeout handling for stuck steps
- Compensation ordering (reverse of execution)
- Observable: emit events for monitoring

**Failure Injection Tests**:
1. Payment service fails after inventory reserved → verify compensation runs
2. Network timeout on shipping → verify retry then compensate
3. Orchestrator crashes mid-saga → verify recovery on restart

---

## Exercise 5: Consistency Model Selection (Reasoning Task)

For each workload, choose the **minimum** consistency model and justify:

| Workload | Requirements | Your Choice | Why not stronger? | Why not weaker? |
|----------|--------------|-------------|-------------------|-----------------|
| Bank transfer | No double-spend, audit trail | | | |
| Shopping cart | Add/remove items, checkout | | | |
| Collaborative doc | Concurrent edits, merge | | | |
| Analytics dashboard | Approximate counts OK | | | |
| Inventory decrement | No oversell | | | |
| Social media feed | Eventual OK, ordering per user | | | |
| Leaderboard | Real-time ranking | | | |
| Config service | All nodes see same value | | | |

**Discussion**: Where does PACELC matter? Map each to PA/EC, PC/EC, PA/EL, PC/EL.

---

## Exercise 6: Schema Migration with Zero Downtime (Code + Operations Task)

**Scenario**: Rename column `user_id` → `account_id` in 50TB `events` table. Zero downtime required.

**Tasks**:
1. Write the **3-phase migration SQL/scripts** (Expand, Migrate, Contract)
2. Design the **dual-write application code** (Java) that writes to both columns
3. Plan the **backfill strategy**: batch size, throttling, progress tracking
4. Define **rollback procedure** for each phase
5. Create **monitoring queries** to verify consistency during migration

**Failure Injection**:
- Simulate: migration script crashes at 60% → resume from checkpoint
- Simulate: application bug writes wrong value to new column → detect & fix
- Simulate: replica lag causes stale reads during cutover → mitigation

---

## Exercise 7: Quorum Configuration Optimization (Math Task)

**Given**: 5-node cluster, network RTT = 2ms (same DC), 50ms (cross-region).
Workload: 70% reads, 30% writes. Target: p99 latency < 20ms, tolerate 1 node failure.

**Find optimal (W, R) for each deployment**:
1. Single DC (5 nodes, 2ms RTT)
2. Multi-region (2 nodes US, 2 EU, 1 AP; cross-region 50ms)

**Calculate**:
- Expected latency (assume quorum = slowest of W/R responses)
- Availability (probability of successful op with 1 random failure)
- Data loss risk on leader failure (async vs sync)

**Extension**: How does adding a 6th node (witness) change the math?

---

## Exercise 8: Consistent Hashing Implementation (Code Task)

**Implement** a consistent hashing ring with virtual nodes:

```java
public class ConsistentHashRing<T> {
    // TODO: Add node (with vnode count)
    // TODO: Remove node
    // TODO: Get node for key
    // TODO: Get N replicas for key (for replication)
}
```

**Requirements**:
- Configurable virtual nodes per physical node
- `getReplicas(key, n)` returns N distinct physical nodes
- Thread-safe
- Efficient: O(log V) lookup where V = total vnodes

**Test**:
1. Add 10 nodes × 100 vnodes, verify uniform distribution (χ² test)
2. Remove 1 node, measure key movement % (should be ~10%)
3. Add node, verify only ~10% keys move
4. Concurrent add/remove under load

---

## Exercise 9: Failure Injection & Chaos Testing (Experimental Task)

**Target**: A running distributed database cluster (Cassandra, MongoDB, or CockroachDB).

**Inject these failures** and observe behavior:
1. **Network partition**: Split cluster into two halves (iptables)
   - Verify: which side stays available? Data divergence?
2. **Leader kill**: Kill primary during write load
   - Measure: failover time, data loss (if any), client errors
3. **Slow disk**: Add 100ms latency to one node's disk
   - Observe: replication lag, quorum impact, client latency
4. **Clock skew**: Offset one node's clock by 5s (NTP manipulation)
   - Effect on: lease expiration, TTL, transaction timestamps
5. **Byzantine**: Node returns corrupted data
   - Detection: checksums, quorum reads, application-level validation

**Document**: For each, record: detection time, recovery time, data integrity, client impact.

---

## Exercise 10: Real-World Case Study (Research Task)

**Pick ONE** and write a 2-page analysis:
- **Discord**: How they scaled Cassandra for messages (billions/day)
- **Uber**: Schemaless (MySQL + sharding) for trips
- **Slack**: Vitess for MySQL sharding
- **Pinterest**: MySQL → sharded MySQL migration
- **Shopify**: Multi-tenant MySQL with per-tenant schemas
- **Figma**: CRDTs for real-time collaboration

**Structure**:
1. Scale metrics (data size, QPS, tenants)
2. Architecture diagram
3. Key technical decisions (sharding, replication, consistency)
4. Notable incidents & lessons
5. What you'd do differently

---

## Grading Rubric

| Exercise | Points | Criteria |
|----------|--------|----------|
| 1. Multi-tenant Design | 15 | Complete architecture, routing logic, migration plan |
| 2. Sharding Comparison | 10 | Thorough analysis, justified recommendation |
| 3. Replication Topology | 15 | Meets all requirements, handles failures |
| 4. Saga Implementation | 20 | Correct, idempotent, observable, tested |
| 5. Consistency Selection | 10 | Accurate models, clear reasoning |
| 6. Schema Migration | 15 | Zero-downtime plan, rollback, monitoring |
| 7. Quorum Math | 10 | Correct calculations, explained tradeoffs |
| 8. Consistent Hashing | 15 | Working implementation, tested |
| 9. Chaos Testing | 15 | Executed, documented, insights |
| 10. Case Study | 10 | Depth, accuracy, critical analysis |

**Total**: 135 points