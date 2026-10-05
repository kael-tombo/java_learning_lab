# Apache Iceberg — REAL WORLD PROJECT

## Context

A logistics group is standardising on an open table format so that five engines
(Spark, Flink, Trino, Athena, Snowflake external) can read one copy of the
data. Iceberg is the candidate; Delta is already in 40 tables. The deliverable
is a decision with evidence, a coexistence strategy, and a production-hardened
Iceberg footprint for the 3.4PB of new data.

## Scale & Constraints

| Dimension | Value |
|---|---|
| New data | 3.4PB/yr across 900 tables, 6 business domains |
| Engines | Spark 3.5, Flink 1.18, Trino 428, Athena, Snowflake (external catalog) |
| Writers | 60 batch jobs, 12 Flink streaming jobs, 4 near-real-time writers |
| Snapshots | 2.6M across all tables; largest table 340k |
| Deletes | GDPR erasure (subject-level), plus CDC-driven deletes on 30 tables |
| Compliance | 7-year retention, SOX point-in-time reporting, EU residency |
| Constraint | no engine lock-in; all reads must stay portable |

## Architecture (target)

```
   writers
     |-- Spark batch MERGE / OVERWRITE          partitioned by date + bucket
     |-- Flink streaming APPEND (12 jobs)      never MERGE on the hot path
     |-- CDC upsert jobs (30 tables)           equality deletes + MERGE
     v
   ICEBERG CATALOG (REST / Glue / Hive Metastore, HA)
     |-- version-hint.txt  +  atomic metadata.json swap
     |-- snapshot retention: main 30d, tags 7y (for SOX)
     v
   metadata/  v*.metadata.json, snap-*.avro, m-*.avro
   data/      p=.../f-*.parquet
     |
   5 engines read the same table, same snapshots
```

## The Decision: Iceberg Alongside Delta, Not Instead of It

| Criterion | Iceberg | Delta | Weight | Verdict |
|---|---|---|---|---|
| Multi-engine read | 5 engines supported | Spark-centric; others via integrations | High | Iceberg |
| CDC-style row deletes | First-class equality/position deletes | MERGE-based rewrite | High | Iceberg |
| Time travel | Snapshots, plus long-lived refs/tags | Version history + `TIMESTAMP AS OF` | Medium | Tie |
| Streaming write | Strong, well-documented Flink connector | Strong Spark Structured Streaming | Medium | Tie |
| Ops maturity (our team) | 6 months of Spark experience | 2 years | Medium | Delta |
| Open-format multi-engine writes | Multiple engines can write safely | Mostly one writer engine | High | Iceberg |
| Schema evolution | 4 well-defined evolutions | More modes, more flexibility | Medium | Iceberg |
| Metadata format | Avro manifests, queryable metadata tables | JSON log | Low | Iceberg |

**Outcome:** Iceberg for all new tables; the 40 existing Delta tables stay
Delta and are exposed to Trino/Athena through the existing Delta read path.
Coexistence is explicit and has an end date (18 months) rather than being
ambiguous forever.

## Key Implementation — the practices that made Iceberg production-safe

**1. Partition specs chosen for the query, with `bucket` to bound file count.**
Day-only partitioning on a high-volume fact created 512 files per day per
region. Adding a bucket transform made it 16 per day, per region, with the
same pruning for the common filters.

```java
/**
 * Rule of thumb: partition by (low-to-medium cardinality time column) AND
 * (a bucket of a medium/high-cardinality filter column). Never partition by a
 * high-cardinality column alone: it produces one tiny file per distinct value.
 */
public record PartitionSpecDef(String timeColumn, int days, int bucketColumn, int buckets) {}

static final List<PartitionSpecDef> SPECS = List.of(
    new PartitionSpecDef("event_date", 1, "region_code", 16),     // daily x 16
    new PartitionSpecDef("order_date", 1, "customer_bucket", 64), // daily x 64
    new PartitionSpecDef("static",      0, "country", 8)          // reference data
);

public String specString(PartitionSpecDef d) {
    List<String> parts = new ArrayList<>();
    if (d.days() > 0) parts.add("days(truncate_ts(" + d.timeColumn() + ", 86400000))");
    if (d.bucketColumn() != null) parts.add("bucket[" + d.buckets() + "](" + d.bucketColumn() + ")");
    return String.join(", ", parts);
}
```

**2. Snapshot retention by design, with tags for audit.** Keeping 90 days of
snapshots on a 3.4PB estate is not affordable; keeping 7 years is not a
snapshot problem at all, because old snapshots point at old data files that
cold storage already holds.

```java
/**
 * Retention policy:
 *   main branch  -> 30 days of snapshots, then expire (metadata only)
 *   audit tag    -> never expired; a tag is a named, persistent ref
 *   data files   -> deleted only when NO live snapshot or tag references them
 *
 * The rule that matters: expiration checks references, not age. A file 400
 * days old is still required if a 400-day-old audit tag points at it.
 */
public final class SnapshotRetention {
    public Set<String> referencedFiles(TableMetadata md) {
        Set<String> out = new HashSet<>();
        for (Snapshot s : md.snapshots()) out.addAll(filesIn(s));
        for (BranchRef b : md.refs())  out.addAll(filesIn(b.snapshotId()));  // tags/branches
        return out;
    }

    public int expire(TableMetadata md, Instant cutoff) {
        Set<String> live = referencedFiles(md);
        int removed = 0;
        for (Snapshot s : md.snapshots()) {
            if (s.timestampMs() >= cutoff.toEpochMilli()) continue;
            if (live.containsAll(filesIn(s))) continue;      // still referenced: keep
            md.removeSnapshot(s.id());
            removed++;
        }
        return removed;
    }
}
```

