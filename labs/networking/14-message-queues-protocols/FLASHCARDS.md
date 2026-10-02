# FLASHCARDS — Message Queues

| # | Front | Back |
|---|-------|------|
| 1 | Three core patterns? | Pub/sub (broadcast), work queue (partition labor), request/reply (correlation ID). |
| 2 | Routing ladder? | Fanout → direct → topic (increasing expressiveness). |
| 3 | DLQ? | Poison-message quarantine for autopsy. |
| 4 | Broker vs log? | Smart-broker-push (RabbitMQ) vs dumb-broker-pull (Kafka). |
| 5 | Keyed vs null-key? | Same partition (order) vs round-robin (spread). |
| 6 | Parallelism bound? | min(partitions, consumers). |
| 7 | Semantic ladder? | At-most (lossy) → at-least (dups) → exactly-once (transactions). |
| 8 | Kafka exactly-once trio? | Idempotent producer + transactions + offset coordination. |
| 9 | MQTT fit? | Constrained IoT: 2-byte header, QoS 0/1/2, last-will. |
| 10 | Lag signals? | Queue depth (RMQ UI) / consumer lag (kafka-consumer-groups). |
| 11 | Backpressure order? | Depth → slow consumer → scale → batch → async → repartition → throttle. |
| 12 | Rebalance triggers? | Join/leave; EagerSticky vs CooperativeSticky. |
| 13 | Fraud pipeline shape? | Kafka ingest → Flink windows + RocksDB → Redis alerts. |
| 14 | Batch knobs? | `fetch.min.bytes`, `max.poll.records`. |
| 15 | Producer signals? | acks=all, publisher confirms, flow control. |
