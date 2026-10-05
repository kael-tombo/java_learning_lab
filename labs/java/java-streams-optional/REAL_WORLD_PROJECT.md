# Real-World Project — ETL Pipeline Service

## Problem
Nightly ETL: 10GB CSV → validate → enrich → Parquet/DB, observable + restartable.

## Architecture
```
Files.lines (lazy) → parse (Optional<Row>) → validate → enrich (lookup map)
  → batch(10k) → writer (JDBC batch / Parquet) → DLQ + metrics
Parallel: chunk files, not rows (avoid common-pool exhaustion)
```

## Milestones
1. **M1 Parser**: record Row, `parse(): Optional<Row>`, DLQ for malformed.
2. **M2 Pipeline**: single-pass stream, teeing stats (ok/bad/revenue).
3. **M3 Batch sink**: 10k JDBC batches, idempotent upsert keys.
4. **M4 Scale**: file-level parallelism (fixed pool = cores), backpressure queue.
5. **M5 Ops**: checkpoint file, resume, Prometheus counters, alert DLQ spike.

## Key Code
```java
try (var lines = Files.lines(in)) {
  var res = lines.skip(1).map(Row::parse).flatMap(Optional::stream)
    .collect(teeing(filtering(Row::valid, toList()),
                    filtering(r -> !r.valid(), toList()), Batch::new));
  writer.writeBatches(res.ok(), 10_000);
}
```
Run: `java -Xmx2g -XX:+UseG1GC -Djava.util.concurrent.ForkJoinPool.common.parallelism=4 Etl`.

## Testing
- Golden 100k file: exact counts; fuzz bad rows 5% → DLQ matches.
- Idempotency: rerun same batch → no dupes.
- Bench: boxed vs primitive, seq vs file-parallel numbers recorded.

## Ops
- Docker temurin:21, 2Gi; cron/K8s Job; PVC for in/out; Grafana DLQ panel.
- Alert: DLQ% > 2%, p99 batch > 30s.

## Interview Angles
- Why file-parallel not row-parallel? Collector choice? Optional DLQ design?

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Oracle streams: https://docs.oracle.com/javase/8/docs/api/java/util/stream/package-summary.html
- Oracle Optional: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Optional.html
- OpenJDK gatherers: https://openjdk.org/jeps/462
