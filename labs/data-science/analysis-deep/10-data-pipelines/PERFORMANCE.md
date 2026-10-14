# Performance - Data Pipelines

## Complexities

- Ingest + checks: O(rows * cols) single pass.
- Keyed sink merge: O(1) amortized per record.
- Compat: O(fields). Windows: O(n) naive slice form, O(1) amortized
  running form. DAG overhead: O(nodes + edges) - negligible.

## Scaling guidance

- Throughput comes from partitioning by key (parallel merges per
  partition), not from tuning the merge itself - state the partition
  key before profiling anything.
- Checks stream: never hold two copies (raw + transformed) when one
  pass with staged writes suffices; memory is O(window), not O(history).
- Backfills are the heavy job: same code, bounded parallelism over key
  ranges, throttled against the serving store - schedule, don't rush.

## No invented benchmarks

No rows/sec or latency figures appear: they depend on hardware, stores,
and record width. Size from your own load test with production-shaped
records, then add headroom for replays running concurrently.

## Real cost driver

Reprocessing and late-data handling dominate budgets: design replay and
backfill paths before launch, because the first schema break or logic
bug will demand them under time pressure.

## Cost table

| Operation | Time | Memory |
|---|---|---|
| ingest + checks | O(rows * cols) | O(cols) |
| keyed merge | O(1) amortized/record | O(keys) |
| compat check | O(fields) | O(1) |
| naive windows | O(n) slices | O(window) |
| DAG overhead | O(nodes + edges) | O(edges) |

## Measurement note

Load-test with production-shaped records (real widths, real skew) and
report rows/sec with row counts - then add headroom for a concurrent
replay, because breaks arrive during peak, never during calm.
