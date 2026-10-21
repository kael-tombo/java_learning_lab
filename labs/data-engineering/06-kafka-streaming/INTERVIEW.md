# Kafka Streams Interview Questions

## Beginner
**Q**: What is Kafka Streams and how is it different from Kafka Consumer?
**A**: Kafka Streams is a stream processing library built on top of Kafka's consumer/producer APIs, adding stateful processing, exactly-once semantics, and a declarative DSL.

## Intermediate
**Q**: How does exactly-once work in Kafka Streams?
**A**: Uses Kafka's transactional API. Producers write atomically to output topics and consumer offsets are committed as part of the same transaction.

## Advanced
**Q**: How would you handle state store recovery in Kafka Streams?
**A**: State stores are backed by changelog topics. On restart or rebalance, the stores are rebuilt from these topics. RocksDB provides fast local recovery with the changelog as the source of truth.
