# Lab 13: Kafka Consumer Lag Incident — Data Processing Delay

## Situation Overview

**Scenario**: LinkedIn/Confluent — consumer lag grows to millions of messages, data processing delayed by hours

**Severity**: P1 (High) / SEV2

**Impact Assessment**:
- Order processing pipeline stalled — 2.7 million unprocessed messages in `order-events` topic
- Consumer lag growing at 10,000 messages/minute (production rate exceeds consumption rate)
- Data processing delayed by 3 hours 45 minutes at peak
- Real-time fraud detection system using same consumer group unable to detect active fraud patterns
- Business intelligence dashboards showing 4-hour stale data
- Customer notifications (order confirmations, shipping updates) delayed by hours
- Revenue impact: $63,000/hour in delayed order fulfillment
- Incident duration: 4 hours 12 minutes (14:23 UTC — 18:35 UTC)

**Affected Systems**:
- Kafka cluster `prod-events` (6 brokers, 3 AZs, Confluent Cloud)
- Consumer group `order-processor-group` (12 consumers across 3 pods)
- Topic `order-events` (24 partitions, replication factor 3)
- Downstream: Elasticsearch indexer, data warehouse (Snowflake), real-time dashboard
- Upstream: 47 microservices producing order events at ~5,000 messages/second

**Detection**: Grafana dashboard shows `records-lag-max` JMX metric climbing past 500,000. PagerDuty alert `KafkaConsumerLagHigh` fires at 14:28 UTC when lag exceeds 100,000 messages.

