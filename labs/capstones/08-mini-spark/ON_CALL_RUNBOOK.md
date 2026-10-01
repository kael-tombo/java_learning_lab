# On-Call Runbook: Mini Spark (Capstone 08)

> Scope: `SparkContext`, `RDD` / `PairRDD` (map/filter/flatMap/reduceByKey/join), `DAGScheduler` (stage building), `TaskExecutor` (thread-pool), `ShuffleManager` (hash partitioning).
> Audience: on-call for batch jobs running on this Java Spark-like engine.

## 1. Job Triage (first 5 minutes)

```
Job slow / stuck / failed?
├─ Fails fast with exception → §2 (logic / stage build)
├─ Stuck with low CPU → §3 (shuffle / skew / executor starvation)
├─ Slow with high CPU/GC → §4 (partitioning / memory)
└─ Wrong results, fast → §5 (semantics: union/intersection/join)
```

Capture: app name (`SparkContext` name), job/stage IDs from `DAGScheduler` status, partition count, input size, last green run's stage timings.

## 2. Runbook: Fast Failure (Stage Build / Task Exception)

**Symptoms:** `DAGScheduler` job submission throws, stages never start, `TaskExecutor` failure counter jumps.

**Steps:**
1. Read the stage that failed to build: a `reduceByKey`/`join`/`groupByKey` forces a shuffle boundary — a missing partitioner or mismatched key type surfaces here, not in `map`/`filter`.
2. Check `TaskExecutor` batch submission result: all tasks failing identically → deterministic user-function bug (e.g., NPE in `map` lambda, `reduce` on empty RDD returning `Optional.empty` unhandled). Fix the function, not the scheduler.
3. Check `SparkContext.textFile`/`parallelize` input: empty input + `reduce`/`join` produces silent wrong-success; validate input non-empty before rerun.
4. Roll back the job code to the last green version first; debug the new transformation logic offline.

## 3. Runbook: Stuck Job (Shuffle / Skew / Starvation)

**Symptoms:** stages start but never finish, executors idle, no errors.

**Steps:**
1. Inspect `DAGScheduler` stage status: one stage at 99% with a few tasks running forever → **data skew** (one `reduceByKey` key dominates). Mitigate by salting the hot key or increasing partitions for that stage, then rerun.
2. Inspect `ShuffleManager` blocks: readers waiting on missing shuffle blocks → writer stage actually failed silently; check writer-stage task status, not the waiting readers.
3. Check `TaskExecutor` pool: parallelism set too low (`local[1]`-style) serializes a wide shuffle — raise parallelism to ≈ 2–3× CPU cores for the rerun.
4. Kill the stuck job before rerunning — duplicate jobs double-write shuffle blocks and confuse diagnosis.

## 4. Runbook: Slow Job (High CPU / GC Pressure)

**Symptoms:** job completes but 3–10× slower than baseline, heavy GC, executor OOM retries.

**Steps:**
1. Check partition count in `ShuffleManager` (configurable partitions): too few → giant partitions → GC hell; too many (10k+ on small data) → scheduling overhead dominates. Adjust toward ~100–200 MB per partition.
2. Look for `groupByKey` where `reduceByKey` suffices: `groupByKey` ships all values across the shuffle; `reduceByKey` pre-aggregates. This single change is the most common 10× fix.
3. Check `flatMap` fan-out: an exploding `flatMap` (e.g., tokenizing huge documents) multiplies shuffle write volume — cap or filter upstream before the shuffle.
4. For repeated actions on the same RDD (`count` then `collect`), the engine recomputes lineage each time — restructure to a single action pass during the incident window rather than tuning GC flags.

## 5. Runbook: Wrong Results

- `union`/`intersection`/`distinct` semantics differ from SQL UNION: check for duplicate handling assumptions.
- `leftOuterJoin` with missing keys yields empty optionals — NPE handlers that assume presence produce wrong-fast results.
- `sortByKey` ordering depends on key comparator, not insertion order — verify with a small deterministic fixture, not the full dataset.

## 6. Post-Incident Checklist

- [ ] Failing stage ID + task error sample archived
- [ ] Partition count and skew key (if any) recorded
- [ ] Shuffle read/write volumes before/after attached
- [ ] Rerun verified against last-green stage timings
- [ ] Action items: skew test fixture, partition sizing guide, `reduceByKey`-over-`groupByKey` lint
