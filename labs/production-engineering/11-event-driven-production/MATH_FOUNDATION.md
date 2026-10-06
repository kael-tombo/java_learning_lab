# Lab 11: Event-Driven Architecture & Kafka in Production — Math Foundation

Event-driven systems fail on arithmetic: throughput per partition, lag growth, retention headroom, and the dual-write window. These are the numbers.

---

## 1. Throughput ceiling: partitions × per-partition rate

```
partition_throughput = min( min(producer_rate_per_partition, consumer_rate_per_partition), broker_network / partitions )
service_throughput    ≤ partitions × partition_throughput × safe_consumer_utilisation
```

Measured per-partition rate: `50 MB/s`, `20,000 msg/s` (whichever is lower, given 4 KB messages = 80 MB/s so messages win):
```
partitions = 6, producer limit = 120,000 msg/s
consumer capacity = 6 × 20,000 = 120,000 msg/s
with 60% consumer utilisation:  6 × 20,000 × 0.6 = 72,000 msg/s usable
```
Peak demand `90,000 msg/s` → **already over**; needed partitions `ceil(90,000 / (20,000 × 0.6)) = 8`, and only if the consumer is the current limit.

**Conclusion**: partition count is a capacity decision that is expensive to change later, and consumer headroom must be explicit (2× peak).

---

## 2. Lag growth and drain time

```
lag_growth_rate = produce_rate − consume_rate
drain_time      = lag / (consume_rate − produce_rate)      if consume_rate > produce_rate
```

Produce `90,000/s`, consume `72,000/s`:
```
lag_growth = 18,000 msg/s
after 10 min:  lag = 18,000 × 600 = 10.8M messages
```

Recovery attempt at full capacity (`consume = 120,000/s`):
```
drain_time = 10.8M / (120,000 − 90,000) = 10.8M / 30,000 = 360 s = 6 min
```

Retention requirement:
```
max_tolerable_outage = 60 min
bytes_required = 90,000 msg/s × 3,600 s × 4 KB × safety(2)
               = 2.6 TB          →  retention.bytes ≥ 2.6 TB
```
If `retention.bytes = 500 GB`, data is lost after:
```
survival = 500 GB / (90,000 × 4 KB) = 500e9 / 360e6 ≈ 1,388 s ≈ 23 min
```
So a 60-minute consumer outage becomes **silent data loss at 37 minutes**. This is the single most important retention calculation in the lab.

---

## 3. Rebalance storm arithmetic

```
poll_cycle_time = records_per_poll × processing_time_per_record
rebalance iff poll_cycle_time > max.poll.interval.ms
```

`max.poll.records = 500`, downstream latency rose to `800 ms` per record:
```
poll_cycle = 500 × 0.8 = 400 s = 400,000 ms > 300,000 ms  →  kicked out
```
Consequences per cycle:
```
records processed before kick ≈ 300,000 / 800 = 375   (then discarded — offsets not committed)
throughput_effective = 375 / (revoke + assign + poll) ≈ 375 / (say 20 s) = 19 records/s
lag_growth = 90,000 − 19 ≈ 89,981 msg/s  →  total stall
```
Fixes, with numbers:
```
option A: max.poll.records = 100 →  poll_cycle = 80 s < 300 s   ✓
option B: max.poll.interval.ms = 900,000 →  poll_cycle = 400 s < 900 s  ✓
option C: pause/commit/resume → cycle independent of batch size  ✓ (preferred)
```
Note option B increases the maximum data-loss window on a crash from 5 min to 15 min — the trade is recovery time against duplication/exposure.

---

## 4. Fan-out and consumer-group economics

```
consumers_in_group ≤ partitions               (extra consumers idle)
total_broker_read_load = Σ_groups (group_rate × bytes_per_msg)
group_cost = broker_read + broker_fetch + consumer_cpu
```

Topic with 6 partitions and 4 consumer groups (search, billing, analytics, archive):
```
partitions per group = 6   → all 4 groups read all 6 partitions independently
fan-out factor = 4
broker_network_load = 4 × production_rate
```
An archive group running 40,000 msg/s consumes 40,000 × 4 KB = 160 MB/s of broker egress **forever**, to serve a workload nobody queries. Options: `sampling` (keep 1%), tiered storage, or a compacted derived topic.

Partition–consumer table:

| Partitions | Consumers in group | Effective parallelism | Idle consumers |
|---|---|---|---|
| 6 | 3 | 3 | 0 |
| 6 | 6 | 6 | 0 |
| 6 | 12 | 6 | 6 |
| 12 | 12 | 12 | 0 |

---

## 5. Idempotency and dedup-table sizing