**Business Context**: The consumer lag was caused by a database bottleneck (PostgreSQL connection pool exhaustion in the consumer's transaction processing logic). This was exacerbated by repeated consumer group rebalances triggered by session timeouts — the rebalances paused all consumers, causing lag to accumulate faster than it could be drained.

**Engineering Teams Involved**:
- Data Platform Team (Kafka cluster, consumer groups)
- Java Application Team (consumer code, DB connection pool)
- Database Team (PostgreSQL performance, connection pool sizing)
- Observability Team (JMX metrics, Grafana dashboards)
- SRE Team (incident response, escalation)

## References

1. Confluent Blog — Kafka Consumer Lag: (link removed)
2. LinkedIn Engineering Blog — Kafka at Scale: (link removed)
3. Netflix Tech Blog — Kafka Consumer Tuning: https://netflixtechblog.com/kafka-consumer-tuning
4. Google SRE Book — Chapter 5: Eliminating Toil: https://sre.google/sre-book/eliminating-toil/
5. Apache Kafka Documentation — Consumer Configs: https://kafka.apache.org/documentation/#consumerconfigs
6. Confluent Documentation — Monitoring Consumer Lag: https://docs.confluent.io/platform/current/monitoring.html
7. Uber Engineering Blog — Kafka at Uber: (link removed)
8. Twitter Engineering Blog — Kafka Consumer Best Practices: https://blog.twitter.com/engineering/en_us/topics/infrastructure

## Key Metrics

| Metric | Value | Normal Range |
|--------|-------|-------------|
| Consumer lag (max) | 2,718,493 | < 10,000 |
| Lag growth rate | 10,000 msg/min | 0 (should drain) |
| Processing latency | 3h 45m | < 30 seconds |
| Consumer group rebalances | 17 in 4 hours | < 1 per hour |
| DB connection pool usage | 100% (50/50) | < 70% |
| Consumer poll timeout | 5 min (session timeout) | 30 seconds |
| Time to detect | 5 minutes (automated) | < 1 minute target |
| Time to resolve | 4h 12m | < 1 hour target |

## Detailed Impact Analysis

### Consumer Lag Growth Trajectory

| Time (UTC) | Lag (Messages) | Growth Rate | Cumulative Delay | Event |
|-----------|---------------|-------------|-----------------|-------|
| 14:00 | 12,000 | 0 (steady) | 0 min | Marketing campaign starts |
| 14:07 | 45,000 | +5,000/min | 0.5 min | DB connection pool exhaustion |
| 14:15 | 145,000 | +12,500/min | 2 min | First consumer timeout |
| 14:20 | 295,000 | +30,000/min | 4 min | Rebalance storm begins |
| 14:30 | 845,000 | +55,000/min | 11 min | 7 rebalances in 30 min |
| 14:45 | 1,520,000 | +45,000/min | 20 min | Multiple consumers dead |
| 15:00 | 2,100,000 | +38,000/min | 28 min | DB fix applied |
| 15:12 | 2,450,000 | +25,000/min | 33 min | Consumers recovering |
| 15:20 | 2,650,000 | +15,000/min | 35 min | Config tuning applied |
| 15:30 | 2,718,493 | 0 (peak) | 36 min | Static membership + cooperative |
| 15:45 | 2,100,000 | -8,000/min | 28 min | Lag draining |
| 16:00 | 150,000 | -150,000/min | 2 min | Drain accelerating |
| 16:02 | 0 | 0 | 0 | Lag cleared |

### Rebalance Storm Impact

Each rebalance had the following cost:

```
Consumer group: order-processor-group (12 consumers)
Assignment strategy: Eager (stop-the-world)
Rebalance duration: ~32 seconds average

Cost per rebalance:
- 12 consumers × 32 seconds = 384 consumer-seconds of lost processing
- At 5,000 msg/s production: 5,000 × 32 = 160,000 messages accumulate
- At 2,000 msg/s consumption: 2,000 × 32 = 64,000 messages NOT processed
- Net lag increase per rebalance: ~96,000 messages

Total cost (17 rebalances):
- Lost processing time: 17 × 384 = 6,528 consumer-seconds (108 minutes)
- Lag from rebalances: 17 × 96,000 = 1,632,000 messages
- Total peak lag: 2,718,493 (60% from rebalance storm alone)
```

### Consumer Configuration Comparison

| Parameter | Before (v1) | After (v2) | Impact |
|-----------|-------------|-------------|--------|
| max.poll.records | 500 | 5,000 | +900% throughput per poll |
| max.poll.interval.ms | 300,000 (5 min) | 600,000 (10 min) | 2× time before timeout |
| session.timeout.ms | 45,000 (45s) | 30,000 (30s) | Faster dead consumer detection |
| heartbeat.interval.ms | 15,000 (15s) | 10,000 (10s) | More frequent heartbeats |
| group.instance.id | Not set | ${HOSTNAME} | Static membership |
| partition.assignment.strategy | RangeAssignor | CooperativeStickyAssignor | Non-blocking rebalance |

### Throughput Analysis

```
Processing capacity per consumer (before):
  max.poll.records = 500
  processing time per message = 200ms (DB write)
  Total poll cycle = 500 × 200ms = 100 seconds
  Effective throughput = 5 msg/s per consumer
  Total (12 consumers) = 60 msg/s = 3,600 msg/min

Processing capacity per consumer (after):
  max.poll.records = 5,000
  processing time per message = 15ms (optimized DB write)
  + async queue decouples poll from write
  Total poll cycle = 5,000 × 15ms = 75 seconds
  Effective throughput = 67 msg/s per consumer
  Total (12 consumers) = 800 msg/s = 48,000 msg/min

Production rate at peak: 5,000 msg/s = 300,000 msg/min
Gap (before): 300,000 - 3,600 = 296,400 msg/min (lag growing)
Gap (after): 300,000 - 48,000 = 252,000 msg/min (lag draining)
Wait, the math doesn't work because I need to factor in the async processing.
With async: poll thread fast, processing in background.
Poll cycle = 5,000 × 0.1ms (queue) = 0.5 seconds
Processing = 5,000 × 15ms = 75 seconds (background, parallel)
Effective throughput limited by background processing with 8 threads:
  8 threads × (1000ms / 15ms) = 533 msg/s = 32,000 msg/min
  Still < 300,000 msg/min production
  
Need more consumers: scale to 50 consumers:
  50 × 533 = 26,650 msg/s (exceeds 5,000 msg/s production)
```

## Lessons Learned

1. **DB bottleneck**: Consumer processing time was dominated by database writes (avg 200ms per message). When connection pool exhausted, processing time jumped to 2+ seconds per message.

2. **Rebalance storm**: Session timeout (5 min) with 12 consumers caused frequent rebalances. Each rebalance paused all consumers for 30+ seconds, during which lag grew unchecked.

3. **No static group membership**: Without `group.instance.id`, any consumer restart triggered a full rebalance rather than incremental rebalancing.

4. **Cooperative rebalancing not used**: The consumer group was using eager rebalancing (stop-the-world), causing all consumers to pause during rebalance.

5. **No lag alert tuning**: The initial alert threshold (100,000 lag) was too high — by the time it fired, significant backlog had already accumulated.

6. **Batch size too small**: `max.poll.records` was set to 500 — increasing to 5,000 would have improved throughput significantly.

7. **No async processing**: Consumers wrote to DB synchronously in the poll thread, blocking the next poll cycle.

8. **No auto-scaling**: Consumer group replica count was static. No HPA based on consumer lag.

9. **No circuit breaker**: When DB was slow, consumers continued retrying instead of failing fast and re-queuing.

10. **Replication factor mismatch**: Topic had 24 partitions but only 12 consumers, meaning each consumer handled 2 partitions — any slowdown affected multiple partitions.

### Appendix A: Kafka Cluster Configuration

| Property | Value |
|----------|-------|
| Cluster | prod-events (Confluent Cloud) |
| Brokers | 6 |
| Regions | us-east-1a, us-east-1b, us-east-1c |
| Topic: order-events | 24 partitions, replication factor 3 |
| Retention | 7 days |
| Compression | lz4 |
| Max message size | 1 MB |
| acks | all |
| min.insync.replicas | 2 |
| Consumer group | order-processor-group |

### Appendix B: Consumer Configuration Template

```properties
# Standard consumer configuration for ALL production consumers

# Connection
bootstrap.servers=prod-events.confluent.cloud:9092
group.id=${spring.application.name}
client.id=${HOSTNAME}

# Session management
group.instance.id=${HOSTNAME}
session.timeout.ms=30000
heartbeat.interval.ms=10000
max.poll.interval.ms=600000

# Batch processing
max.poll.records=5000
fetch.min.bytes=1048576
fetch.max.wait.ms=500
max.partition.fetch.bytes=1048576

# Offset management
enable.auto.commit=false
auto.offset.reset=earliest

# Rebalancing
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor

# Security
security.protocol=SASL_SSL
sasl.mechanism=PLAIN

# Deserializers
key.deserializer=org.apache.kafka.common.serialization.StringDeserializer
value.deserializer=org.apache.kafka.common.serialization.StringDeserializer
```

### Appendix C: Consumer Group CLI Commands Reference

```bash
# Describe consumer group (check lag)
kafka-consumer-groups.sh --bootstrap-server <broker> --group <group> --describe

# Describe with state
kafka-consumer-groups.sh --bootstrap-server <broker> --group <group> --describe --state

# List members
kafka-consumer-groups.sh --bootstrap-server <broker> --group <group> --describe --members --verbose

# Reset offsets (for replay)
kafka-consumer-groups.sh --bootstrap-server <broker> --group <group> \
  --reset-offsets --to-earliest --topic <topic> --execute

# Delete consumer group
kafka-consumer-groups.sh --bootstrap-server <broker> --group <group> --delete

# Describe topic
kafka-topics.sh --bootstrap-server <broker> --describe --topic <topic>
```

### Appendix D: Rebalance Detection Script

```bash
#!/bin/bash
# detect-rebalance-storm.sh
# Monitors consumer group for excessive rebalancing

GROUP="order-processor-group"
BOOTSTRAP="prod-events.confluent.cloud:9092"
THRESHOLD=3  # Rebalances per hour threshold
SLACK_WEBHOOK="(link removed)"

echo "Monitoring rebalances for group: $GROUP"

while true; do
  # Get current rebalance count
  REBALANCE_COUNT=$(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP \
    --group $GROUP --describe --state 2>/dev/null | \
    grep -c "REBALANCING")
  
  # Check if group is currently rebalancing
  STATE=$(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP \
    --group $GROUP --describe --state 2>/dev/null | \
    tail -1 | awk '{print $NF}')
  
  echo "$(date): Group state: $STATE"
  
  if [ "$STATE" = "REBALANCING" ]; then
    echo "ALERT: Consumer group is rebalancing!"
    curl -X POST -H "Content-type: application/json" \
      --data "{\"text\":\":warning: Consumer group $GROUP is REBALANCING\"}" \
      $SLACK_WEBHOOK
  fi
  
  sleep 30
done
```

### Appendix E: Lag Drain Automation

```bash
#!/bin/bash
# drain-lag.sh — Automated lag drain with scaling

GROUP="order-processor-group"
TOPIC="order-events"
BOOTSTRAP="prod-events.confluent.cloud:9092"
DEPLOYMENT="order-processor-consumer"
NAMESPACE="production"
LAG_THRESHOLD=50000

drain_lag() {
  echo "=== Lag Drain Started: $(date) ==="
  
  # Get current lag
  TOTAL_LAG=$(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP \
    --group $GROUP --describe 2>/dev/null | \
    awk '{sum+=$5} END {print sum}')
  
  echo "Current lag: $TOTAL_LAG"
  
  if [ "$TOTAL_LAG" -gt "$LAG_THRESHOLD" ]; then
    echo "Lag exceeds threshold ($LAG_THRESHOLD). Scaling up consumers..."
    
    # Double consumer count
    CURRENT_REPLICAS=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE \
      -o jsonpath='{.spec.replicas}')
    NEW_REPLICAS=$((CURRENT_REPLICAS * 2))
    
    kubectl scale deployment $DEPLOYMENT -n $NAMESPACE --replicas=$NEW_REPLICAS
    echo "Scaled from $CURRENT_REPLICAS to $NEW_REPLICAS"
    
    # Monitor until lag clears
    while [ "$TOTAL_LAG" -gt 10000 ]; do
      sleep 30
      TOTAL_LAG=$(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP \
        --group $GROUP --describe 2>/dev/null | \
        awk '{sum+=$5} END {print sum}')
      echo "$(date): Lag = $TOTAL_LAG"
    done
    
    # Scale back down
    kubectl scale deployment $DEPLOYMENT -n $NAMESPACE --replicas=$CURRENT_REPLICAS
    echo "Scaled back to $CURRENT_REPLICAS"
  fi
  
  echo "=== Lag Drain Complete: $(date) ==="
}

drain_lag
```

### Appendix F: Consumer Lag KEDA Auto-Scaler

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: order-processor-consumer-scaler
  namespace: production
spec:
  scaleTargetRef:
    name: order-processor-consumer
  minReplicaCount: 12
  maxReplicaCount: 50
  triggers:
    - type: kafka
      metadata:
        bootstrapServers: prod-events.confluent.cloud:9092
        consumerGroup: order-processor-group
        topic: order-events
        lagThreshold: "10000"
        offsetResetPolicy: earliest
  advanced:
    horizontalPodAutoscalerConfig:
      behavior:
        scaleUp:
          stabilizationWindowSeconds: 0
          policies:
            - type: Percent
              value: 100
              periodSeconds: 15
        scaleDown:
          stabilizationWindowSeconds: 300
          policies:
            - type: Percent
              value: 50
              periodSeconds: 60
```

### Appendix G: Circuit Breaker Configuration

```yaml
resilience4j.circuitbreaker:
  instances:
    orderEventDatabase:
      registerHealthIndicator: true
      slidingWindowSize: 100
      minimumNumberOfCalls: 10
      permittedNumberOfCallsInHalfOpenState: 5
      automaticTransitionFromOpenToHalfOpenEnabled: true
      waitDurationInOpenState: 30s
      failureRateThreshold: 50
      recordExceptions:
        - org.springframework.dao.DataAccessException
        - java.sql.SQLException
        - java.net.ConnectException
      ignoreExceptions:
        - com.acmecorp.orderprocessor.exception.ValidationException
```
