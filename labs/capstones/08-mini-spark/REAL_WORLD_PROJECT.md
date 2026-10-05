# Mini Spark — REAL WORLD PROJECT

## Context

A media company runs 1,100 Spark jobs per day on a shared EMR cluster. The
platform team inherited 4.3PB of Parquet, 1,400 tables, and a bill that grew
2.9x in a year while data grew 1.7x. There is no per-job cost attribution, no
physical-design standard, and a job-processing queue where one badly skewed
job delays 40 others. You own the compute platform.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Cluster | 400-node EMR, 3.6PB, on-demand + spot, 200-slot shared YARN queue |
| Jobs | 1,100/day, 90 concurrent peak, 340 in the critical path before 07:00 |
| Data | 4.3PB Parquet, 1.2B rows/day, 1,400 tables |
| Bill | $1.9M/month: 41% shuffle, 28% scan, 19% storage, 12% idle |
| Problems | small files (55% < 1MB), unpartitioned tables, no cost attribution |
| Constraint | no downtime; 4 teams share the cluster with no isolation |
| Compliance | SOX; the finance close depends on jobs finishing on time |

## Architecture (target)

```
physical design standard
  - partitioning: date + bucket
  - file size: 256MB-1GB
  - codec: zstd + dictionary
  - no SELECT *: column projection is mandatory
        |
   +----+--------------------------------------------+
   |              |                |                |
 team A       team B           team C           team D
 (ingest)      (ml)          (analytics)       (bi)
   |              |                |                |
   +--> Spark 3.5 shared cluster, partitioned queue by SLO
          |-- critical pool: reserved 40 slots, finance close
          |-- standard pool: 120 slots
          |-- backfill pool: 40 slots, off-peak
        AQE on: coalesce + skew split + BHJ conversion
        cost attribution by job tag
```

## Key Implementation — the three cost problems, in order of size

**Problem 1: shuffle is 41% of the bill ($779k/month), and it is mostly
avoidable shuffle.** Not shuffle that a distributed computation needs, but
shuffle caused by unpartitioned tables and missing predicate pushdown.

```java
/**
 * The dominant pattern, found by reading plans rather than by profiling CPU:
 * a job scans 400GB and shuffles 180GB to compute a daily aggregate, when the
 * table is unpartitioned by date so a `WHERE event_date = X` filter prunes
 * nothing.
 *
 * Fix: a physical design standard applied to the 60 largest tables first,
 * where the effect is measurable, and a CI check that blocks a query without
 * a partition predicate on a partitioned table.
 */
public final class PartitionPredicateLint {
    /**
     * The rule, and the reason it is a lint rather than advice: an unfiltered
     * scan on a 400GB table is 5x the cost of a filtered one, and the author
     * sees no difference in the result.
     */
    static final List<Rule> RULES = List.of(
        new Rule("filter present on partitioned column",
                 q -> q.isPartitioned() && !(q.hasPredicateOn(q.partitionColumns())),
                 "add a predicate on a partition column; this scan reads ~5x more than needed"),
        new Rule("no SELECT *",
                 q -> q.projectsAllColumns(),
                 "columnar scan cost scales with projected columns"),
        new Rule("join key aligns with partitioning",
                 q -> q.isShuffleJoin() && !q.joinsOnPartitionColumns(),
                 "shuffling both sides of a partitioned join; consider a bucketed table or broadcast"),
        new Rule("subtree can fuse",
                 q -> q.hasUdf() && q.inputs() > 1,
                 "a UDF between two operations prevents whole-stage codegen"));
}
```

| Table group | Tables | Change | Shuffle bytes/day | Time |
|---|---|---|---|---|
| Finance marts | 14 | partition by `book_date`, cluster by `entity` | 410GB -> 22GB | 94% |
| ML features | 22 | partition + Z-order on the label column | 180GB -> 61GB | 66% |
| Marketing extracts | 18 | partition by `event_date` | 96GB -> 34GB | 65% |
| Remaining 1,346 | 1,346 | lint applied, no re-partition yet | unchanged | — |

The remaining tables are handled by the lint rather than a rewrite, because a
1,346-table re-partitioning is a quarter of work and the top 54 tables were
73% of the shuffle.

**Problem 2: 55% of files are under 1MB, and it costs listing time, task time,
and cluster memory.** Files come from Spark's default 128MB partition size on
small hourly increments, and from two CDC writers that repartition to 200.

