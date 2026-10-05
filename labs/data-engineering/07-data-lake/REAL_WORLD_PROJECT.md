# Data Lake — REAL WORLD PROJECT

## Context

A media conglomerate consolidated 14 acquisition's data onto one S3 "data lake"
that has become a 4.3PB cost centre. Engineering teams are billed by the TB and
complain about slowness; finance wants a 40% storage reduction; legal needs
provable deletion for GDPR. All three are storage-architecture problems, not
tooling problems. You own the lake's physical design and lifecycle.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Objects | 1.9B files, 4.3PB |
| Ingest | 40TB/day, 92% in Parquet, 8% in CSV/JSON drop zones |
| Query engines | 6 (Spark, Trino, Athena, Snowflake, BigQuery, Presto-on-EMR) |
| Small files | ~55% of files < 1MB; drives listing cost and metadata latency |
| Retention | raw 400d, curated 2y, gold 7y (legal) |
| Cost | $780k/month, 61% storage, 24% egress, 15% requests |
| Compliance | GDPR erasure must be provable across all zones and all engines |

## Architecture (target)

```
landing/         drop zones, CSV/JSON, 7d TTL, no SLA          ~0.3PB
bronze/          immutable raw, Parquet+zstd, dt partitions    1.4PB -> 180d -> cold
silver/          conformed + deduped, business-date parts       0.9PB -> 2y
gold/            marts + aggregates                            0.1PB -> 7y
archive/glacier/ cold Parquet, read-through only                1.6PB

manifests/       one per partition: files, rows, checksums, schema version
catalog/         table definitions, ownership, retention class
```

## Key Implementation — physical design rules with the numbers behind them

| Rule | Value | Reason (measured) |
|---|---|---|
| File size | 256MB - 1GB | below 128MB: task overhead dominates; above 1GB: no parallelism benefit |
| Partition granularity | daily, then bucket(1000) on `entity_id` | daily-only gave 1.3M-file months |
| Row group | 128MB | matched to read page size; measured 22% fewer seeks |
| Codec | zstd level 3 + dictionary | 610GB -> 240GB with no read regression |
| Drop zone TTL | 7 days | nothing legitimate lives longer untyped |
| Compaction | weekly per zone, incremental | small-file share fell 55% -> 6% |

```java
public enum RetentionClass {
    DROP_ZONE(7, 7, 30),          // days: hot, cold, expire
    BRONZE(30, 180, 400),
    SILVER(90, 365, 2_555),       // ~7y
    GOLD(90, 365, 2_555),         // ~7y, legal floor
    AUDIT_IMMUTABLE(3_650, 3_650, 3_650);  // never expires: write-once evidence

    final int daysToCold; final int daysToGlacier; final int daysToExpire;
    RetentionClass(int cold, int glacier, int expire) {
        this.daysToCold = cold; this.daysToGlacier = glacier; this.daysToExpire = expire;
    }
}
```

## Compaction Without a Maintenance Window

Naive compaction rewrites whole partitions, which re-reads terabytes. The
incremental approach rewrites only files below the target size, appending the
compacted output as a new version, and deletes the inputs only after the new
version is committed to the manifest.

```java
public record CompactionPlan(List<Path> inputs, Path output, long inputBytes) {
    boolean profitable() {
        // A rewrite is worth it only if IO is amortized. Below ~2x target size in
        // aggregate, the write cost dominates the listing savings.
        return inputBytes >= 2L * TARGET_FILE_BYTES;
    }
}

public CompactionPlan planCompaction(List<Path> files) {
    long total = files.stream().mapToLong(this::size).sum();
    return files.size() < MIN_FILES || total < 2L * TARGET_FILE_BYTES
            ? null
            : new CompactionPlan(sortedByKeyTimestampAsc(files),
                                 newOutputFile(), total);
}
```

The payoff shows up as a metadata metric, not a storage metric: partition
listing time dropped from 9.4s to 0.3s, and the engines' planning time with it.

## Provable Deletion (the GDPR Problem)

A deletion request must be provable, which means it must be *recorded*.

```java
public final class ErasureService {
    /** Ordered, idempotent, and it leaves an immutable evidence trail. */
    public ErasureReceipt erase(String subjectId, LegalRequest request) {
        ErasureReceipt receipt = new ErasureReceipt(UUID.randomUUID().toString(),
                subjectId, request.reference(), Instant.now());

        for (String zone : List.of("landing", "bronze", "silver", "gold")) {
            for (Path p : lake.findPartitionsContainingSubject(zone, subjectId)) {
                lake.rewriteExcluding(p, subjectId, receipt.id());   // physical removal
            }
        }
        lake.trackers().forEach(t -> t.deleteVectors().deleteWhere(subjectId, receipt.id()));
        lake.purgeBackups(receipt.id());          // snapshots, caches, ES, vector stores
        lake.appendToImmutableAuditLog(receipt);   // who, when, what scope, what proof
        return receipt;
    }
}
```

Two hard rules learned the expensive way: (1) never rely on a logical delete flag
for erasure — a `deleted_at` column still contains the personal data; (2) every
copy counts, including the "temporary" debug copy someone made in March.

## Failure Modes and the Runbook

1. **A single query without a partition filter scans 4TB.** Symptom: cost spike,
   engine queue time. Fix: default partition requirement enforced by a linter,
   per-team byte budgets, and a daily report of the top-10 unscoped queries.
2. **Small-file storm** after a burst of micro-batches. Symptom: listing latency,
   engine planning timeouts. Fix: compaction triggered by file count, not a
   weekly calendar.
3. **Compaction and a reader race.** Symptom: "file not found" during a query.
   Fix: commit output to the manifest first, delete inputs after; readers resolve
   through the manifest, never by listing.
4. **Lifecycle policy expires data still needed by an audit.** Fix: retention
   class is a property of the table, and `AUDIT_IMMUTABLE` has no expiry path.
5. **Egress bill spike** from cross-region reads. Fix: pin hot gold data
   co-located with the engines that read it; measure egress per team.
6. **A 400GB CSV drop zone blocked by a bad export.** Fix: drop zone is 7d TTL
   and quota-limited per producer, so junk expires instead of accumulating.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Parquet is a columnar file format that stores data in row groups and pages,
  enabling column projection, row-group pruning, and dictionary/compression
  encodings — the basis for scanning less data in a lake.
  - Reference: https://parquet.apache.org/docs/
  - Reference: https://parquet.apache.org/docs/file-format/
- Apache Iceberg is an open table format for huge analytic datasets: it adds
  snapshot isolation, schema evolution, hidden partitioning, and time travel on
  top of object storage.
  - Reference: https://iceberg.apache.org/
  - Reference: https://iceberg.apache.org/docs/latest/
- Delta Lake provides ACID transactions and time travel over a data lake, which
  is how a lakehouse gets multi-writer correctness without a warehouse.
  - Reference: https://docs.delta.io/latest/index.html
  - Reference: https://github.com/delta-io/delta

## Deliverables
- [ ] Target-state zone design with partition/file/codec rules and measured reasons
- [ ] Compaction engine with a profitability heuristic and manifest-based swap
- [ ] Lifecycle policy table including a never-expiring audit class
- [ ] GDPR erasure service with an evidence receipt and a leak test
- [ ] Cost model by zone with a 40% reduction plan
- [ ] Runbook for the six failure modes
