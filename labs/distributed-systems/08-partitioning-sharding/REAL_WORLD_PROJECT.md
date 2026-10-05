# Partitioning and Sharding - Real World Project

## Project: Sharding a Growing Multi-Tenant Application Table

### Objective
Take a single table that has outgrown one node, choose a defensible shard key, implement
online repartitioning with no downtime, and establish the operational limits that will govern
all future growth.

### Why This Is a Real Problem
Most "we need to shard" moments are actually "one tenant is too big" or "one index is too
hot." Sharding on the wrong axis converts a solvable problem into a rewrite, and doing it
online while writes continue is where projects stall.

### Architecture Overview
```
  App ─▶ Shard Router (consistent hash ring + directory)
            │
            ├── shard-0  ─▶ partition A1, A2 (replica pair)
            ├── shard-1  ─▶ partition B1, B2
            └── shard-N  ─▶ ...
     Directory: shard id → {physical node, state, key range}
```

### Phase 1: Prove You Need It (Week 1)
1. Measure per-tenant row counts, query rates, and storage size
2. Identify the actual constraint: storage, memory, write throughput, or index depth
3. Quantify the ceiling: at current growth, when does the node stop?
4. Test whether the constraint is one hot tenant — if so, partition-per-tenant solves it and
   co-location is not required

### Phase 2: Choose the Shard Key (Week 2)
1. List every query the application runs and the column each filters on
2. Choose the shard key that satisfies the most queries with one-shard routing; document
   which queries become scatter-gather and their measured cost
3. Verify the key distribution: no tenant above ~5% of data or 10% of QPS
4. Confirm the key is immutable — a mutable shard key means a rewrite, not a rebalance
5. Write the decision down, including the option you rejected and why

### Phase 3: Build the Directory and Router (Week 3)
1. Directory entry: `shardId → {node, state, keyRange, rowCount, version}`
2. Router caches the directory and invalidates on version change
3. States: `ACTIVE`, `DRAINING`, `READ_ONLY`, `OFFLINE` — the state machine is what makes
   online moves safe
4. Fallback: a cache miss or unknown shard must fail loudly, never silently route wrong

### Phase 4: Online Repartitioning (Week 4)
```java
void moveShard(int shardId, Node target) {
    dir.transition(shardId, ACTIVE, DRAINING);       // stop new writes to it
    var rows = scanShard(shardId);                   // chunked, resumable by key
    for (var chunk : chunks(rows, 5000)) {
        copyWithCheckpoint(chunk);                   // record progress durably
        backfillDelta(shardId, sinceCheckpoint());    // catch writes that raced
    }
    dir.transition(shardId, DRAINING, READ_ONLY);    // final sync, verify row counts
    dir.bind(shardId, target, ACTIVE);               // flip the routing atomically
    decommission(sourceShard);
}
```
1. Chunk by primary key range so restarts resume, not restart
2. Backfill deltas after the initial copy — the race is where rows go missing
3. Verify counts and checksums before flipping to READ_ONLY
4. Flip routing atomically; then delete the old copy only after a TTL and a checksum match

### Phase 5: Operate (Week 5+)
1. Dashboard: per-shard rows, QPS, p99, bytes; skew ratio
2. Alerts: skew ratio above 1.5, any shard above 60% of node capacity, rebalance failures
3. Runbook: "add a shard" and "hot shard" with the actual commands
4. Capacity model: current rows/GB per shard, growth rate, months to next split

### Deliverables
1. Shard-key decision record with rejected alternatives and measured query costs
2. Directory, router, and the online move implementation with checkpoints
3. Migration run with row counts and checksums verified per shard
4. Skew dashboard, capacity model, and the two runbooks

### Success Criteria
- Migration completed with zero downtime and zero lost rows, verified by checksum
- No query exceeds its pre-migration p99 by more than 10%
- Skew ratio stays under 1.5 as tenants are added
- A second shard split is rehearsed end to end before it is needed

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Amazon DynamoDB Developer Guide, "Core components of Amazon DynamoDB" —
  https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html
  Use for: partition keys, the hot-partition problem, and adaptive capacity as the reference
  model for shard-key distribution. Useful when arguing for a managed store over
  hand-rolled sharding for the same workload.
- Kubernetes Documentation, "Workload Management: StatefulSets" —
  https://kubernetes.io/docs/concepts/workloads/controllers/
  Use for: stable network identities and ordered rollout per shard — the practical mechanism
  behind keeping a shard bound to a stable endpoint during online repartitioning.

### Estimated Time
7-8 weeks part-time