```java
/**
 * Two fixes, and the second matters as much as the first: a compaction job AND
 * a write-side rule. Compaction alone returns to 55% within a month, which is
 * what happened twice before this project.
 */
public final class FileHealthPolicy {
    static final long TARGET_FILE_BYTES = 512L * 1024 * 1024;
    static final long MIN_FILE_BYTES = 32L * 1024 * 1024;

    public record Verdict(String table, long fileCount, long smallFileShare,
                          long avgFileBytes, Action action) {}

    public enum Action { COMPACT, REWRITE_WRITER, INSPECT, OK }

    public Verdict evaluate(String table, FileStats stats, boolean hasCustomWriter) {
        if (stats.fileCount() < 500) return new Verdict(table, stats.fileCount(), 0, 0, Action.OK);
        double smallShare = stats.smallFiles() / (double) stats.fileCount();
        if (smallShare > 0.20) {
            // If the writer is custom, fixing the writer prevents recurrence.
            return new Verdict(table, stats.fileCount(), smallShare, stats.avgBytes(),
                    hasCustomWriter ? Action.REWRITE_WRITER : Action.COMPACT);
        }
        return new Verdict(table, stats.fileCount(), smallShare, stats.avgBytes(), Action.OK);
    }
}
```

| Metric | Before | After |
|---|---|---|
| Files < 1MB | 55% | 6% |
| Average file size | 41MB | 340MB |
| Median planning time for a partitioned scan | 2.4s | 0.19s |
| Cluster metadata memory | 61GB | 24GB |
| Write-side enforcement | none | 2 CDC writers fixed, CI lint added |

**Problem 3: 12% of the bill is idle.** Clusters sized for peak, running at
mean. The ratio is 4.1x here, which is normal, and the fix is right-sizing
plus a queue structure that makes the tail someone else's problem.

```java
/**
 * The insight that changed the queue design: the problem is not idle compute,
 * it is idle compute at the WRONG time. A cluster sized for the 00:00 peak is
 * mostly idle for 23 hours, and the cost is the same. The queue structure that
 * works is by SLO, not by team: the finance close gets reserved capacity, the
 * backfills get off-peak capacity, and everyone else shares what is left.
 */
public final class QueuePolicy {
    static final Map<String, Pool> POOLS = Map.of(
        "critical",   new Pool(40,  "finance close and SOX reporting; admission-controlled"),
        "standard",   new Pool(120, "default; 40 concurrent per team cap"),
        "backfill",   new Pool(40,  "off-peak only 20:00-05:00 UTC; shadow writes only"));

    /** A misbehaving job must not be able to consume a whole pool. */
    static final int MAX_CONCURRENT_PER_TEAM = 40;
    static final Duration MAX_JOB_RUNTIME = Duration.ofHours(6);
}
```

| Metric | Before | After |
|---|---|---|
| Idle cluster time | 12% of bill | 3.1% |
| Critical-path completion before 07:00 | 84% | 99.4% |
| Jobs delayed by a straggler | ~340/week | 11/week |

## Key Implementation — skew detection, because it is the incident you get paged for

A regression in one job (40 min to 9 hours) turned out to be key skew that had
been invisible until a data distribution shifted. A monthly holiday changed the
key distribution and no plan-level change was involved.

```java
/**
 * Skew is a data property, not a code property. The only reliable detector is
 * per-task metrics within a stage: max/median task time. A stage whose ratio
 * exceeds 5x has a straggler, and the next question is always "what is in that
 * key" rather than "what changed in the code".
 */
public record StageHealth(int stageId, long maxTaskMillis, long medianTaskMillis,
                          long p95TaskMillis, long shuffleBytes, int tasks) {
    public double imbalance() {
        return medianTaskMillis == 0 ? Double.POSITIVE_INFINITY
                                     : (double) maxTaskMillis / medianTaskMillis;
    }
    public boolean skewSuspected() { return imbalance() > 5.0; }
    public String diagnose() {
        return String.format("stage %d imbalance %.1fx, shuffle %,d bytes, %d tasks",
                stageId, imbalance(), shuffleBytes, tasks);
    }
}

public final class SkewGuard {
    /**
     * Where the guard actually pays: it runs in CI against a representative
     * data sample, so a new skewed key is caught before it ships, rather than
     * discovered at 02:00 on the day a holiday changes the distribution.
     */
    public List<String> auditOnSample(List<StageHealth> stages) {
        return stages.stream().filter(StageHealth::skewSuspected).map(StageHealth::diagnose).toList();
    }
}
```

The two fixes that were applied, in order of preference:

| Fix | When it works | Example |
|---|---|---|
| Pre-aggregate at the source | when the hot key is itself a missing sum | a series_id with 9% of rows: group by (bucket_hour, series_id) first, then by series_id. 24x more keys, each small |
| Salt | when the hot key cannot be reduced | deterministic `salt = pmod(xxhash64(key), 16)`, then a second small aggregation |
| AQE skew join | for skewed joins, not skewed aggregations | only helps joins; a skewed groupBy still needs one of the above |

## Key Implementation — cost attribution, because reduction needs a target

```sql
-- Every job carries a tag. This query is the entire attribution layer, and it
-- is the reason the optimisation work could be prioritised at all.
SELECT TAG_NAME, TEAM, SUM(CREDITS_USED) AS credits,
       SUM(BYTES_SCANNED) / POW(1024,4) AS tib_scanned,
       SUM(SHUFFLE_WRITE_BYTES) / POW(1024,4) AS tib_shuffled,
       SUM(EXECUTOR_RUN_TIME)/60000 AS executor_hours
  FROM SPARK_HISTORY.events
 WHERE start_timestamp >= CURRENT_DATE() - 30
 GROUP BY TAG_NAME, TEAM
 ORDER BY credits DESC;
```

