# Model Monitoring - Performance

## Cost control
- Aggregate at serving time into counters and sketches; avoid scanning raw events per dashboard load.
- Roll up hourly, then daily; keep raw events short-term only.
- Compute distribution checks on samples when full scans are too slow.

## Freshness
- Dashboard lag of minutes is fine; paging checks run on shorter cadences.
- Label joins run in batch; provisional metrics are clearly marked.
- Pinned reference windows avoid recomputation churn.

## Scale
- Shard aggregation by time and slice key; comparator work is per slice.
- Alert evaluation is cheap boolean logic over precomputed rollups.
- Cap cardinality: bound the number of tracked slices explicitly.

## What to watch
- Monitor the monitors: alert volume, precision, and time-to-detect per rule.

## Sampling strategy
- Full scans on every dashboard load waste the serving budget; sample first.
- Size samples from the narrowest slice: rare segments need absolute counts.
- Recompute exact numbers only for paging decisions and postmortems.

## Cardinality discipline
- Each tracked slice multiplies comparator work; cap the slice registry.
- Drop slices nobody reads; every kept slice needs an owner and a rule.
- Prefer hierarchical rollups (region, then device) over flat cross products.

## Join efficiency
- Label joins run in batch keyed once, not per dashboard query.
- Pre-join maturity flags so queries filter without recomputation.
- Backfill joins reuse the same keyed path; idempotent by window.

## Paging cadence
- Evaluate paging rules on short cadences over precomputed rollups.
- Dashboards refresh on the order of minutes; nobody triages a flicker.
- Alert evaluation stays boolean-cheap; heavy math belongs in rollups.

## Retention arithmetic
- Raw events cost the most per insight after days; roll them up and drop.
- Keep one raw sample per window for forensics after bulk deletion.
- Verify deletion jobs in monitors so drops read as expected, not as outages.
