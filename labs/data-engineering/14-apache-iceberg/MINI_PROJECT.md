# Apache Iceberg — MINI PROJECT

## Project: Iceberg Metadata Engine + Hidden Partitioning

Implement the metadata layer of an Iceberg-style table — snapshots, manifest
lists, manifest files, partition specs with transforms — plus a mini query
engine that prunes files using hidden partitioning.

### Scope
- Metadata: `TableMetadata` -> snapshots -> manifest lists -> manifests -> data files.
- Snapshot: append / fast-append / overwrite / delete with a manifest diff.
- Partition transforms: identity, truncate, bucket, year, month, day, hour.
- Hidden partitioning: a query on `ts` prunes without the user writing `WHERE day=...`.
- Branching: create a branch, write to it, detect conflicts on merge.
- Multi-engine read: same table read through 3 adapters with equal output.

### Architecture

```
table/metadata/v1.metadata.json        table properties, current snapshot id
table/metadata/snap-123.avro           manifest list (which manifests, added/removed)
table/metadata/snap-123-<uuid>-m0.avro manifest (which files, with stats + partition summaries)
table/data/p=2026-01-01/part-0.parquet actual data

query "WHERE ts >= 2026-01-10"
   -> transform(ts, day) -> 2026-01-10
   -> manifest summary prune: only manifests with that partition value
   -> file-level stats prune
   -> read 3 files instead of 1.2M
```

### Implementation — the metadata chain

```java
public record TableMetadata(int formatVersion, long currentSnapshotId,
                            List<Long> snapshotIds, List<Snapshot> snapshots,
                            Schema schema, PartitionSpec spec, List<String> sortOrders,
                            Map<String,String> properties) {}

public record Snapshot(long id, long parentId, long sequenceNumber, long timestampMs,
                       String operation, String summary,
                       List<Long> manifestListId, List<Long> manifestIds) {
    public enum Operation { APPEND, FAST_APPEND, OVERWRITE, DELETE, REPLACE }
}

public record Manifest(long id, long snapshotId, int content,       // 0=data, 1=deletes
                       long addedSnapshotId, long sequenceNumber,
                       List<PartitionSummary> partitions, List<DataFile> files) {}

public record DataFile(String path, long fileSize, int recordCount,
                       Map<Integer,Long> columnSizes,
                       Map<String,Long> lowerBounds, Map<String,Long> upperBounds,
                       Map<String,Integer> partitionValues) {}
```

### Partition transforms — the thing hidden partitioning depends on

```java
public sealed interface Transform permits Identity, Truncate, Bucket, Year, Month, Day, Hour {
    /** Maps a value to the partition key it belongs to. */
    int apply(java.util.function.Function<Integer,Object> read, int rowOrdinal, Schema schema);

    String name();
}

public record Truncate(int width) implements Transform {
    public String name() { return "truncate[" + width + "]"; }
    public int apply(...) {
        long v = ((Number) read.apply(...)).longValue();
        return (int) (v - Math.floorMod(v, width));
    }
}

public record Bucket(int buckets) implements Transform {
    public String name() { return "bucket[" + buckets + "]"; }
    /** Iceberg's bucket transform is murmur3-based, not hashCode. Reproducing
     *  a different function silently changes the partition layout for every
     *  existing row, so this must match the spec, not be "close enough". */
    public int apply(...) {
        return (int) (murmur3(serializedValue) & Integer.MAX_VALUE) % buckets;
    }
}

public record Day(String sourceColumn) implements Transform {
    public String name() { return "day(" + sourceColumn + ")"; }
    public int apply(...) {
        long epochDay = Math.floorDiv(epochMillis(read), 86_400_000L);
        return (int) (epochDay - EPOCH_DAY_1970);          // days since 1970-01-01
    }
}
```

### Pruning: the entire point

```java
public final class ManifestReader {

    /** Level 1: skip whole manifests using partition summaries. */
    public List<Manifest> pruneManifests(List<Manifest> manifests, Map<Integer, Range> filter) {
        return manifests.stream()
                .filter(m -> filter.entrySet().stream().allMatch(e -> {
                    Range r = e.getValue();
                    return m.partitions().stream()
                            .filter(p -> p.fieldId() == e.getKey())
                            .anyMatch(p -> p.contains(r));        // does any partition overlap?
                }))
                .toList();
    }

    /** Level 2: skip whole data files using column min/max stats. */
    public List<DataFile> pruneFiles(List<Manifest> manifests, Map<Integer,Range> filter) {
        return manifests.stream().flatMap(m -> m.files().stream())
                .filter(f -> filter.entrySet().stream().allMatch(e -> {
                    Long lo = f.lowerBounds().get(e.getKey());
                    Long hi = f.upperBounds().get(e.getKey());
                    if (lo == null || hi == null) return true;   // no stats: must read
                    return !(hi < e.getValue().min() || lo > e.getValue().max());
                }))
                .toList();
    }
}
```

### Hidden partitioning in action

