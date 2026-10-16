# MLOps Orchestration - Performance

## Throughput
- Parallelize independent DAG branches; shard data-heavy tasks by partition.
- Cache immutable inputs between runs; rebuild only what changed.
- Separate queues for scheduled, event, and backfill work prevent starvation.

## Latency
- Gate evaluation should be seconds on precomputed metrics, not a retraining loop.
- Backoff caps bound retry storms during dependency outages.
- Fail fast on validation errors instead of consuming training budget.

## Resource use
- Request CPU and memory per task from measured peaks, not guesses.
- Clean intermediate artifacts on a retention policy; lineage pointers keep the record.
- Limit backfill parallelism so replays do not starve live runs.

## What to watch
- Run duration, queue wait, retry counts, and gate outcomes per pipeline.

## Scheduler lightness
- Keep scheduling decisions in memory; persist only run state changes.
- Heavy computation inside the scheduler serializes every lane at once.
- Shard task dispatch when branch counts grow into the thousands.

## Cache discipline
- Immutable inputs cache across runs keyed by data version.
- Invalidate on version change only; content hashes verify hits.
- Evict intermediates by retention policy, never while a run references them.

## Gate speed
- Precompute evaluation metrics during training so gates read, not compute.
- Slice breakdowns materialize beside overall numbers in the same pass.
- Seconds-scale gates keep promotion snappy; retraining loops stay out.

## Backfill pacing
- Replay windows sequentially to preserve ordering guarantees downstream.
- Cap parallelism explicitly; unbounded replays look like denial of service.
- Monitor live-lane waits during replays as the fairness signal.

## Measurement
- Track run duration, queue wait, retry counts, and gate outcomes per pipeline.
- Alert on duration drift: slow pipelines delay freshness silently.
- Review the slowest stage monthly; it owns the next optimization.
