# Feature Stores — Internals

## Offline layout
Partition by (time bucket, entity hash). Rows immutable, compressed
columnar blocks. As-of joins become per-entity range scans with a
ts <= t predicate plus a take-latest reduction. Late events append;
compaction never rewrites values, only reorganizes files.

## Online layout
Hash-sharded KV: key entity id, value serialized vector plus per-field
ts. Reads apply TTL per field at lookup. Writes are upserts guarded by
ts comparison, making retries safe.

## Materializer mechanics
Tail the offline commit log in order. For each (entity, ts, value),
compare with the stored ts; write only if newer. Batch writes per
shard; checkpoint offsets so restarts resume without duplicates
(output idempotent regardless).

## Registry storage
Small relational tables: definitions, versions, code hashes, owners,
TTLs, backfill receipts. Every training build writes a lineage record
linking dataset id to version set. Small but load-bearing: loss of this
metadata is loss of reproducibility.

## Failure handling
- Materializer crash: restart from the last committed offset; upserts
  keyed by (entity, ts) make replayed rows no-ops when older.
- Late event past the watermark: append plus bounded recompute of
  affected training partitions; never an in-place rewrite.
- Online shard loss: rebuild from the offline log tail (full replay
  for the shard's entity range), not from a stale snapshot.
- Registry outage: serving continues on cached version pins; new
  training builds wait rather than proceeding unpinned.