**3. Row-level deletes for erasure.** This is Iceberg's decisive advantage
over a rewrite-based MERGE: erasing a subject writes a small delete file
instead of rewriting the partitions holding that subject.

```java
/**
 * Equality delete file: rows whose `subject_id` equals one of these values,
 * in the referenced data files, are logically deleted. Reads apply delete files
 * by position or by equality. Cost is proportional to the number of erased
 * subjects, not to the size of the data.
 */
public final class ErasureWritesDeleteFile {
    public DeleteFile writeEqualityDelete(String table, String subjectColumn,
                                          Set<String> subjectIds) {
        PartitionData partition = partitionFor(table, subjectIds);   // one partition, not all
        List<Pair<Integer, ByteBuffer>> equalityFields = List.of(
                fieldId(subjectColumn), utf8(sorted(subjectIds)));
        return DeleteFile.builder()
                .content(FileContent.DATA_DELETES)
                .fileSizeInBytes(estimateSize(subjectIds))
                .recordCount(subjectIds.size())
                .equalityFieldIds(List.of(fieldId(subjectColumn)))
                .lowerBounds(equalityFields)
                .upperBounds(equalityFields)
                .referencedDataFile(partition.dataFilesInScope())
                .build();
    }
}
```

Caveats stated honestly in the design: delete files do not physically remove
bytes, so compaction (`RewriteDataFiles`) is required to reclaim space, and
the erasure is logically complete at read time for every engine that implements
delete-file semantics — verified by an engine matrix test, not assumed.

**4. WAP for the two teams that write the same table.** A data-science team
exploring and a production team both writing `trips` needed a pattern that
lets both work without the explorers corrupting the main table.

```java
public enum Pattern { WRITE_AUDIT_PUBLISH, DIRECT_WITH_RETRY }

public final class WritePolicy {
    /**
     * A table with more than one writing team MUST use WAP. Direct concurrent
     * writes produce merge conflicts at commit time, and "retry until it works"
     * is not a policy - it is a race with extra log noise.
     */
    public Pattern patternFor(String table, Set<String> writingTeams) {
        return writingTeams.size() > 1 ? Pattern.WRITE_AUDIT_PUBLISH
                                       : Pattern.DIRECT_WITH_RETRY;
    }
}
```

## Failure Modes and the Runbook

1. **Commit conflict under concurrent writes.** Symptom:
   `ValidationException: cannot commit, conflicting files`. Fix: WAP for
   multi-writer tables; for single-writer tables, ensure exactly one writer per
   partition range (enforced in CI).
2. **Snapshot/metadata bloat.** Symptom: planning time climbs, metadata
   directory has millions of files. Fix: expire snapshots by the reference-aware
   policy above, then `rewrite_manifests`; snapshot retention is not a log
   retention problem.
3. **Expensive `DELETE FROM` on a fact table.** Symptom: a 6-hour rewrite. Fix:
   equality deletes for targeted erasure; a full-partition delete is a partition
   drop; anything else needs a predicate that maps to whole partitions.
4. **Partition spec change on a large table.** Symptom: a full rewrite, or an
   unreadable table if half-done. Fix: `ALTER TABLE ... REPLACE PARTITION FIELD`
   is metadata-only for future writes but leaves old data in the old spec —
   schedule a `RewriteDataFiles` to migrate, with a rollback point.
5. **Engine-version incompatibility.** Symptom: one engine reads, another fails
   on a new feature. Fix: a per-engine capability matrix test in CI, and
   `format-version` held back until every required engine supports it.
6. **Orphaned data files after a failed job.** Symptom: storage grows with no
   snapshot referencing the files. Fix: `orphan file removal` on a schedule, with
   a grace period longer than the longest possible job runtime.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Apache Iceberg is an open table format for huge analytic datasets, providing
  snapshot isolation, hidden partitioning, schema evolution, partition
  evolution, and time travel on top of object storage, usable from multiple
  engines.
  - Reference: https://iceberg.apache.org/
  - Reference: https://iceberg.apache.org/docs/latest/
  - Reference: https://iceberg.apache.org/docs/latest/evolution/
- Iceberg tracks row-level deletes as delete files with position and equality
  deletes, which is what allows targeted row removal without rewriting data
  files.
  - Reference: https://iceberg.apache.org/docs/latest/spec/#position-deletes
  - Reference: https://iceberg.apache.org/docs/latest/spec/#equality-deletes
- Parquet remains the data file format, so column pruning and statistics-based
  skipping are what make pruning effective at two levels.
  - Reference: https://parquet.apache.org/docs/file-format/

## Deliverables
- [ ] Iceberg-vs-Delta decision record with a weighted criteria table
- [ ] Coexistence plan for the 40 Delta tables, with an 18-month end date
- [ ] Partition spec standard (day + bucket) with a file-count and pruning measurement
- [ ] Reference-aware snapshot and tag retention policy
- [ ] Erasure via equality delete files, with an engine matrix test
- [ ] WAP policy: multi-writer tables must branch
- [ ] Engine capability matrix and a CI compatibility test
- [ ] Runbook for the six failure modes
