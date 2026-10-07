# Prevention: Kafka Consumer Lag

## Strategic Prevention Framework

Based on patterns from Confluent's Kafka operational best practices, LinkedIn Engineering's Kafka-at-scale experience, and Google SRE principles for eliminating toil.

## Layer 1: Static Group Membership

### Mandatory Consumer Configuration

```properties
# Required for ALL production Kafka consumers
group.instance.id=${HOSTNAME}  # Unique per consumer instance
session.timeout.ms=30000        # 30 seconds
heartbeat.interval.ms=10000     # 10 seconds
max.poll.interval.ms=600000     # 10 minutes (with async processing)
max.poll.records=5000           # Process more per batch
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

### Why Static Group Membership Prevents Rebalance Storms

Without `group.instance.id`:
- Consumer stops heartbeating → broker detects timeout → triggers full rebalance
- All consumers stop processing during rebalance
- Rebalance reassigns ALL partitions

With `group.instance.id`:
- Consumer stops heartbeating → broker marks that specific member as dead
- Only that member's partitions are reassigned (incremental)
- Other consumers continue processing unaffected
- When consumer rejoins, it reclaims its original assignment

## Layer 2: Cooperative Rebalancing

### Consumer Configuration

```java
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    "org.apache.kafka.clients.consumer.CooperativeStickyAssignor");
```

### Benefits vs Eager Rebalancing

| Aspect | Eager Rebalancing | Cooperative Rebalancing |
|--------|------------------|------------------------|
| Processing during rebalance | All consumers stopped | Only revoked partitions stop |
| Assignment stability | Full reassignment | Sticky (minimal movement) |
| Rebalance duration | 30-60 seconds | < 1 second per consumer |
| Impact on lag | Significant increase | Minimal |
| Consumer group availability | 0% during rebalance | ~95% during rebalance |

## Layer 3: Async Processing Pattern

### Architecture

```
Kafka Topic
    ↓ (poll)
Consumer Thread (fast, non-blocking)
    ↓ (queue)
Async Processing Queue (ArrayBlockingQueue)
    ↓ (drain)
Batch Processor (scheduled, rate-limited)
    ↓ (batch insert)
Database
```

### Implementation Requirements

```properties
# Async processing configuration
kafka.consumer.async.enabled=true
kafka.consumer.async.queue.capacity=10000
kafka.consumer.async.batch.size=500
kafka.consumer.async.flush.interval.ms=1000
kafka.consumer.async.retry.max-attempts=3
kafka.consumer.circuit-breaker.enabled=true
kafka.consumer.circuit-breaker.threshold=100  # consecutive failures before circuit opens
kafka.consumer.circuit-breaker.reset-timeout-ms=30000
```

### Degradation Behavior

1. **Normal**: Async queue → batch processor → DB (low latency, high throughput)
2. **Queue near full**: Fall back to synchronous processing (latency increases, throughput preserved)
3. **DB unavailable**: Circuit breaker opens, messages remain in Kafka (no data loss)
4. **Consumer restart**: Static group membership preserves partition assignment
5. **Traffic spike**: Queue absorbs bursts; batch processor scales within limits

## Layer 4: Early Lag Detection

### Alert Thresholds

```yaml
- alert: KafkaConsumerLagWarning
  expr: kafka_consumer_lag_total{topic="order-events"} > 10000
  for: 1m
  labels:
    severity: warning
  annotations:
    summary: "Consumer lag > 10K for {{ $labels.consumer_group }}"
    description: "Processing delay: ~{{ $value | humanizeDuration }}"

- alert: KafkaConsumerLagCritical
  expr: kafka_consumer_lag_total{topic="order-events"} > 50000
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Consumer lag > 50K for {{ $labels.consumer_group }}"
    description: "Processing delay: ~{{ $value | humanizeDuration }}"

- alert: KafkaConsumerRebalancing
  expr: rate(kafka_consumer_group_rebalance_count[10m]) > 1
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "High rebalance rate for {{ $labels.consumer_group }}"
    description: "{{ $value }} rebalances per 10 minutes"
