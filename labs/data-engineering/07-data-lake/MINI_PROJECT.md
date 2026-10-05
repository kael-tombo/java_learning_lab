# Data Lake — MINI PROJECT

## Project: Local Data Lake with Zones, Compaction, and Lifecycle

A filesystem-backed lake (MinIO or local FS) with a bronze/silver/gold zone
layout, Parquet-style columnar files, a compactor, and a lifecycle executor.

### Scope
- Bronze: immutable raw append, partitioned by `ingest_date=YYYY-MM-DD`.
- Silver: typed, deduped, partitioned by business date.
- Gold: aggregated by `date` + `country`.
- Compactor: rewrite small files into target-size (256MB) files.
- Lifecycle: `tier(raw, days)` -> move to cold storage; `expire(bronze, days)`.
- Report: bytes read per query with and without column projection.

### Architecture

```
s3://lake/bronze/orders/ingest_date=2026-01-01/  (immutable, 4KB-2MB files)
s3://lake/silver/orders/date=2026-01-01/         (typed, 128MB files)
s3://lake/gold/revenue_daily/date=2026-01-01/     (aggregate, 8MB files)
        |
   [compactor]  -> rewrites < target size, preserves partition
        |
   [lifecycle]  -> bronze(400d) -> cold, silver(2000d) -> cold, gold(4000d) keep
```

### Parquet write with projection-aware reads

```java
public final class ParquetLake {
    private final Path root;
    private final long targetFileBytes = 256L * 1024 * 1024;

    public Path writeBronze(String entity, LocalDate ingest, List<Row> rows) throws IOException {
        Path dir = root.resolve("bronze").resolve(entity)
                     .resolve("ingest_date=" + ingest);
        Files.createDirectories(dir);
        Path file = dir.resolve("part-" + UUID.randomUUID() + ".parquet");
        try (ParquetWriter<Row> w = ParquetWriter.builder(rowGroupType())
                .withCompressionCodec(CompressionCodecName.ZSTD)
                .withRowGroupSize(128 * 1024 * 1024)   // match read granularity
                .withPageSize(1 * 1024 * 1024)
                .withDictionaryEncoding(true)         // low-cardinality columns compress well
                .withWriterVersion(ParquetWriter.DEFAULT_WRITER_VERSION)
                .forWriter(new PathOutputFile(file))) {
            for (Row r : rows) w.write(r);
        }
        return file;
    }

    /** Read only two columns: the bytes read should drop by an order of magnitude. */
    public double readRevenue(Path file, List<String> projection) throws IOException {
        try (ParquetReader<Row> r = ParquetReader.builder(rowGroupType())
                .withConf(new ParquetReadConf(file.toUri().toString(), projection))
                .withFileSystem(new LocalOutputFile(file.toUri().toString()).getFileSystem())
                .forWriter(new PathInputFile(file))) {
            double sum = 0; Row row = r.read();
            while (row != null) { sum += row.getDoubleField("net_amount", 0); row = r.read(); }
            return sum;
        }
    }
}
```

### Compactor

```java
public final class Compactor {
    private final long targetBytes;
    private final int minFilesToCompact = 8;

    public record Result(String partition, int before, int after, long bytesBefore, long bytesAfter) {}

    public List<Result> compactZone(String zone) throws IOException {
        List<Result> results = new ArrayList<>();
        for (Path partition : listPartitions(zone)) {
            List<Path> files = listFiles(partition);
            long total = sizeOf(partition);
            if (files.size() < minFilesToCompact && total < targetBytes) continue;

            Path tmp = partition.resolveSibling(partition.getFileName() + ".compacting");
            Files.createDirectories(tmp);
            long written = 0; int out = 0;
            try (RowGroupWriter merged = new RowGroupWriter(tmp, targetBytes)) {
                for (Path f : sortedByTsAsc(files)) {     // deterministic order = reproducible output
                    written += merged.append(f);
                }
                out = merged.fileCount();
            }
            deleteQuietly(partition);                     // swap only after full success
            Files.move(tmp, partition, StandardCopyOption.ATOMIC_MOVE);
            results.add(new Result(partition.getFileName().toString(),
                    files.size(), out, total, sizeOf(partition)));
        }
        return results;
    }
}
```

### Lifecycle

```java
public enum Tier { HOT, WARM, COLD, GLACIER }

public record LifecyclePolicy(String zone, int daysToWarm, Integer daysToCold, Integer daysToExpire) {}

public final class Lifecycle {
    public static final List<LifecyclePolicy> DEFAULT = List.of(
        new LifecyclePolicy("bronze", 30,  400,  400),    // expire only after it reaches cold
        new LifecyclePolicy("silver", 90,  null, 2000),  // conformed data: keep long
        new LifecyclePolicy("gold",   90,  null, null)   // aggregates: small, keep forever
    );

    /** Expiry is gated on a legal-hold check and an audit row; never delete blind. */
    public boolean mayExpire(String zone, Instant lastModified, List<String> legalHolds) {
        LifecyclePolicy p = policyFor(zone);
        if (p.daysToExpire() == null) return false;
        if (!legalHolds.isEmpty()) return false;
        return lastModified.isBefore(Instant.now().minus(Duration.ofDays(p.daysToExpire())));
    }
}
```

### Bytes-read report

```java
public void report(Path file, List<String> all, List<String> projection) throws IOException {
    long t0 = System.nanoTime();
    lake.readRevenue(file, all);
    long wideMillis = (System.nanoTime() - t0) / 1_000_000;
    t0 = System.nanoTime();
    lake.readRevenue(file, projection);
    long narrowMillis = (System.nanoTime() - t0) / 1_000_000;
    System.out.printf("wide=%dms narrow=%dms ratio=%.1fx bytesProjected=%s%n",
            wideMillis, narrowMillis, (double) wideMillis / narrowMillis, projection);
}
```

### Stretch
- Add a manifest file per partition (file list + row counts + checksums) like a table format does.
- Measure listing cost: 40k-file partition vs 200-file partition for a metadata scan.
- Add a `zone map` style min/max per column to prune row groups yourself.

## Deliverables
- [ ] Three-zone layout with documented partition schemes
- [ ] Parquet writer with zstd + dictionary + row-group sizing
- [ ] Compactor with a before/after report per partition
- [ ] Lifecycle engine with legal-hold gating
- [ ] Bytes-read report showing column projection savings
- [ ] Manifest file per partition