```
dedup_rows = event_rate × dedup_retention
```

`event_rate = 90,000/s`, dedup retention 7 days:
```
rows = 90,000 × 604,800 = 5.4 × 10^10 rows
at 100 bytes/row → 5.4 TB   →  not affordable on the hot path
```
Practical designs:
```
offset-based dedup (partition,offset) only  →  rows = partitions × retention_seconds × rate... still large
bounded-window dedup: dedup_key unique index on (consumer, event_id) with TTL = max_possible_redelivery_window
   e.g. 24 h  →  90,000 × 86,400 = 7.8 × 10^9 rows  →  still large
   →  use a probabilistic structure (e.g. a Redis SET with TTL, or a 2-hour TTL)
```
**Conclusion**: idempotency must be bounded by the maximum redelivery window, not by the maximum retention. Consumer rebalances and relay retries redeliver within minutes/hours, not days. A 2–24 h dedup TTL is the standard answer; make it explicit.

Cheaper alternative when the business key is naturally unique:
```
INSERT INTO effects (payment_id, ...) ON CONFLICT DO NOTHING
```
zero extra rows, because the effect table is already the dedup table.

---

## 6. Outbox relay sizing

```
relay_throughput = batch_size / (query_ms + publish_ms)
max_sustainable_event_rate = relay_throughput × safety
```

`batch = 500`, query 15 ms, publish 8 ms/batch of 500 with `linger.ms=5`:
```
cycle = 23 ms  →  500/0.023 = 21,700 events/s
```
Event rate at peak `18,000/s`: utilisation `18,000/21,700 = 83%` — too tight. With `batch = 2,000`:
```
cycle = 15 + 20 = 35 ms  →  2,000/0.035 = 57,000 events/s  →  utilisation 32%  ✓
```
Publication lag (time from DB commit to broker acknowledgement):
```
p50_lag ≈ cycle/2 + linger.ms = 17 + 5 = 22 ms  →  fine for most domains
```
If sub-100 ms propagation matters, move to CDC (WAL → broker), which removes the polling cycle entirely at the cost of operating Debezium/connectors.

---

## 7. Ordering and partition expansion

```
partition(p) = murmur2(key) mod P     (producer default partitioner)
```

`P = 6` → `P = 12`:
```
hash(key) mod 6  ≠  hash(key) mod 12 for most keys
P(pairs of records for the same key landing in the same partition) ≈ 1/2
```
So about half of all keys have their pre-expansion and post-expansion records split across partitions — ordering for those keys is broken **irreversibly**, because the old records are already written under the old mapping.

Migration options:

| Option | Ordering preserved | Cost |
|---|---|---|
| Add partitions in place | No (≈50% of keys split) | zero |
| Drain → add → reseed | Yes | downtime/complexity |
| New topic + dual-write + cutover | Yes if sequenced | temporary double cost |
| Relax ordering (per-key where needed) | n/a | product change |

If ordering matters for a key, the only correct answer is a new topic (or single-partition topic per ordered stream).

---

## 8. Hot partition load

```
skew_ratio = max_partition_rate / mean_partition_rate
throughput_lost = (1 − 1/skew_ratio) × capacity
```

`mean = 90,000/12 = 7,500 msg/s`; one hot key carries `40,000/s`:
```
max_partition_rate = 40,000  →  skew_ratio = 5.3
effective_parallelism = 12 − 1 (the hot partition is the limiter) = 11 usable
hot_partition_determines_throughput = 40,000 < 90,000  →  not yet the limit, but at 2× growth it is
```

Salting: append a random suffix `0..N-1` to the key:

```
salts = ceil(hot_rate / target_per_partition)
at hot_rate = 200,000/s, target 7,500 → salts = 27
throughput becomes 200,000/27 = 7,400 per salted key  ✓
cost: no per-key ordering  →  any downstream needing order must re-sequence or read one salt
```

---

## 9. DLT sizing and detection latency

```
dlt_rate = error_rate × event_rate
detection_latency = DLT_depth / dlt_rate       (time until an operator notices via depth)
```

`error_rate = 0.1%`, `event_rate = 90,000/s`:
```
dlt_rate = 90 messages/s = 7.8M/day
if an operator only looks when depth > 1M  →  detection_latency = 1M/90 = 11,111 s = 3.1 hours
```
So alerting on depth alone with a 1M threshold gives you a 3-hour detection. Alert on the **rate** too, with a 5-minute threshold:
```
5 min of DLT at 90/s = 27,000 messages →  threshold 20,000 in 5 min  →  page
```

---

## 10. Cost of an event-driven design