The first week of output found two things no one had asked about: a single
dashboard refresh costing $4,100/month, and 340 jobs running with an empty
`spark.sql.shuffle.partitions` override set to 20,000 — 200x the default, on
tables that produce 12 partitions.

| Metric | Before | After |
|---|---|---|
| Jobs with cost attribution | 0% | 100% |
| Shuffle partitions overridden to 20,000 | 340 jobs | 0 |
| Monthly credit spend | $1.9M | $1.19M (-37%) |
| Spark share of the bill | 41% | 23% |

## Measured outcomes

| Metric | Day 0 | Day 180 |
|---|---|---|
| Monthly bill | $1.9M | $1.19M (-37%) |
| Shuffle as a share of compute | 41% | 19% |
| Files under 1MB | 55% | 6% |
| Average file size | 41MB | 340MB |
| Median planning time (partitioned scan) | 2.4s | 0.19s |
| Idle cluster cost | 12% | 3.1% |
| Critical-path on-time completion | 84% | 99.4% |
| Straggler-caused delays per week | ~340 | 11 |
| Tables with a physical design standard | 54 | 380 |
| Jobs with cost attribution | 0% | 100% |

The bill fell 37% while data volume grew 18% over the same period.

## Failure Modes and the Runbook

1. **A job with 20,000 shuffle partitions.** Symptom: a stage schedules 20,000
   tasks of which 19,990 are near-empty; planning takes minutes. Fix: AQE
   coalescing, plus the CI lint that blocks a partition override above a
   threshold without a written justification.
2. **Skew from a distribution change.** Symptom: one stage's time increases 10x
   with no deploy. Fix: the SkewGuard ratio, then look at the key distribution
   for that date range. Assume the data changed, not the code.
3. **Small files return after a writer change.** Symptom: file count climbs 10x
   in a week. Fix: the FileHealthPolicy distinguishes "compact this" from
   "rewrite this writer", and the second case is the one that recurs.
4. **A job holds a pool.** Symptom: other jobs queued for hours. Fix: per-team
   concurrency caps and a max runtime enforced by the queue, not by the job.
5. **A partition-filtered scan reads a full table.** Symptom: cost spike, plan
   shows no partition pruning. Fix: the lint, plus a check for a predicate on a
   *transformed* column, which looks filtered and is not.
6. **Spot nodes reclaimed mid-stage.** Symptom: `FetchFailedException` retries,
   then a stage re-run. Fix: external shuffle tracking so a stage does not
   recompute, plus on-demand capacity for the critical pool only.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Spark's execution is built on a DAG of stages separated by shuffles; narrow
  dependencies pipeline within a stage and wide dependencies (shuffles) form
  stage boundaries, which is what makes whole-stage codegen possible.
  - Reference: https://spark.apache.org/docs/latest/rdd-programming-guide.html
  - Reference: https://spark.apache.org/docs/latest/job-scheduling.html
- Spark SQL's optimizer performs predicate pushdown, column pruning, constant
  folding, and join selection, and Adaptive Query Execution coalesces shuffle
  partitions, converts sort-merge joins to broadcast joins, and splits skewed
  partitions at runtime.
  - Reference: https://spark.apache.org/docs/latest/sql-performance-tuning.html
  - Reference: https://spark.apache.org/docs/latest/sql-programming-guide.html
- Parquet's columnar layout, row groups, and statistics enable column pruning
  and file skipping, which is why a physical file standard is one of the
  highest-leverage cost interventions on a lakehouse.
  - Reference: https://parquet.apache.org/docs/
  - Reference: https://parquet.apache.org/docs/file-format/
- The Spark HistoryServer and event logs record per-task metrics, which is what
  makes per-stage task-time distributions (and therefore skew detection)
  available rather than guessed at.
  - Reference: https://spark.apache.org/docs/latest/monitoring.html
  - Reference: https://spark.apache.org/docs/latest/spark-standalone.html

## Deliverables

- [ ] Physical design standard: partitioning, file size, codec, projection, with
      the measured effect for each
- [ ] CI lints: partition predicate required, no `SELECT *`, no unjustified
      partition overrides, bucket alignment for partitioned joins
- [ ] Partition + cluster applied to the top 60 tables, with before/after
      shuffle bytes and runtime
- [ ] File health policy distinguishing compaction from writer fixes, plus
      write-side enforcement so it does not regress
- [ ] SLO-based queue with reserved critical capacity, per-team caps, and
      enforced max runtime
- [ ] Skew guard in CI against a representative sample, plus AQE config
- [ ] Cost attribution by tag and team, with the per-team budget
- [ ] Before/after table for bill, shuffle share, file health, planning time,
      idle cost, on-time completion
- [ ] Runbook for the six failure modes
