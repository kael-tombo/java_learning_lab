# Refactoring: Database Security

## Common Refactoring Patterns

### Pattern 1: Monolithic to Distributed

**Before:** Single database handling all operations.
`java
Connection conn = DriverManager.getConnection(jdbcUrl);
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(\"SELECT * FROM orders WHERE user_id = ?\");
`

**After:** Distributed with routing logic.
`java
Router router = new ConsistentHashRouter(nodes);
String target = router.getNode(userId);
Connection conn = nodeConnections.get(target);
stmt = conn.prepareStatement(\"SELECT * FROM orders WHERE user_id = ?\");
`

**Migration Strategy:**
1. Identify routing key and strategy
2. Create new node databases with same schema
3. Implement dual-write (write to both old and new)
4. Backfill historical data
5. Verify consistency
6. Cut over reads to new system
7. Decommission old database

### Pattern 2: Modulo to Consistent Hashing

**Before:** Simple modulo-based routing.
`java
int nodeId = key.hashCode() % numNodes;
`

**After:** Consistent hashing with virtual nodes.
`java
ConsistentHashRing ring = new ConsistentHashRing<>(vnodeCount);
String node = ring.getNode(key);
`

### Pattern 3: Client-Side to Proxy Routing

**Before:** Each application has embedded routing logic.
**After:** Centralized proxy handles routing transparently.

**Benefits:**
- Applications become database-agnostic
- Centralized routing configuration
- Easier to update routing strategy
- Better monitoring and debugging

### Pattern 4: Manual to Automatic Rebalancing

**Before:** Manual rebalancing with planned downtime.
**After:** Automatic continuous rebalancing with no downtime.

**Implementation:**
- Monitor skew factor continuously
- Trigger rebalance automatically at threshold
- Use consistent hashing for minimal data movement
- Throttle during business hours

### Code Smells to Detect
1. Hardcoded node mappings → Externalize to configuration
2. Cross-node joins in queries → Poor routing key choice
3. Distributed transactions everywhere → Consider saga pattern
4. Manual failover procedures → Automate with health checks
5. Hardcoded connection strings → Use service discovery
6. Missing correlation IDs → Add distributed tracing

### Refactoring Safety Checklist
- [ ] Comprehensive test suite before refactoring
- [ ] Feature flags for gradual rollout
- [ ] Shadow reads/writes for validation
- [ ] Performance benchmarks before/after
- [ ] Rollback plan documented
- [ ] Team communication plan
- [ ] Monitoring and alerting configured
- [ ] Runbook for common issues
