# Feature Stores — Performance

## What dominates cost
As-of joins scan history per entity; online reads are single-key
lookups. The join is the expensive operation, the lookup the
latency-sensitive one. Size them separately.

## Join efficiency
- Partition pruning by time bucket cuts scanned rows per label.
- Per-entity sorting by ts makes take-latest a linear pass.
- Pre-aggregated windows (7d sums) trade ingest compute for join speed.

## Serving efficiency
- Keep vectors narrow: wide vectors multiply per-request bytes.
- Cache hot entities, but TTL still applies on top of cache.
- Serialize compactly; schema registries catch width creep.

## Backfill efficiency
Backfills are bounded batch jobs: run in ts order, validate per
partition (counts, null rates), mark receipts. Throttle to avoid
starving the live materializer of throughput.

## Capacity planning rule
Provision the offline scan path for backfill plus training-build
concurrency, and the online path for peak QPS times vector bytes with
headroom for retry storms. When the two contend (shared cluster),
throttle backfills first: stale-version training can wait, live serving
cannot. Revisit TTLs before buying hardware — shorter retention shrinks
both scan cost and storage, and the demo's 0.5 coverage at TTL 30 shows
how directly TTL sets the served fraction.

## Numbers from this lab
Demo scale only: 4-row histories, coverage 0.5 at TTL 30. No
throughput claims — those depend on hardware this lab does not
benchmark. The structural point stands: joins cost scans, serving
costs bytes times QPS.
