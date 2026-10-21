# Theory of Distributed Queues

## 1. Why Distributed Queues?

Queues decouple producers from consumers, allowing:
- Load leveling (smooth traffic spikes)
- Backpressure handling
- Buffering for downstream failures
- Multiple consumer patterns

## 2. Delivery Semantics

### At-Most-Once (Fire and Forget)
- Message sent once, no retry
- Can lose messages
- Highest throughput

### At-Least-Once
- Message retried until acknowledged
- Can cause duplicates
- Requires idempotent consumers

### Exactly-Once
- Message delivered exactly once
- Combines deduplication + idempotency
- Highest cost

## 3. Queue Partitioning

Partitions (shards) allow parallel processing:
- Each partition is an ordered sequence
- Messages within partition are ordered
- Cross-partition ordering not guaranteed
- Partition key determines assignment

## 4. Apache Pulsar Architecture

### Components
- **Broker**: Handles producer/consumer connections
- **BookKeeper**: Persistent message storage
- **ZooKeeper**: Metadata and coordination

### Subscription Types
- **Exclusive**: One consumer per subscription
- **Shared**: Multiple consumers, round-robin
- **Failover**: One active, standby consumers
- **Key_Shared**: Key-based ordering with multiple consumers

## 5. Message Deduplication

- Producer assigns unique message ID
- Consumer tracks processed IDs
- Broker detects and drops duplicates
- Time window for deduplication (usually 5 min)

## 6. Dead Letter Queues

Messages that can't be processed after max retries:
- Moved to DLQ for manual inspection
- Prevents poison pill messages from blocking
- Alerting on DLQ depth
