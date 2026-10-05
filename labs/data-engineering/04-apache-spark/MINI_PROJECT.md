# Apache Spark — MINI PROJECT

## Project: Ad-hoc Clickstream Analytics Engine

A small Spark job suite over a synthetic clickstream dataset: sessionization,
funnel, cohort retention, and a top-N leaderboard — plus a plan-reporting mode
that prints the physical plan and stage metrics for every job.

### Scope
- Ingest: generate 5M events with a realistic Zipf key distribution (hot users).
- Jobs: `sessionize`, `funnel`, `retention`, `topN`, `skewDemo`.
- Report: for each job print logical plan, physical plan, shuffle bytes, task time.

### Architecture

```
generate-clickstream (local FS, 5M JSON lines)
   |
   +-- sessionize  : window(session, 30m) -> count, duration   [stateful shuffle]
   +-- funnel      : left-anti + conditional count            [multiple shuffles]
   +-- retention   : join to cohort, distinct dates            [broadcast cohort]
   +-- topN        : flatMap explode + window rank             [single hot key = skew]
   +-- skewDemo    : same as topN, salted, for comparison
```

### Implementation

```java
public final class ClickstreamJobs {

    public static void sessionize(Dataset<Click> clicks) {
        clicks
            .withColumn("ts", col("ts").cast("timestamp"))
            // 30-minute inactivity gap starts a new session
            .withColumn("newSession",
                    col("userId").eqNullSafe(lag("userId").over(w))
                        .or(col("ts").minus(lag("ts").over(w).cast("long")) > 1800)))
            .withColumn("sessionId",
                    sum(when(col("newSession"), 1).otherwise(0))
                        .over(Window.partitionBy("userId").orderBy("ts").rowsBetween(
                                Window.unboundedPreceding(), Window.currentRow())))
            .groupBy("userId", "sessionId")
            .agg(count(lit(1)).as("events"),
                 min("ts").as("start"),
                 max("ts").as("end"),
                 sum(when(col("event").equalTo("purchase"), col("amount"))).as("revenue"))
            .write().mode("overwrite").parquet("out/sessions");
    }

    private static final Window w = Window.partitionBy("userId").orderBy("ts")
            .rowsBetween(Window.unboundedPreceding(), -1);
```

### Skew: detect, then fix

```java
public static void topN(Dataset<Click> clicks) {
    clicks.groupBy("userId").agg(count(lit(1)).as("n"))
         .orderBy(desc("n")).limit(100)
         .write().mode("overwrite").parquet("out/topN");
    // Observe: one stage takes 14x longer than siblings -> the hottest key.
}

public static void topNSalted(Dataset<Click> clicks, int saltBuckets) {
    clicks
        .withColumn("salt", pmod(xxhash64("userId"), lit(saltBuckets)))
        .repartition("userId", "salt")            // spread the hot key across partitions
        .groupBy("userId").agg(count(lit(1)).as("n"))
        .groupBy("userId").agg(sum("n").as("n"))  // second, small aggregation
        .orderBy(desc("n")).limit(100)
        .write().mode("overwrite").parquet("out/topN-salted");
}
```

### Plan report

```java
public static void report(SparkSession spark, String label, Dataset<?> df) {
    System.out.println("== " + label);
    df.explain(true);                            // logical + optimized + physical
    // The plan to read: Exchange hashpartitioning -> Sort -> Aggregate.
    // If you see Sort before a range-friendly Aggregate, expect O(n log n).
}
```

### Test It

```scala
// (test sketch; run with spark-submit --class ClickstreamJobsTest)
val small = Seq(
  Click("u1", t0, "view", 0.0), Click("u1", t0+600, "view", 0.0),
  Click("u1", t0+3600, "purchase", 25.0), Click("u2", t0, "view", 0.0)
).toDS()
ClickstreamJobs.sessionize(small).count() == 3   // 2 sessions for u1, 1 for u2
```

### Stretch
- Enable Adaptive Query Execution; log the coalesced partition counts before/after.
- Compare `repartition(col)` vs `repartition(n)` for a `time` filter workload.
- Convert the whole funnel to a single Catalyst SQL query and read the plan.

## Deliverables
- [ ] Four jobs over 5M synthetic events
- [ ] Plan report mode: physical plan + shuffle bytes per job
- [ ] Salting fix that measurably reduces max stage time
- [ ] Executor sizing note with a memory budget calculation
- [ ] README explaining each exchange in the physical plan
