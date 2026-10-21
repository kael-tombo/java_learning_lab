# Exercises: Database Replication

## Beginner Level

### Exercise 1: Basic Implementation
Implement a basic version of the core routing algorithm without optimizations.

**Requirements:**
- Single-threaded implementation
- Support for 3-5 nodes
- Basic hash function (use Java's hashCode())
- Unit tests verifying correctness

### Exercise 2: Configuration
Add configuration support using Java Properties or YAML.

**Requirements:**
- Read node list from configuration
- Configurable parameters
- Validation of configuration values

### Exercise 3: Simple Monitoring
Add a metrics collection layer.

**Requirements:**
- Track operation counts per node
- Track latency per operation
- Expose metrics through a simple API

## Intermediate Level

### Exercise 4: Multi-threading
Make the implementation thread-safe.

**Requirements:**
- Use ReadWriteLock for concurrent access
- No data races or visibility issues
- Stress test with 100 concurrent threads

### Exercise 5: Virtual Nodes
Add virtual node support to improve distribution.

**Requirements:**
- Configurable virtual node count
- Even distribution with as few as 10 physical nodes
- Test distribution with chi-squared test

### Exercise 6: Failure Handling
Handle node failures gracefully.

**Requirements:**
- Health check mechanism
- Automatic failover
- Re-route traffic from failed nodes

## Advanced Level

### Exercise 7: Rebalancing
Implement automatic rebalancing.

**Requirements:**
- Monitor skew factor
- Trigger rebalance when skew > threshold
- Minimize data movement during rebalance
- No downtime during rebalance

### Exercise 8: Cross-Node Queries
Implement scatter-gather pattern.

**Requirements:**
- Fan-out queries to all nodes
- Parallel execution using CompletableFuture
- Result merging and sorting
- Configurable timeout per node

### Exercise 9: Distributed Transactions
Implement a saga-based transaction coordinator.

**Requirements:**
- Compensating transactions on failure
- Transaction ID tracking
- Recovery from partial failures
- Idempotency guarantees

## Challenge Level

### Exercise 10: Production-Grade Implementation
Build a complete production-ready system.

**Requirements:**
- All of the above features integrated
- Comprehensive error handling
- JMX monitoring integration
- Graceful shutdown
- Configuration hot-reload
- Integration tests with actual databases

### Exercise 11: Performance Optimization
Profile and optimize the implementation.

**Requirements:**
- Use JMH for benchmarking
- Identify top 3 bottlenecks
- Implement optimizations
- Show before/after benchmarks

### Exercise 12: Chaos Engineering
Test the system under adverse conditions.

**Requirements:**
- Random node failures
- Network latency injection
- Data corruption scenarios
- Verify system recovers correctly
