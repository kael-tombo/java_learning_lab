# Lab 13 — Real-World Project: Lag War Room

## Incident Timeline (Flash-Sale Lag)
| Time | Event |
|------|-------|
| T+0 | Produce 3× normal (flash sale); lag alert `sum>10k for 10m` fires |
| T+3m | `--describe`: all 6 partitions lagging uniformly (~8k each), assignment even |
| T+6m | Consumer logs: p99 processing 800ms (downstream DB throttling) + rebalance every ~4 min |
| T+8m | SEV-2 declared; downstream throttled reads scaled; `max.poll.records` 200→50 to stop rebalances |
| T+15m | KEDA scales consumers 6→12 (12 partitions available); drain rate 2.5k/s vs produce 2k/s |
| T+35m | Lag <1k; E2E p99 back <30s; SEV downgraded |
| T+60m | Resolved; DLQ 212 poison msgs triaged separately |
| T+2d | Post-mortem: partition doubling + DB pool fix + lag-based autoscale |

## War-Room Runbook
1. **Describe** (2 min): per-partition lag + ownership; hot vs uniform decides path.
2. **Logs**: rebalance? exception? GC? Downstream 429/timeout?
3. **Broker**: ISR/URP, disk, leader balance — rule out infra.
4. **Stop growth**: cut batch size, pause non-critical groups, throttle producer if business-ok.
5. **Drain**: scale to partitions (KEDA), fix poison via DLQ, replay after.
6. **Verify**: falling lag + E2E p99 green for 15 min before resolve.

## Metrics That Matter
- TTD: lag alert <10 min. TTM: growth stopped <15 min. Drain ETA posted in channel.
- SLI: E2E p99 <30s; lag sum <10k. SLO burn triggers page.
- DLQ rate + age; rebalance rate; consume throughput vs produce.

## Prevention Backlog
- [ ] 12→24 partitions (key review) + KEDA lag autoscale.
- [ ] Bounded retry + DLQ everywhere; DLQ dashboard + weekly triage.
- [ ] DB pool + cache for downstream; backpressure `pause()` on 429.
- [ ] 2× load test pre-sale; lag heatmap on NOC wall.
- [ ] Retention sized to 2× worst drain time.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Kafka consumer group / offset management: https://kafka.apache.org/documentation/#consumerconfigs
- Kafka consumer configs (poll intervals, session timeout): https://kafka.apache.org/documentation/#consumerconfigs
- Kubernetes autoscaling with KEDA (lag-based): https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
