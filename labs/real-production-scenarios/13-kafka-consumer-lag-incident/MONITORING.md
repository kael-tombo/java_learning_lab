# Monitoring: Kafka Consumer Lag

## Monitoring Architecture

Multi-layered monitoring to detect consumer lag at multiple thresholds, identify rebalance storms, and provide early warning of downstream dependency failures.

## 1. Kafka Consumer Group Metrics

### JMX Metrics (records-lag-max)

| Metric | MBean | Description |
|--------|-------|-------------|
| records-lag-max | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=*` | Max lag across all partitions |
| records-lag | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=*` | Per-partition lag |
| records-consumed-rate | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=*` | Consumption rate (msg/s) |
| fetch-rate | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=*` | Fetch request rate |
| network-io-rate | `kafka.consumer:type=consumer-metrics,client-id=*` | Network I/O rate |

### Broker-Side Consumer Group Metrics

| Metric | MBean | Description |
|--------|-------|-------------|
| rebalance-rate-per-hour | `kafka.consumer.group:type=consumer-group-metrics,group=*` | Hourly rebalance rate |
| group-size | `kafka.consumer.group:type=consumer-group-metrics,group=*` | Consumer count |
| group-state | `kafka.consumer.group:type=consumer-group-metrics,group=*` | STABLE, REBALANCING, DEAD |

## 2. Prometheus Alert Rules

```yaml
groups:
  - name: kafka_consumers
    interval: 30s
    rules:
      - alert: KafkaConsumerLagWarning
        expr: kafka_consumer_lag_total{topic="order-events"} > 10000
        for: 1m
        labels:
          severity: warning
          team: data-platform
        annotations:
          summary: "Consumer lag > 10K for {{ $labels.consumer_group }}"
          description: "Lag: {{ $value }} messages (approx {{ $value | humanizeDuration }} delay)"

      - alert: KafkaConsumerLagCritical
        expr: kafka_consumer_lag_total{topic="order-events"} > 100000
        for: 1m
        labels:
          severity: critical
          team: data-platform
          page: true
        annotations:
          summary: "Consumer lag > 100K for {{ $labels.consumer_group }}"
          description: "Lag: {{ $value }} messages. Processing delay critical."
          runbook: "https://runbook.acmecorp.com/kafka-lag"

      - alert: KafkaConsumerLagGrowing
        expr: |
          deriv(kafka_consumer_lag_total{topic="order-events"}[10m]) > 1000
        for: 5m
        labels:
          severity: warning
          team: data-platform
        annotations:
          summary: "Consumer lag growing for {{ $labels.consumer_group }}"
          description: "Lag increasing at {{ $value }} msg/min"

      - alert: KafkaConsumerRebalanceRate
        expr: |
          rate(kafka_consumer_group_rebalance_count{group="order-processor-group"}[1h]) > 2
        for: 5m
        labels:
          severity: warning
          team: data-platform
        annotations:
          summary: "High rebalance rate for {{ $labels.group }}"
          description: "{{ $value }} rebalances/hour. Possible rebalance storm."

      - alert: KafkaConsumerDown
        expr: |
          kafka_consumer_group_members{group="order-processor-group"} < 12
        for: 1m
        labels:
          severity: critical
          team: data-platform
        annotations:
          summary: "Consumer group {{ $labels.group }} has fewer members than expected"
          description: "Expected 12, have {{ $value }}"

      - alert: KafkaConsumerProcessingTime
        expr: |
          kafka_consumer_processing_time_seconds{consumer_group="order-processor-group"} > 0.5
        for: 5m
        labels:
          severity: warning
          team: app-team
        annotations:
          summary: "Consumer processing time > 500ms for {{ $labels.consumer_group }}"
```

## 3. Prometheus Recording Rules

```yaml
groups:
  - name: kafka_recording
    rules:
      - record: kafka_consumer_lag_total
        expr: sum by (consumer_group, topic) (kafka_consumer_fetch_manager_metrics_records_lag)
      
      - record: kafka_consumer_lag_growth_rate
        expr: deriv(kafka_consumer_lag_total[10m])
      
      - record: kafka_consumer_group_rebalance_count
        expr: increase(kafka_consumer_coordinator_metrics_rebalance_rate_total[1h])
      
      - record: kafka_consumer_throughput
        expr: sum(rate(kafka_consumer_fetch_manager_metrics_records_consumed_rate[5m]))
```

## 4. Grafana Dashboard: Kafka Consumer Health

### Panel 1: Total Lag (Singlestat + Timeseries)
- **Query**: `kafka_consumer_lag_total{topic="order-events"}`
- **Thresholds**: green < 10K, yellow 10K-100K, red > 100K
- **Warning line**: 10,000
- **Critical line**: 100,000

### Panel 2: Lag per Partition (Bar Gauge)
- **Query**: `kafka_consumer_fetch_manager_metrics_records_lag`
- **Group by**: partition
- **Display**: horizontal bar chart showing imbalanced partitions