```java
/**
 * The user writes:  WHERE ts >= '2026-01-10' AND ts < '2026-01-11'
 * The spec is:       PARTITIONED BY (days(ts))
 * The planner derives day(ts) IN (2026-01-10) and prunes. The user never
 * mentions a partition. This is why a re-partitioned table does not break
 * every query in the codebase.
 */
public final class HiddenPartitionPlanner {
    public PredicatePlan plan(PartitionSpec spec, Map<String,Range> predicates) {
        Map<Integer, Set<Object>> required = new HashMap<>();
        for (var e : predicates.entrySet()) {
            int fid = schema.fieldId(e.getKey());
            spec.fields().stream()
                    .filter(f -> f.sourceId() == fid)
                    .findFirst()
                    .ifPresent(f -> required.computeIfAbsent(f.fieldId(), k -> new HashSet<>())
                            .addAll(f.transform().applyRange(e.getValue())));
        }
        return new PredicatePlan(required);
    }
}
```

### Branching and the WAP pattern

```java
public final class BranchManager {
    public long createBranch(String name, long fromSnapshotId) {
        return metadata.add(new BranchRef(name, fromSnapshotId, List.of(), Map.of(
                "write.wap.enabled", "true")));
    }

    /**
     * Write-Audit-Publish: writers commit to a branch; a validation job
     * inspects the branch; only a good branch is fast-forwarded into main.
     * Writers never block readers, and a bad write never reaches readers.
     */
    public void promote(String branch, long snapshotId) {
        long mainHead = metadata.currentSnapshotId();
        if (isAncestor(mainHead, snapshotId)) {
            metadata.setCurrentSnapshotId(snapshotId);          // fast-forward: cheap
        } else {
            mergeWithConflictDetection(branch, snapshotId);       // expensive, but rare
        }
    }

    /** A conflict is a data file that both sides changed. Detect, do not silently last-write-wins. */
    public List<Conflict> detect(long baseSnapshot, long branchHead) {
        Set<String> baseFiles = filesAt(baseSnapshot);
        Set<String> mainAdded = filesAddedSince(baseSnapshot, currentSnapshotId());
        Set<String> branchAdded = filesAddedSince(baseSnapshot, branchHead);
        Set<String> overlapping = new HashSet<>(mainAdded);
        overlapping.retainAll(branchAdded);
        return overlapping.stream().map(Conflict::new).toList();   // same file = conflict
    }
}
```

### Schema evolution

```java
public Schema evolve(Schema current, Schema proposed) {
    List<Field> added = proposed.fields().stream()
            .filter(f -> current.field(f.name()).isEmpty())
            .peek(f -> require(f.required(), () ->
                    new SchemaViolation("cannot add a required column "
                            + f.name() + " without a default")))
            .toList();
    List<Field> removed = current.fields().stream()
            .filter(f -> proposed.field(f.name()).isEmpty())
            .peek(f -> require(f.required(), () ->
                    new SchemaViolation("cannot drop required column " + f.name())))
            .toList();
    List<Field> promoted = current.fields().stream()
            .filter(f -> f.required() && proposed.field(f.name())
                    .map(p -> !p.required()).orElse(false))
            .peek(f -> require(false, () ->
                    new SchemaViolation("cannot make required column optional: " + f.name())))
            .toList();

    // Reorder: always legal, and positional readers depend on it.
    List<Field> reordered = proposed.fields().stream()
            .filter(f -> current.field(f.name()).isPresent())
            .toList();
    return new Schema(Stream.concat(added.stream(), reordered.stream()).toList());
}
```

### Test It

```java
@Test void hiddenPartitionPrunesFiles() {
    TableMetadata md = tableWithDaysPartition();        // 1,200 files, 400 days
    PredicatePlan plan = planner.plan(spec(), Map.of("ts", range(2026_01_10, 2026_01_11)));
    long filesToRead = reader.pruneFiles(
            reader.pruneManifests(md.manifests(), plan.required()), plan.required()).size();
    assertTrue(filesToRead <= 6, "expected ~1 day of files, planned " + filesToRead);
}

@Test void wapPromotionDetectsConflict() {
    long branch = branches.createBranch("etl-2026-01-10", current());
    writeOn("main", fileA());
    writeOn("etl-2026-01-10", fileA());                  // same partition, same file name space
    assertFalse(branches.detect(base, branchHead).isEmpty());
}
```

### Stretch
- Add delete files (equality deletes + positional deletes) and an equality-delete read path.
- Add a `RewriteDataFiles` operation (compaction) with a predicate.
- Read the same table through a Spark adapter, a Trino-style adapter, and the
  local engine, and assert identical row counts and checksums.

## Deliverables
- [ ] Metadata chain: metadata -> snapshots -> manifest lists -> manifests -> files
- [ ] All 7 partition transforms, with `bucket` matching the spec hash
- [ ] Two-level pruning (manifest summaries + file stats) with a measurement
- [ ] Hidden partition planner, with a test showing a 200x file reduction
- [ ] Branch create/promote with conflict detection and a WAP demo
- [ ] Schema evolution covering add/drop/rename/reorder/required-ness
- [ ] Three-reader equivalence test
- [ ] README mapping each metadata file to its purpose
