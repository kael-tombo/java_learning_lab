# Lab 13 — Flashcards: Kafka Consumer Lag

| # | Front | Back |
|---|-------|------|
| 1 | Lag | log-end-offset − committed offset |
| 2 | Offsets stored | __consumer_offsets |
| 3 | First command | kafka-consumer-groups.sh --describe |
| 4 | Hot partition | Hot key / poison pill |
| 5 | Uniform lag | Slow code or broker |
| 6 | Max useful consumers | = partition count |
| 7 | max.poll.records | Batch size vs poll liveness trade-off |
| 8 | max.poll.interval.ms | Kick member if poll gap exceeds (5 min def) |
| 9 | session.timeout.ms | 10s default failure detector |
| 10 | heartbeat.interval.ms | 3s, must be << session timeout |
| 11 | Rebalance storm | GC/blocking poll → repeated rebalances |
| 12 | Poison pill | Bad msg causing retry loop |
| 13 | DLQ | Dead-letter topic after N retries |
| 14 | Idempotent consumer | Safe replay via unique key |
| 15 | E2E latency | record.timestamp → consume time |
| 16 | Lag growth rate | Δlag/Δt = msgs/s behind |
| 17 | Scale signal | Lag, not CPU |
| 18 | Heatmap | Lag by partition visual |
| 19 | ISR | In-sync replicas; shrink = broker trouble |
| 20 | URP | Under-replicated partitions metric |
| 21 | Burrow | Lag status OK/WARN/ERR evaluator |
| 22 | Coordinator logs | Rebalance join/sync lines |
| 23 | Pause API | consumer.pause() for backpressure |
| 24 | Autoscale cap | max replicas = partitions |
| 25 | Cooldown | 5 min to avoid thrash |
| 26 | Retention vs lag | Lag beyond retention = data loss |
| 27 | Fetch latency | Broker-side slowness signal |
| 28 | JMX lag metric | kafka_consumer_records_lag / fetch manager |
| 29 | Consume rate | rate(records_consumed_total[5m]) |
| 30 | SLI | p99 produce-to-consume <30s |
| 31 | Load test | 2× produce sustained |
| 32 | Key design | Even distribution avoids hot partition |
| 33 | Partition sizing | ≥2× peak concurrency |
| 34 | Adding partitions | Needs key-compatible; ordering caveat |
| 35 | Ordering | Guaranteed only within partition |
| 36 | Retry backoff | Exponential, bounded, with headers |
| 37 | DLQ headers | topic/partition/offset/error |
| 38 | Alert threshold | sum(lag)>10k for 10 min (tune per topic) |
| 39 | Catch-up vs incident | Falling lag = recovering; rising = incident |
| 40 | Rolling restart cost | Rebalance no-progress window |
| 41 | GC pause link | Long pause → missed poll → rebalance |
| 42 | Blocking poll | Never block poll thread; use worker pool |
| 43 | Worker pool | Bounded queue + backpressure |
| 44 | Commit mode | Sync for correctness, async for speed |
| 45 | Auto-commit risk | Duplicates/loss on crash |
| 46 | Seek replay | consumer.seek() to reprocess |
| 47 | Reset offsets | --reset-offsets --to-datetime (careful) |
| 48 | Runbook order | describe → logs → broker → scale-or-skip |
| 49 | Mitigation target | <10 min to stop growth |
| 50 | Post-mortem Q | Why no DLQ / why partitions capped? |
| 51 | Dashboard must | Lag sum + by-partition + consume rate |
| 52 | On-call habit | Check partition ownership first |
| 53 | Java client | spring-kafka poll timeout tuning |
| 54 | Micrometer gauge | kafka.consumer.lag custom metric |
| 55 | Chaos drill | Kill consumer → measure recovery |
| 56 | Throttle drill | Slow broker → fetch latency |
| 57 | Backpressure on 429 | Pause partitions, resume on recovery |
| 58 | Topic describe | kafka-topics.sh --describe (ISR/leader) |
| 59 | Group list | --list to find stale groups |
| 60 | Lesson | Per-partition lag tells the story |