```
monthly_cost = brokers × storage_months × replication_factor × rate
              + egress + consumer_compute
```

`1 TB/month`, 3 brokers, RF=3, 30-day retention:
```
storage = 1 TB × 3 (replication) = 3 TB
monthly = 3 TB × $0.10/GB-month ≈ 3,072 × $0.10 ≈ $307   →  ~$400/month with overhead
```
Add the fan-out cost of 4 consumer groups reading that volume at `$0.09/GB` egress internally:

```
egress to archive group = 1 TB × $0.09 ≈ $90/month — and it dominates the value delivered
```

Compare with the synchronous alternative: N services × M calls/s × cost per call — usually larger. **Conclusion**: the economic case for event-driven is decoupling and elasticity; cost is a secondary argument, and retention/fan-out are where it surprises people.

---

## 11. Saga availability

```
saga_success = Π step_success_i      (each step must succeed to complete)
compensations execute on failure; each must also succeed
```

6-step saga with `s_success = 0.999` per step:

```
P(forward completion) = 0.999^6 = 99.4%
P(needs compensation) = 0.6%  →  at 1,000 sagas/s, 6 compensations/s
compensation_capacity_must_handle = compensation_rate × avg_compensation_cost
```
If a compensation itself fails (it is a distributed call with the same failure modes), you need a *compensating* DLT and manual reconciliation. Budget for it: `P(partial saga) ≈ 0.6% × P(compensation fails) = 0.6% × 1% = 6 per 100k sagas`.

---

## 12. Backlog vs latency trade-off

```
consumer_buffer = batch_size × avg_msg_bytes
consumer_lag_seconds = lag / consume_rate
```

Sizing for the target lag:
```
batch_size = lag_target × consume_rate / 60
```

Target lag < 5 s, consume rate 72,000/s:

```
batch_size = 5 × 72,000/60 = 6,000 records/batch
memory ≈ 6,000 × 4 KB = 24 MB  →  fine
poll_cycle = 6,000 × 8 ms = 48 s < 300 s  ✓
```

Note how this interacts with rebalances: larger batches raise `poll_cycle`, so the binding constraint is `batch × processing_time < max.poll.interval.ms`.

---

## 13. Quick drills

1. 6 partitions, `20,000/s` per partition, 60% utilisation. Usable throughput? **Answer: 72,000 msg/s. Peak 90,000 → need ≥ 8 partitions.**
2. Produce 90,000/s, consume 72,000/s for 10 min. Lag? **Answer: 10.8M messages.**
3. `retention.bytes = 500 GB`, 90,000 msg/s × 4 KB. Survival time? **Answer: ~23 min. A 60-min outage loses data.**
4. `max.poll.records=500`, 800 ms/record. Storm? **Answer: 400 s > 300 s → yes. Set records=100 or interval=900 s, or pause/commit/resume.**
5. 4 consumer groups on 6 partitions. Fan-out? **Answer: 4× broker read load; extra consumers beyond 6 idle.**
6. Dedupe at 90,000/s for 7 days. Rows? **Answer: 5.4×10^10 → use a bounded TTL (hours) or natural business-key uniqueness.**
7. Outbox batch 500 → 21,700 events/s. Safe for 18,000/s peak? **Answer: 83% utilisation — too tight. Batch 2,000 → 57,000/s.**
8. Expand 6 → 12 partitions. Ordering? **Answer: broken for ~50% of keys (hash mod changes). Only a new topic preserves it.**
9. Hot key at 40,000/s, mean 7,500. Skew ratio? **Answer: 5.3×. Salting with 27 salts normalises it but destroys per-key order.**
10. DLT at 90/s, depth threshold 1M. Detection latency? **Answer: 3.1 hours. Alert on rate (e.g. 20k/5min).**

---

## 14. Formulas worth memorizing

| Formula | Use |
|---|---|
| `throughput ≤ partitions × per_partition × utilisation` | sizing partitions and consumer headroom |
| `drain_time = lag/(consume − produce)` | recovery planning |
| `retention ≥ max_outage × rate × safety` | the retention setting that prevents silent loss |
| `poll_cycle = records × processing_time < max.poll.interval.ms` | the rebalance-storm inequality |
| `fan_out = number_of_consumer_groups` | broker load and cost |
| `skew_ratio = max_partition/mean` | hot-key detection |
| `dedup_ttl = max_possible_redelivery_window` | bounded idempotency |
| `outbox_cycle = query + publish`, `rate = batch/cycle` | relay sizing |
| `P(saga needs compensation) = 1 − Π s_i` | saga reliability and compensation capacity |
| `detection_latency = DLT_depth/dlt_rate` | alert on DLT rate, not just depth |
