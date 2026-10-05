# Lab 13 — Kafka Consumer Lag Incident — Theory: Mechanics + Detection

## 1. What Lag Is
- Lag = `log-end-offset − consumer-committed-offset` per partition, summed per group. Messages produced faster than consumed.
- Offsets committed to `__consumer_offsets`; rebalances pause consumption and spike lag.
- Lag is a queueing signal: rising lag + falling consumer throughput = incident; flat lag with catch-up = normal deploy.

## 2. Mechanics of Falling Behind
- Slow processing: blocking DB call, GC pause, poison-pill message retry loop.
- Under-partitioned: 3 partitions max 3 consumers in group; adding 10 pods doesn't help.
- Rebalance storm: short `session.timeout.ms` + long GC → repeated rebalances, no progress.
- Broker-side: slow disk, ISR shrink, leader election stalls fetch.
- Java client: `max.poll.records` too high + `max.poll.interval.ms` too low → kicked out of group.

## 3. Detection
| Signal | Tool |
|--------|------|
| `kafka_consumer_lag_sum` rising >10 min | Prometheus JMX/Kafka exporter, Burrow |
| Consumer throughput drop | `rate(kafka_consumer_records_consumed_total[5m])` |
| Rebalance rate spike | `kafka_consumer_rebalance_total` / coordinator logs |
| End-to-end latency (produce→consume) | OpenTelemetry trace, custom `record.timestamp` gauge |
| DLQ growth | Dead-letter topic rate |

## 4. Triage Order
1. `kafka-consumer-groups.sh --describe` → which partitions lagging? Owner assignment even?
2. Consumer logs: rebalance? exception? GC pause?
3. Broker: ISR, under-replicated partitions, disk/Network.
4. Decide: scale consumers (if partitions allow) vs fix poison pill vs add partitions (long-term).

## 5. Key Configs
- `fetch.max.wait.ms`, `max.poll.records` (batch size vs poll liveness trade-off).
- `session.timeout.ms` (10s default) + `heartbeat.interval.ms` (3s) + `max.poll.interval.ms` (5 min).
- Enable idempotence + transactional outbox for safe replays after lag catch-up.

## 6. Prevention
- Partition count ≥ 2× peak consumer concurrency; autoscale on lag, not CPU.
- DLQ + skip/park poison pills after N retries; alert on DLQ rate.
- Load-test with 2× produce rate; dashboard lag-by-partition heatmap.

## 7. Takeaway
Lag per-partition tells the story: all partitions lagging = slow code/broker; one partition spiking = hot key/poison pill. Never scale blindly without `--describe`.
