# Lab 13 — Math Foundation: Lag & Queueing

## 1. Lag Growth Equation
- `lag(t+1) = lag(t) + (produce_rate − consume_rate) × Δt`. If produce 2000/s, consume 1500/s → +500/s; 10 min → +300k lag.
- Catch-up time: `T = lag / (consume_max − produce)`. 300k backlog, spare 1000/s → 300s to drain.
- Required consumers: `N = produce_rate / per_consumer_rate`. 2000/400 → 5 consumers (capped by partitions).

## 2. Little's Law for Consumers
- `L = λ × W`: queued messages = arrival rate × wait time. λ=1000/s, W=30s → L=30k lag expected.
- SLO W<30s with λ=1000 → provision for L≥30k buffer; alert before buffer exhausts retention.
- Retention bound: if retention 7d at 1000/s (~604M msgs), lag beyond that = loss. Alert at 10% of retention size.

## 3. Partition Parallelism
- Max throughput = `partitions × per_partition_rate`. 3 partitions × 500/s = 1500/s ceiling regardless of consumer count.
- Utilization: consumers/partitions ≤ 1 useful. 6 consumers on 3 partitions → 3 idle (50% waste).
- Hot key: one partition gets 80% traffic → effective parallelism ~1, not N. Key cardinality must be >> partitions.

## 4. Rebalance Cost
- Rebalance pause `R=30s` every `T=5 min` → availability `1 − R/T = 90%`. Frequent rebalances directly cut throughput 10%+.
- Storm: rebalance every 60s with 30s pause → 50% throughput loss → lag grows even if code is fast enough.
- Fix value: raising `max.poll.interval.ms` to survive p99 processing reduces rebalance rate multiplicatively.

## 5. Batch-Size Trade-off
- `max.poll.records=500` × 20ms/msg = 10s processing > poll interval risk. `50 × 20ms = 1s` safe but 10× more polls (overhead).
- Optimal: `batch × p99_process < 0.5 × max.poll.interval`. p99 20ms, interval 300s → batch up to 7500 safe, but memory bounds lower.

## 6. Worked Example
- 6 partitions, 4 consumers at 300/s each = 1200/s vs produce 1500/s → +300/s. After 20 min lag = 360k.
- Add 2 consumers (6 total): capacity 1800/s, spare 300/s → drain 360k in 1200s (20 min). Double to 12 partitions + 8 consumers for headroom.
