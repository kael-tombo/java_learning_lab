# Apache Spark — REAL WORLD PROJECT

## Context

A media streaming company runs a 6PB-scale lake on S3 and runs ~1,200 Spark
jobs per day for the data platform and the ML feature pipelines. A single
overnight job regressed from 40 minutes to 9 hours after an unrelated schema
addition. The root cause was not the schema — it was key skew that had been
invisible until the data distribution shifted. You are the engineer who finds
it and prevents a repeat.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Input | 6.2PB Parquet, 1.1B rows/day, hourly incremental jobs |
| Cluster | 400-node EMR, 3.6PB total HDFS/S3 capacity |
| Concurrency | ~1,200 jobs/day, 40-90 concurrent on a 200-slot shared queue |
| Latency | 90% of marts refreshed before 07:00; freshness SLO 1h |
| Cost | $1.9M/month; scan and shuffle dominate |
| Constraint | one shared cluster, no per-team isolation today |

## Architecture

```
bronze (raw append, partitioned by ingest_hour)
   |
silver (conformed + dedupe + SCD2, 200 tables)
   |
gold (marts + aggregates)
   +-- ml feature jobs  -> online store
   +-- BI aggregates    -> dashboard cache
   |
serving: 200-core shared YARN/K8s queue with dynamic allocation on
```

## Key Implementation — the four-line triage that finds skew

Every job is instrumented at the shuffle boundary. The skew detector reads
task metrics and reports imbalance, not just averages.

```java
public record StageHealth(String stageId, long maxTaskMillis, long medianTaskMillis,
                          long shuffleBytes, int tasks) {
    // max/median ratio is the signal: > 5 means someone is waiting on one straggler.
    public double imbalance() {
        return medianTaskMillis == 0 ? Double.POSITIVE_INFINITY
                                     : (double) maxTaskMillis / medianTaskMillis;
    }
    public boolean skewSuspected() { return imbalance() > 5.0; }
}

public final class SkewGuard {
    public static List<String> audit(List<StageHealth> stages) {
        return stages.stream()
            .filter(StageHealth::skewSuspected)
            .map(s -> "stage %s imbalance=%.1fx shuffleBytes=%,d".formatted(
                    s.stageId(), s.imbalance(), s.shuffleBytes()))
            .toList();
    }
}
```

The offending query grouped by `series_id` where one series (a live sports
league) carried 9% of a day's rows into a single reducer. The fix that stuck
was not salting — it was **pre-aggregation at the source**, because the hot key
was itself the result of not summing earlier:

```java
// Before: 1.1B rows -> groupBy(series_id) -> skew
// After: 1.1B rows -> groupBy(bucket_hour, series_id) [uniform, 24x more keys]
//                    -> partial sum -> groupBy(series_id) [each key now small]
Dataset<Row> hourly = events
    .withColumn("bucket", window(col("ts"), "1 hour"))
    .groupBy("bucket", "series_id", "episode_id")
    .agg(sum("watch_seconds").as("secs"));

Dataset<Row> daily = hourly
    .groupBy(functions.date_format(col("bucket"), "yyyy-MM-dd").as("d"), "series_id")
    .agg(sum("secs").as("secs"));                 // shuffle now carries ~24x fewer rows
```

## Join Strategy Selection

| Fact size | Dim size | Strategy | Measured |
|---|---|---|---|
| 1.1B | 12k | Broadcast hash join | 34 min -> 3 min |
| 1.1B | 900M | Sort-merge, partitioned by join key | stable, 2 shuffles |
| 1.1B | 40M | Broadcast failed (OOM), fell back to SMJ and thrashed | set `autoBroadcastJoinThreshold` explicitly |

The silent failure mode worth remembering: a "broadcast" join that exceeds
memory does not fail loudly, it falls back and the stage gets 10x slower. Pin
the threshold instead of inheriting the default.

## Failure Modes and the Runbook

1. **Shuffle fetch failure / `FetchFailedException`.** Symptom: stage retries.
   Cause: executor lost mid-fetch, often OOM. Fix: raise `spark.shuffle.io.maxRetries`,
   size off-heap, and check whether the retry is hiding a real leak.
2. **Spill to disk.** Symptom: `Size of Deserialized Objects` exceeds executor
   memory. Fix: aggregate earlier, use partial aggregation, or up the memory fraction.
3. **Small file explosion** after a wide `repartition(20000)`. Symptom: task
   scheduling time dominates. Fix: coalesce before write, target 128-256MB files.
4. **Data skew in a nightly batch only.** Cause: a holiday or a promo changed the
   key distribution. Fix: the SkewGuard above, plus a scheduled distribution
   assertion so the job fails fast with a clear message.
5. **Dynamic allocation thrashing** — executors decommissioning mid-stage. Fix:
   cap `spark.dynamicAllocation.minExecutors`, and use shuffle tracking so
   decommission can wait for the shuffle to be materialized.
6. **Concurrent job starvation** on the shared queue. Fix: priority by freshness
   SLO, not by team, and cap per-team concurrency.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Spark's execution is built around a DAG of stages separated by shuffles;
  the narrow vs wide dependency distinction determines where stage boundaries fall.
  - Reference: https://spark.apache.org/docs/latest/job-scheduling.html
  - Reference: https://spark.apache.org/docs/latest/rdd-programming-guide.html
- Spark SQL uses Catalyst (analysis, optimization, planning) and Tungsten
  (code generation and memory management), which is why the physical plan is
  the right place to look for performance causes.
  - Reference: https://spark.apache.org/docs/latest/sql-performance-tuning.html
  - Reference: https://spark.apache.org/docs/latest/sql-programming-guide.html
- Adaptive Query Execution coalesces shuffle partitions and can convert sort-merge
  joins to broadcast joins at runtime, and it can split skewed partitions.
  - Reference: https://spark.apache.org/docs/latest/sql-performance-tuning.html#adaptive-query-execution

## Deliverables
- [ ] Stage-level skew detector with an alert threshold
- [ ] Before/after benchmark for the regressed job, with the physical plan diff
- [ ] Join strategy decision table with memory budgets
- [ ] Executor sizing and dynamic allocation configuration with reasoning
- [ ] Runbook for all six failure modes, tested in a sandbox cluster
- [ ] Preventive distribution assertions wired into CI