### Panel 3: Lag Growth Rate (Timeseries)
- **Query**: `kafka_consumer_lag_growth_rate`
- **Display**: msg/min
- **Zero line**: highlighted (lag growing above zero is bad)

### Panel 4: Rebalance Rate (Timeseries)
- **Query**: `rate(kafka_consumer_group_rebalance_count[1h])`
- **Threshold**: 1 rebalance/hour
- **Display**: spikes indicate rebalance storms

### Panel 5: Consumer Count (Stat)
- **Query**: `kafka_consumer_group_members{group="order-processor-group"}`
- **Expected**: 12
- **Alert**: any deviation

### Panel 6: Processing Time (Heatmap)
- **Query**: `kafka_consumer_processing_time_seconds`
- **Display**: histogram of processing times
- **Threshold**: 500ms line

### Panel 7: Throughput Rate (Timeseries)
- **Query**: `kafka_consumer_throughput{consumer_group="order-processor-group"}`
- **Compare**: production rate vs consumption rate
- **Dual axis**: production (line) vs consumption (line)

### Panel 8: DB Connection Pool (Singlestat)
- **Query**: `hikaricp_connections_active{pool="OrderProcessorPool"}`
- **Display**: active / total connections
- **Threshold**: > 80% usage

## 5. Synthetic Consumer Health Check

```bash
#!/bin/bash
# consumer-health-check.sh

GROUP="order-processor-group"
TOPIC="order-events"
BOOTSTRAP="prod-events.confluent.cloud:9092"
SLACK_WEBHOOK="(link removed)"

echo "=== Kafka Consumer Health Check ==="

# 1. Check group state
STATE=$(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP \
  --group $GROUP --describe --state 2>/dev/null | tail -1 | awk '{print $NF}')
echo "Group state: $STATE"

if [ "$STATE" != "STABLE" ]; then
  curl -X POST -H "Content-type: application/json" \
    --data "{\"text\":\":warning: Consumer group $GROUP is in state: $STATE\"}" \
    $SLACK_WEBHOOK
fi

# 2. Check total lag
TOTAL_LAG=0
while IFS= read -r line; do
  LAG=$(echo "$line" | awk '{print $5}')
  if [ "$LAG" != "LAG" ] && [ -n "$LAG" ] && [ "$LAG" -eq "$LAG" ] 2>/dev/null; then
    TOTAL_LAG=$((TOTAL_LAG + LAG))
  fi
done < <(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP \
  --group $GROUP --describe 2>/dev/null)
echo "Total lag: $TOTAL_LAG"

if [ "$TOTAL_LAG" -gt 10000 ]; then
  curl -X POST -H "Content-type: application/json" \
    --data "{\"text\":\":warning: Consumer lag $TOTAL_LAG for $GROUP\"}" \
    $SLACK_WEBHOOK
fi

# 3. Check consumer count
MEMBER_COUNT=$(kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP \
  --group $GROUP --describe --members --verbose 2>/dev/null | grep -c "member_id")
echo "Consumer count: $MEMBER_COUNT"

# 4. Check partition imbalance
echo "--- Partition Lag Distribution ---"
kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP \
  --group $GROUP --describe 2>/dev/null | grep -v "^$" | tail -n +2 | \
  awk '{print $1, $2, $3, $4, $5}'

echo "=== Health Check Complete ==="
```

## 6. Alert Escalation Matrix

| Alert | Severity | Notification | Response Time | Action |
|-------|----------|-------------|---------------|--------|
| Lag > 10K | Warning | Slack #ops-alerts | 15 min | Investigate |
| Lag > 100K | Critical | PagerDuty + Slack | 5 min | Declare incident |
| Lag growing | Warning | Slack #ops-alerts | 15 min | Check throughput |
| > 2 rebalances/hour | Warning | Slack #ops-alerts | 15 min | Check member stability |
| Consumer count < expected | Critical | PagerDuty + Slack | 5 min | Scale consumers |
| Processing time > 500ms | Warning | Slack #app-alerts | 30 min | Check dependencies |
| DB pool > 80% | Warning | Slack #ops-alerts | 15 min | Scale DB/connections |
| DB pool 100% | Critical | PagerDuty + Slack | 5 min | Emergency DB actions |

## 7. Integration with External Monitoring

```yaml
# Datadog integration
datadog:
  kafka:
    consumer:
      - lag_total
      - lag_per_partition
      - rebalance_count
      - consumer_count
      - processing_time
      - throughput
```

## References

- Confluent Monitoring: https://docs.confluent.io/platform/current/monitoring.html
- LinkedIn Kafka Observability: (link removed)
- Apache Kafka JMX Metrics: https://kafka.apache.org/documentation/#monitoring
- Google SRE Monitoring Principles: https://sre.google/sre-book/monitoring-distributed-systems/
