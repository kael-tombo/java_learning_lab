# Debugging: Query Optimization

## Common Issues and Solutions

### Issue 1: Data Skew

**Symptoms:**
- One node has significantly more data than others
- Queries to a specific node are consistently slow
- Storage on one node is near capacity

**Root Causes:**
- Poor routing key selection (low cardinality)
- Monotonically increasing keys without hashing
- Uneven data distribution inherent in the dataset

**Diagnosis:**
`java
for (NodeStats stats : manager.getAllStats().values()) {
    System.out.printf(\"Node %s: size=%d, ops=%d%n\",
        stats.getNodeId(), stats.getDataSize(), stats.getQueryCount());
}
double skew = manager.getSkewFactor();
System.out.printf(\"Skew factor: %.2f (target: < 0.2)%n\", skew);
`

**Resolution:**
1. Rebalance with consistent hashing
2. Change routing key to higher cardinality attribute
3. Use composite routing key for better distribution

### Issue 2: Cross-Node Query Timeouts

**Symptoms:**
- Queries without routing key are very slow or timeout
- High CPU on all nodes simultaneously

**Diagnosis:**
`java
router.enableQueryLogging(true);
router.onQueryComplete(q -> {
    if (q.getLatencyMs() > threshold) {
        System.out.printf(\"Slow query: %s (nodes: %s, latency: %dms)%n\",
            q.getQuery(), q.getAffectedNodes(), q.getLatencyMs());
    }
});
`

**Resolution:**
1. Add covering indexes on queried columns
2. Implement materialized views
3. Cache cross-node query results
4. Denormalize to reduce cross-node needs

### Issue 3: Connection Pool Exhaustion

**Symptoms:**
- Application fails with \"Connection pool exhausted\" errors
- Intermittent timeouts

**Diagnosis:**
`java
for (String node : manager.getAllStats().keySet()) {
    PoolStats pool = pools.get(node).getStats();
    System.out.printf(\"Node %s: active=%d, idle=%d, pending=%d%n\",
        node, pool.getActive(), pool.getIdle(), pool.getPending());
}
`

**Resolution:**
1. Fix connection leaks
2. Increase pool size
3. Add connection timeout
4. Implement circuit breaker

### Issue 4: Split-Brain

**Symptoms:**
- Data inconsistencies between nodes
- Conflicting writes to the same key

**Diagnosis:**
`java
for (String node : manager.getAllStats().keySet()) {
    boolean healthy = healthChecker.isHealthy(node);
    long hb = healthChecker.getLastHeartbeat(node);
    System.out.printf(\"Node %s: healthy=%b, heartbeat=%dms ago%n\",
        node, healthy, System.currentTimeMillis() - hb);
}
`

**Resolution:**
1. Implement lease-based fencing
2. Use majority quorum for writes
3. Add network redundancy

### Issue 5: Rebalancing Failures

**Symptoms:**
- Rebalance gets stuck or takes too long
- Increased latency during rebalance

**Resolution:**
1. Throttle rebalance during peak hours
2. Reserve headroom on each node
3. Implement checkpoint/resume for rebalance
4. Verify data integrity after rebalance

### Debugging Tools

| Tool | Purpose |
|------|---------|
| JMX Metrics | Monitor runtime statistics |
| Distributed Tracing | Track cross-node operations |
| Query Logging | Capture all executed queries |
| Health Checks | Monitor node availability |
| Chaos Engineering | Test failure scenarios |

### Troubleshooting Flowchart
1. Is the issue specific to one node or all?
   - One node → Check that node's health and resources
   - All nodes → Check routing layer and upstream dependencies
2. Performance or correctness?
   - Performance → Check latency metrics, identify bottlenecks
   - Correctness → Check consistency guarantees
3. Ongoing or intermittent?
   - Ongoing → Check configuration, recent changes
   - Intermittent → Look for patterns
