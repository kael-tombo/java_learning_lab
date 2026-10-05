# MATH FOUNDATION — The Maths You Actually Need

Not a data-science course. These are the seven calculations that decide whether
a pipeline is fast, cheap, and stable.

## 1. Throughput and partitioning

Records are produced at rate `R` (records/sec) with mean serialized size `B`
bytes. The cluster must sustain `R x B` bytes/sec of ingest.

```
target_MBps  = R * B / 1_048_576
partitions   = ceil(target_MBps * headroom / (max_MBps_per_broker * brokers))
```

The two headroom choices:

- **Consumer parallelism headroom**: `partitions >= max concurrent consumers
  you will ever need`. More consumers than partitions means idle consumers.
- **Growth headroom**: multiply by 2-3x. Re-partitioning a live topic is a
  migration, so buying it up front is cheaper.

Worked example: 22,000 events/sec, 420 bytes/event, 6 brokers, 40 MB/s per
broker comfortable limit.

```
target = 22000 * 420 / 1048576 = 8.8 MB/s
partitions = ceil(8.8 * 3 / (40 * 6)) = 1
```

One partition, which is wrong for a different reason: this feeds a Flink job
with parallelism 96, and one partition gives parallelism 1. So the binding
constraint here is parallelism, not bandwidth:

```
partitions = max(throughput_need, max_consumer_parallelism) = 96 -> rounded to 96
```

**The lesson**: compute both constraints and take the max. Almost everyone
computes only the bandwidth one.

## 2. Little's law — the whole reason queues exist

```
L = lambda * W
```

`L` = items in a system, `lambda` = arrival rate, `W` = time in the system.

If arrivals are 40,000/sec and each item takes 2ms of work, then `L = 80` items
must be in flight. If you size a consumer pool for 20, the remaining 60 sit in
a queue, and *queueing delay grows without bound* as utilization approaches 1.

The practical version:

```
queue_delay explodes when utilization > 0.7
```

So: size for peak, not mean. Peak/average ratios of 4-8x are normal in
consumer traffic. And measure the service time distribution, not the mean —
p99 service time is what sets the queue depth.

## 3. Latency percentiles and the tail

The mean hides everything that matters. Use percentiles, and remember that
percentiles do not average:

```
p99 of a sum  !=  sum of p99s
p99 of 6 sequential calls ~= 0.99^6 = 94% chance all are under their p99
```

The second line is the one people get wrong. If a request makes 6 network
calls and each has a 1% chance of being slow, then ~6% of requests hit at least
one slow call. So a 6-hop p99 request is dominated by the *worst* hop's tail,
not by the sum of typical hops.

Actions, in order of effectiveness:

1. Remove hops (batching, a single fan-out read, caching).
2. Make the slowest hop's tail shorter (timeout, circuit breaker, hedge).
3. Add parallelism inside the request (only if the tail is contention, not I/O).

## 4. Storage and cost arithmetic

```
bytes_stored = rows * bytes_per_row_after_compression
monthly_cost = bytes_stored / 1e12 * rate_TB
            + bytes_scanned / 1e12 * rate_scan_TB
            + slot_hours * rate_slot_hour
```

Columnar formats change `bytes_per_row` by 5-10x versus row formats, and
column pruning changes `bytes_scanned` by 10-100x. Those are the two big
levers; compression codecs (gzip -> zstd) give another 2-3x on top.

**Deletion math**: deleting a row from a Parquet file usually requires rewriting
the file. So

```
delete_cost = (rows_in_file / rows_deleted_in_file) * file_rewrite_cost
```

Deleting 1 row from a 1M-row file costs a full 1M-row rewrite. This is why
table formats with delete files or MERGE-scope bounds exist, and why "delete
one row" is a design question rather than a statement.

## 5. Probability for anomaly detection

You need three distributions, and the choice matters more than the threshold.

**Mean/standard deviation** is not robust. One historical spike permanently
widens the threshold. Use the **median absolute deviation**:

```
MAD = median(|x_i - median(x)|)
sigma_estimate = 1.4826 * MAD          # consistent with sigma for normal data
```

**Population Stability Index** compares two bucketed distributions:

```
PSI = sum over buckets of (actual_pct - expected_pct) * ln(actual_pct / expected_pct)
```

Rough reading: `PSI < 0.1` stable, `0.1-0.25` moderate shift, `> 0.25`
significant. It is a bucketing choice plus a log, so it is easy to compute and
easy to over-interpret — use it as a trigger, not a verdict.

**False-positive math.** If you run 100 monitors hourly and each has a 1%
false-positive rate, you get 24 false alarms a day. Precision is a function of
both the threshold and the number of monitors, which is why monitor count is a
governance decision.

## 6. Sampling and error bounds

For a proportion `p` with sample size `n`, the standard error of the estimate is:

```
SE(p) ~= sqrt(p * (1 - p) / n)
95% CI ~= p +/- 1.96 * SE(p)
```

Practical consequence for data quality sampling: to detect a 0.1% defect rate
with reasonable confidence you need on the order of `n = 10,000` samples, and
to detect 0.01% you need ~100,000. So a 1% sample of a 100M-row table
(1M rows) reliably detects 0.1% defects — which is exactly why 1% sampling is
the sweet spot for expensive row-level rules.

Use **deterministic** sampling (hash of the key), not `RANDOM()`, so a failure
is reproducible.

## 7. Backoff, retry, and the retry storm

Exponential backoff with full jitter:

```
delay = random(0, min(cap, base * 2^attempt))
```

Full jitter beats equal jitter and beats no jitter for avoiding thundering
herds, because it spreads the retries uniformly instead of clustering them.

Retry budget: if a downstream call has a 2s timeout and you retry 3 times with
backoff, the worst-case request time is `3*2s + backoff` ≈ 8s. This must fit
inside the caller's own timeout, or the caller gives up and the retry is
pointless. When it does not fit, use a circuit breaker to fail fast and a
queue to absorb the load.

```
retry_attempts <= floor((caller_timeout - single_attempt_timeout) / average_backoff)
```

## Quick reference

| Question | Formula | Practical threshold |
|---|---|---|
| Partitions needed | `max(R*B*headroom / per-broker, max parallelism)` | round up to a multiple of broker count |
| Queue safety | utilization `L/(lambda*W_c)` | keep below 0.7 |
| Cost per query | `bytes_scanned * rate + slot_time * rate` | track per team |
| Delete cost | `file_rewrite` unless the format supports delete files | avoid 1-row deletes |
| Anomaly scale | `1.4826 * MAD` | z > 3.5 ticket, z > 5 page |
| Drift | `PSI` | > 0.25 investigate |
| Retry fit | `(caller_timeout - attempt)/avg_backoff` | >= 2 attempts |
