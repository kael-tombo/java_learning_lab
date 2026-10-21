# 18 - Distributed Queues

## Overview
Distributed queues enable asynchronous communication between services with guarantees about message ordering, delivery, and processing semantics. This lab covers SQS, Pulsar, partitioned queues, and exactly-once semantics.

## Prerequisites
- Java 21+
- Maven 3.8+
- Understanding of distributed systems and messaging

## Topics Covered
- SQS (Simple Queue Service) architecture
- Apache Pulsar topics and subscriptions
- Partitioned queues and ordering guarantees
- At-least-once, at-most-once, exactly-once semantics
- Message deduplication and idempotency
- Dead letter queues and retry policies
- Queue monitoring and metrics

## Package Structure
- com.distributed.queues — Core implementations
  - DistributedQueue.java — Queue interface
  - InMemoryPartitionedQueue.java — Partitioned queue
  - PulsarClient.java — Pulsar producer/consumer
  - MessageDeduplicator.java — Exactly-once support
  - DeadLetterQueue.java — DLQ implementation
  - QueuePartitioner.java — Partition strategy
