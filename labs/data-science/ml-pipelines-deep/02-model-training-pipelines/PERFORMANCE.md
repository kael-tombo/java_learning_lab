# Model Training Pipelines — Performance

## Where time goes
Ingest and transform scale with data volume; training scales with data
times passes times model size; evaluation is a single bounded pass over
held-out data. Validation is cheap relative to training, which is why
gating early saves the most expensive stages.

## Throughput tactics
- Partition ingest and transform by time/entity buckets; stages are
  embarrassingly parallel across partitions.
- Cache feature matrices by (dataset version, transform version) so
  repeated experiments skip recomputation.
- Parallelize hyperparameter trials as separate DAG branches sharing
  one validated feature matrix.

## Latency tactics
- Keep the orchestrator's scheduling overhead small relative to stage
  runtimes; batch tiny stages together.
- Stream validation checks in one pass (counts, nulls, min/max) rather
  than one scan per check — the demo computes nulls and range in a
  single loop for this reason.

## Cost control
- Stop at the first failed gate; never train on data that failed
  validation.
- Cap trial budgets (max runs, max epochs) in the tracker config.
- Retire stale feature caches and unpromoted artifacts on retention
  schedules.

## No fabricated numbers
This lab makes no throughput claims; sizing depends on hardware and
data not present here. The structural guidance — gate early, cache
features, parallelize trials — holds regardless of scale.
