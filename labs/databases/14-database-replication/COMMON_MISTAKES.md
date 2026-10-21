# Common Mistakes: Database Replication

## Mistake 1: Choosing the Wrong Routing Key
**Problem:** Selecting a key with low cardinality or highly skewed distribution.

**Example:** Routing by country_code when 70% of users are in the US.

**Consequences:** One node handles 70% of traffic (hotspot), storage imbalance, poor performance.

**Solution:** Use a composite key or hash the primary key directly.

## Mistake 2: Not Planning for Growth
**Problem:** Choosing node count based on current data without considering growth.

**Consequences:** Nodes exceed capacity sooner than expected, emergency rebalancing under pressure.

**Solution:** Plan for 2-3 years of growth. Target 60-70% utilization. Use consistent hashing.

## Mistake 3: Ignoring Query Patterns
**Problem:** Designing distribution without understanding how data will be queried.

**Consequences:** Most queries become expensive cross-node operations.

**Solution:** Analyze query patterns first. Route by the most common query key.

## Mistake 4: Over-Engineering Early
**Problem:** Implementing complex distribution when a simpler solution would work.

**Consequences:** Increased complexity, higher operational overhead.

**Solution:** Start with vertical scaling or read replicas. Distribute only when needed (data > 1TB or writes > 10K ops/sec).

## Mistake 5: Neglecting Monitoring
**Problem:** Not implementing proper monitoring before going live.

**Consequences:** Hotspots go undetected, no visibility into rebalancing progress.

**Solution:** Implement comprehensive monitoring before launch.

## Mistake 6: Weak Consistency Guarantees
**Problem:** Assuming strong consistency in an eventually consistent system.

**Consequences:** Read-after-write inconsistencies, conflicting updates.

**Solution:** Understand and document your consistency model.

## Mistake 7: Manual Failover
**Problem:** Requiring manual intervention when a node fails.

**Consequences:** Extended downtime, human error under stress.

**Solution:** Automate failover with health checks and consensus.

## Mistake 8: Ignoring Backup and Recovery
**Problem:** Not testing node-level backup and recovery.

**Consequences:** Incomplete backups, unable to recover individual nodes.

**Solution:** Backup each node independently. Test restore procedures regularly.

## Mistake 9: Synchronous Cross-Node Transactions
**Problem:** Using distributed transactions (2PC) for every cross-node operation.

**Consequences:** Blocking protocol, poor performance, reduced availability.

**Solution:** Use Saga pattern with compensating transactions. Minimize cross-node operations.

## Mistake 10: Hardcoding Configuration
**Problem:** Embedding topology in application code.

**Consequences:** Every change requires redeployment.

**Solution:** Externalize configuration to a metadata service. Implement hot-reload.