```

## Layer 5: Consumer Health Dashboard

### Key Metrics

| Metric | Source | Threshold | Action |
|--------|--------|-----------|--------|
| Lag per partition | kafka-consumer-groups | < 1,000 | Info |
| Total lag | JMX records-lag-max | < 10,000 | Warning |
| Lag growth rate | Derivative of total lag | < 0 | Critical if > 0 |
| Rebalance count | Broker metrics | < 1/hour | Warning if > 1 |
| Processing time | Micrometer Timer | < 100ms avg | Warning if > 500ms |
| DB connection usage | HikariCP metrics | < 80% | Warning if > 80% |
| Async queue fill rate | Custom metric | < 60% | Warning if > 80% |
| Poll cycle duration | Kafka metrics | < 60s | Warning if > 240s |
| Consumer count | Consumer group | = expected | Critical if mismatch |

## Layer 6: Preventive CI/CD Checks

```yaml
# CI pipeline: Kafka consumer verification
stages:
  - stage: KafkaConsumerCheck
    jobs:
      - job: ValidateConsumerConfig
        steps:
          - script: |
              # Verify group.instance.id is set
              grep -q "group.instance.id" src/main/resources/application.yml
              if [ $? -ne 0 ]; then
                echo "ERROR: group.instance.id must be configured"
                exit 1
              fi
          - script: |
              # Verify CooperativeStickyAssignor
              grep -q "CooperativeStickyAssignor" src/main/resources/application.yml
              if [ $? -ne 0 ]; then
                echo "ERROR: CooperativeStickyAssignor must be used"
                exit 1
              fi
          - script: |
              # Verify max.poll.records >= 1000
              MAX_POLL=$(grep "max-poll-records" src/main/resources/application.yml | awk '{print $2}')
              if [ "$MAX_POLL" -lt 1000 ]; then
                echo "ERROR: max.poll.records should be >= 1000"
                exit 1
              fi
          - script: |
              # Verify async processing pattern is used
              grep -q "ArrayBlockingQueue\|CompletableFuture.runAsync" src/main/java/
              if [ $? -ne 0 ]; then
                echo "WARNING: Async processing pattern not detected"
              fi
```

## Layer 7: Operational Runbook

### Lag Drain Procedure

```bash
#!/bin/bash
# drain-lag.sh — Emergency lag drain procedure

GROUP="order-processor-group"
TOPIC="order-events"
BOOTSTRAP="prod-events.confluent.cloud:9092"
EXPECTED_CONSUMERS=12

echo "=== Kafka Lag Drain Procedure ==="

# 1. Check current lag
echo "--- Current Lag ---"
kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP \
  --group $GROUP --describe

# 2. Check consumer count
CONSUMER_COUNT=$(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP \
  --group $GROUP --describe --members --verbose | grep -c "member_id")
echo "Active consumers: $CONSUMER_COUNT"

if [ "$CONSUMER_COUNT" -lt "$EXPECTED_CONSUMERS" ]; then
  echo "WARNING: Consumer count ($CONSUMER_COUNT) below expected ($EXPECTED_CONSUMERS)"
fi

# 3. Check for rebalances
REBALANCES=$(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP \
  --group $GROUP --describe --state | grep rebalance)
if [ -n "$REBALANCES" ]; then
  echo "WARNING: Group in rebalance state!"
fi

# 4. Increase processing throughput
kubectl scale deployment order-processor-consumer --replicas=24
echo "Scaled consumers to 24 (2x for lag drain)"

# 5. Monitor drain rate
while true; do
  TOTAL_LAG=0
  while IFS= read -r line; do
    LAG=$(echo "$line" | awk '{print $5}')
    if [ "$LAG" != "LAG" ] && [ -n "$LAG" ]; then
      TOTAL_LAG=$((TOTAL_LAG + LAG))
    fi
  done < <(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP \
    --group $GROUP --describe 2>/dev/null)
  
  echo "$(date): Lag = $TOTAL_LAG"
  if [ "$TOTAL_LAG" -lt 10000 ]; then
    echo "Lag cleared!"
    break
  fi
  sleep 30
done

# 6. Scale back down
kubectl scale deployment order-processor-consumer --replicas=12
echo "Scaled consumers back to 12"
```

## Key Prevention Metrics

| Control | Metric | Target | Owner |
|---------|--------|--------|-------|
| Static membership | % of groups with group.instance.id | 100% | App team |
| Cooperative rebalancing | % of groups using CooperativeStickyAssignor | 100% | App team |
| Async processing | % of consumers with async pattern | 100% | App team |
| Lag alert coverage | % of groups with lag < 10K alert | 100% | SRE |
| Rebalance alerting | % of groups monitored for rebalances | 100% | SRE |
| Lag drain time | Time to clear lag > 100K | < 30 min | SRE |
| Consumer health | % of consumers meeting all requirements | 100% | Platform |

## References

- Confluent Blog — Kafka Consumer Lag: (link removed)
- LinkedIn Engineering — Kafka at Scale: (link removed)
- Netflix Tech Blog — Kafka Consumer Tuning: https://netflixtechblog.com/kafka-consumer-tuning
- Apache Kafka Documentation: https://kafka.apache.org/documentation/#consumerconfigs
- Google SRE Book — Eliminating Toil: https://sre.google/sre-book/eliminating-toil/
