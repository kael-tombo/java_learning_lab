# Quiz: CockroachDB

## Section 1: Fundamentals

### Q1: What is the primary benefit of cockroachdb in distributed databases?
A) Reduced storage costs
B) Improved single-node performance
C) Horizontal scalability
D) Simplified application code
**Answer: C**

### Q2: Which property is MOST important when designing a distributed database strategy?
A) Key length
B) Cardinality and distribution
C) Key data type
D) Key creation timestamp
**Answer: B**

### Q3: In consistent hashing, what happens when a node is removed?
A) All data must be redistributed
B) Only data from the removed node needs redistribution
C) The system goes into read-only mode
D) Data is replicated to all remaining nodes
**Answer: B**

### Q4: What is the main advantage of hash-based distribution over range-based?
A) Better range query performance
B) More even data distribution
C) Simpler to implement
D) Easier to rebalance
**Answer: B**

### Q5: Scatter-gather pattern is used for:
A) Distributing writes across nodes
B) Executing queries without the routing key
C) Rebalancing data between nodes
D) Backing up distributed databases
**Answer: B**

## Section 2: Design

### Q6: What is a hotspot in a distributed database?
A) A node with very fast hardware
B) A node that receives disproportionately more traffic
C) A backup node used during maintenance
D) A node using in-memory storage
**Answer: B**

### Q7: Virtual nodes primarily help with:
A) Reducing memory usage
B) Improving load distribution across physical nodes
C) Increasing security through obfuscation
D) Simplifying the routing algorithm
**Answer: B**

### Q8: Which consistency level provides the highest availability?
A) Strong consistency
B) Eventual consistency
C) Causal consistency
D) Linearizability
**Answer: B**

### Q9: When should you avoid distributing data across multiple nodes?
A) Dataset exceeds 10TB
B) Write throughput exceeds 10K ops/sec
C) Dataset fits comfortably on a single node
D) Geographic distribution is required
**Answer: C**

### Q10: What is split-brain?
A) Two nodes having different schema versions
B) Multiple nodes accepting writes for the same data
C) A node using two different hash functions
D) Cross-shard queries returning inconsistent results
**Answer: B**

## Section 3: Advanced

### Q11: The PACELC theorem adds to CAP by considering:
A) Trade-off between latency and consistency when the system is normal
B) Trade-off between partition tolerance and availability
C) A fourth property: durability
D) Geographic distribution considerations
**Answer: A**

### Q12: In distributed transactions, the Saga pattern uses:
A) Two-phase commit with blocking coordination
B) Compensating transactions to undo previous steps on failure
C) Read-only snapshots for consistency
D) Pessimistic locking across all nodes
**Answer: B**
