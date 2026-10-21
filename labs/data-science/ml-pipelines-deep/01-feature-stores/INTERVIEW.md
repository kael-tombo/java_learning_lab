# Feature Stores — Interview

## Q: Why not just query the warehouse at serving time?
A: Warehouses optimize scans, not single-row millisecond lookups, and
ad-hoc queries are unversioned. The store splits the paths: offline log
for correct training joins, online KV for fast serving, both fed by one
versioned transform.

## Q: Explain point-in-time correctness.
A: For label (e, t), use the feature row with max ts <= t. Anything
newer is future information. I verified a demo: label u1@25 joins value
2.0 (ts=20), not 3.0 (ts=30); the leak biases the row by 1.0.

## Q: How do you detect training/serving skew?
A: Log served vectors, recompute expected vectors offline with the
pinned version, and compare per-feature max absolute difference. Demo:
identical code gives 0.0; a stale shift gives 1.0, which pages the owner.

## Q: Offline vs online store trade-offs?
A: Offline favors scan throughput and completeness; online favors
lookup latency and availability. Partition offline by time/entity hash,
shard online by entity id, and keep the materializer idempotent.

## Q: How do you roll out a feature change safely?
A: Register v2, backfill history in ts order, validate counts and null
rates per partition, mark v2 live, switch new training to v2 while old
models stay pinned to v1. Rollback repoints the version pointer.

## Q: What does TTL buy you?
A: A bound on staleness: values older than TTL read as missing and flow
through declared imputation. Demo: TTL 30 at t=100 keeps 2 of 4 rows,
coverage 0.5, which is also the freshness SLO signal.

## Q: New entity with no history — what should serving return?
A: The declared cold-start default, logged as imputed. Never a silent
zero that looks like measured data, and never another entity's vector.

## Q: How do you backfill without breaking the live model?
A: Compute v2 history offline, validate per-partition counts and null
rates against v1, mark v2 live only on passing receipts, and keep the
deployed model pinned to v1 until it is retrained and promoted on v2.
The live path never reads unvalidated rows.
