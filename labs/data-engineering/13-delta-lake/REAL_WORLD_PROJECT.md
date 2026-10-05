# Delta Lake — REAL WORLD PROJECT

## Context

A subscription company's analytics team adopted Delta Lake for one dashboard,
then for everything. Two years later, 640 of 900 tables are Delta, three
non-Delta formats remain, the log-compaction job is failing on 40 tables, and a
`MERGE` on a 2.1B-row fact table runs for 6 hours and holds a write lock that
blocks the hourly refresh. You own standardizing this and fixing the write
patterns.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Tables | 900 total: 640 Delta, 180 Iceberg, 40 Hudi, 40 Parquet-only |
| Largest fact | 2.1B rows, 41GB Parquet, 340k files before optimization |
| Write pattern | 40 concurrent writers, hourly MERGEs, plus 3 streaming tables |
| Retention | 7 years; time travel used by analysts ~200x/week |
| Log size | 34GB on the largest table, 2.1M log entries |
| Constraint | analysts depend on time travel; cannot shorten retention aggressively |
| Compliance | SOX requires reproducible point-in-time reporting |

## Architecture (target)

```
   +-- writers --+
   |  batch MERGE (hourly, per-partition)     no table-wide locks
   |  streaming append (3 tables)             schema-on-read for late fields
   |  backfill (isolated, clone-then-merge)   never touches the live table
   v
+----------------------------------+
|  DELTA tables (the default)     |
|  _delta_log compaction weekly   |
|  OPTIMIZE nightly on hot facts  |
|  VACUUM after retention floor   |
+----------------------------------+
|  migrations: 40 Hudi / 180 Iceberg / 40 raw Parquet -> Delta
+----------------------------------+
   |                          |
semantic layer            archive (Parquet + manifest, 7y)
```

## Key Implementation — write patterns that do not lock the table

The 6-hour MERGE was a design problem, not a tuning problem: it rewrote the
whole fact table to update 90 minutes of data.

**Pattern 1: partition-scoped MERGE.** Delta's MERGE still rewrites whole data
files, so the fix is to make sure the matched data lives in files that are
already candidates for rewriting.

```java
/**
 * The rule: every MERGE must be able to state, before it starts, which files
 * it can possibly touch. If it cannot, the MERGE is going to rewrite the table.
 *
 * Deterministic file pruning comes from:
 *   - partition values written into the Add action's partitionValues
 *   - per-file stats (min/max) written at write time
 *   - the predicate being pushed into file selection
 *
 * If a MERGE cannot be pruned, split the table by the predicate's leading key.
 */
public record MergeScope(String partitionColumn, Set<String> candidatePartitions,
                         long candidateFiles, long candidateBytes) {
    /** Refuse a MERGE whose scope is a large fraction of the table. */
    public boolean isDangerous(long tableBytes) {
        return tableBytes > 0 && (double) candidateBytes / tableBytes > 0.25;
    }
}
```

**Pattern 2: streaming appends do not MERGE.** The three streaming tables
accumulate an update buffer and apply a bounded, hourly, partition-scoped MERGE
as a separate maintenance job — so the streaming job's own writes are pure
appends, which never conflict.

**Pattern 3: backfill clones, then merges.** A 90-day backfill runs against a
shallow clone; only after a reconciliation check does a single scoped MERGE
promote the result. The live table is readable and writable throughout.

```java
public final class BackfillPromotion {
    public void promote(String table, LocalDate from, LocalDate to) {
        String shadow = table + "__shadow_" + runId();
        lake.clone(table, shadow, /* shallow = */ true, /* since version = */ null);

        // Recompute only the affected partitions in the shadow copy.
        etl.recompute(shadow, from, to);
        validate.reconcile(table, shadow, from, to, tolerance = 0L);

        // Promote with a scoped MERGE: partition values bound the file set.
        lake.merge(shadow, table, eq("date", from, to));
        lake.dropTable(shadow);
        logCompaction.enqueue(table);
    }
}
```

## Log Compaction and File Health

The 2.1M-entry log is not a log problem per se — it is a symptom of one
`MERGE` per hour for 18 months, each adding actions. The real metric is
**operations per data file per day**, and the target is under 1.

