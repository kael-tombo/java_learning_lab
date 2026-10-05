# Lab 13 — Code Deep Dive: kafka-consumer-groups.sh Runbook

## 1. Describe & Scope (2 min)
```bash
K=kafka-prod:9092; G=orders-group
kafka-consumer-groups.sh --bootstrap-server $K --describe --group $G
kafka-consumer-groups.sh --bootstrap-server $K --list | grep $G
kafka-topics.sh --bootstrap-server $K --describe --topic orders | grep -E "Partition|Leader|Isr|Replicas"
```

## 2. Log Snippets
```
# Healthy poll
[Consumer clientId=c-1, groupId=orders-group] Finished assignment for group: {c-1=[orders-0, orders-1]}
# Rebalance storm
[Consumer clientId=c-2] Member c-2 sending LeaveGroup request
[Consumer clientId=c-2] (Re-)joining group
 WARN  Auto offset commit failed: CommitFailedException: Commit cannot be completed since group rebalanced
# Poison pill
ERROR DeserializationException: Can't deserialize data for topic orders partition 3 offset 88123
  at JsonDeserializer.deserialize(...)
  ... retry attempt 47/∞ — lag climbing
# Broker trouble
WARN  [ReplicaFetcher] Under-replicated partition orders-2: ISR [1,2] shrank to [1]
ERROR  LEADER_NOT_AVAILABLE for partition orders-2 — fetch stalled
# Java GC pause
[GC (Allocation Failure) 8192M->8100M, pause 12.4s]  # > session.timeout → rebalance
```

## 3. Consumer Fix (Spring Kafka Sketch)
```java
@KafkaListener(topics = "orders", properties = {
  "max.poll.records:50", "max.poll.interval.ms:300000",
  "session.timeout.ms:10000", "heartbeat.interval.ms:3000"})
public void onMsg(ConsumerRecord<String, Order> r, Acknowledgment ack) {
  try { process(r.value()); ack.acknowledge(); }
  catch (RetryableException e) { retryWithBackoff(r, e); }      // bounded 3×
  catch (Exception e) { dlq.send("orders.DLT", r, e); ack.acknowledge(); } // park poison
}
```

## 4. Reset / Replay (Careful — Staging First)
```bash
# Dry-run reset to 1h ago
kafka-consumer-groups.sh --bootstrap-server $K --group $G --topic orders \
  --reset-offsets --to-datetime 2026-10-05T09:00:00.000 --dry-run
# Execute + verify
kafka-consumer-groups.sh --bootstrap-server $K --group $G --topic orders \
  --reset-offsets --to-datetime 2026-10-05T09:00:00.000 --execute
kafka-consumer-groups.sh --bootstrap-server $K --describe --group $G
```

## 5. Alerts
```promql
sum by (group) (kafka_consumer_lag_sum) > 10000
rate(kafka_consumer_records_consumed_total[5m]) < 0.5 * avg_over_time(rate(kafka_consumer_records_consumed_total[1h])[5m:])
increase(kafka_consumer_rebalance_total[15m]) > 5
```

Order: describe → assign check → consumer logs → broker ISR → scale-or-DLQ → verify drain rate.