| Metric | Before | Target | Action |
|---|---|---|---|
| Files on the largest fact | 340,000 | < 4,000 | `OPTIMIZE` nightly, 1-day Z-order window |
| Log entries | 2.1M | < 50k | `delta.logCompaction` (single-file + 10-day retention) |
| Data-change actions per file per day | 14 | < 1 | compact then `MERGE` at a daily, not hourly, grain |
| Small-file share | 71% | < 5% | `OPTIMIZE` with a target file size of 512MB |
| Query p95 (point lookup scan) | 22s | < 3s | Z-order on the filter columns |

```java
/**
 * Why Z-order helps and where it stops helping: it clusters data by the
 * *leading* columns of the sort specification. A query filtering only on
 * a trailing column gets no pruning from that column.
 */
public record ZOrderSpec(String[] columns, boolean full, int maxFiles) {
    ZOrderSpec {
        if (columns.length < 1) throw new IllegalArgumentException("z-order needs columns");
        // Overlapping specifications in Delta create a layout the optimizer
        // cannot use for both; one spec per table, documented.
    }
    static final ZOrderSpec REVENUE_FACT =
            new ZOrderSpec(new String[]{"date", "country", "channel"}, true, 40_000);
}
```

## Migration of the Non-Delta Tables

The order is not arbitrary: convert by consumption pattern, not by size.

| Wave | Tables | Criterion | Why this order |
|---|---|---|---|
| 1 | 40 raw Parquet | no consumers except one job | lowest risk, fixes the file-health problem first |
| 2 | 40 Hudi | has incremental jobs that will benefit most | immediate win, and the Hudi version pin becomes a non-issue |
| 3 | 180 Iceberg | already has manifest/snapshot semantics | mostly a metadata migration; the file layout survives |
| 4 | — | (640 Delta) | no action; standardize conventions here |

Every wave is: dual-write for one release, compare row counts and checksums
per partition, cut over, keep the source table read-only for 30 days. The
read-only tail is what makes rollback a metadata operation.

## Failure Modes and the Runbook

1. **Log compaction fails on a table.** Symptom: reads slow down, `_delta_log`
   has millions of tiny files. Fix: check for a stale writer holding a version
   lease; compaction cannot run while a concurrent transaction is unresolved.
2. **Concurrent write conflict storm.** Symptom: `ConcurrentAppendException`
   retries. Cause: two writers MERGE the same partition hourly. Fix: partition
   ownership — one writer per (table, partition range) — enforced in CI.
3. **MERGE that rewrites the whole table.** Symptom: a 6-hour job and a blocked
   refresh. Fix: assert the merge scope before execution; refuse above 25% of
   table bytes and require a partitioning change.
4. **Time travel broken after vacuum.** Symptom: an analyst's `VERSION AS OF 90`
   query fails. Cause: files vacuumed while a snapshot still referenced them.
   Fix: retention floor = maximum age any reader needs; vacuum honours the
   oldest live snapshot, not the file's mtime.
5. **Schema evolution surprise on a streaming table.** Symptom: a new field
   appears with nulls and a downstream cast fails. Fix: schema-on-read for
   late-arriving fields plus a compatibility check at the sink.
6. **Small files from a Spark repartition.** Symptom: file count climbs 10x
   overnight. Fix: `OPTIMIZE` scheduled by file count, not by date; and a
   write-side minimum partition size check.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Delta Lake provides ACID transactions over object storage with time travel,
  schema evolution, and the `_delta_log` transaction history, so readers can see
  prior versions and writers get optimistic concurrency control.
  - Reference: https://docs.delta.io/latest/index.html
  - Reference: https://docs.delta.io/latest/delta-batch.html
  - Reference: https://github.com/delta-io/delta
- Apache Iceberg is the other widely used open table format, with snapshots,
  hidden partitioning, and schema evolution; multi-engine support is its main
  advantage over a single-vendor format.
  - Reference: https://iceberg.apache.org/
  - Reference: https://iceberg.apache.org/docs/latest/
- Parquet is the underlying columnar file format for both, so column pruning and
  statistics-based file skipping are what make these table formats fast.
  - Reference: https://parquet.apache.org/docs/file-format/

## Deliverables
- [ ] Write-pattern policy: partition-scoped MERGE, append for streaming, clone-then-promote for backfill
- [ ] Merge-scope guard that refuses a MERGE touching >25% of table bytes
- [ ] Log compaction + OPTIMIZE schedule with before/after metrics
- [ ] Z-order specification per hot fact, with the trailing-column limitation documented
- [ ] 4-wave migration plan for the 260 non-Delta tables with dual-write verification
- [ ] Retention policy tying vacuum to the oldest live snapshot
- [ ] Runbook for the six failure modes
