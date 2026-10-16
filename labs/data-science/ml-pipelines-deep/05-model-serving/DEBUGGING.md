# Model Serving - Debugging

## p99 spikes, p50 flat
- Cause: tail from cold instances, GC pauses, or a slow downstream call.
- Check: version-tagged latency histograms; correlate with deploys and traffic peaks.
- Fix: warmup enforcement, heap tuning, timeout plus fallback on the slow call.

## Throughput below expected
- Cause: batch size too small or batch-wait too short under load.
- Check: batch-size distribution and items/sec per worker.
- Fix: raise batch cap within the latency budget; preallocate buffers.

## Canary looks worse, then recovers
- Cause: small-sample noise judged too early.
- Check: error bars at current traffic share; require predeclared duration.
- Fix: widen share or extend duration before deciding.

## Schema errors after deploy
- Cause: client sends fields the new schema rejects, or units changed.
- Check: rejection logs by client version and field.
- Fix: backward-compatible parsing with explicit version handling.

## Rollback fails
- Cause: rollback path never tested; old artifact evicted.
- Check: drill logs and artifact retention.
- Fix: keep prior version warm until the new one is declared stable.

## Latency budget overrun per leg
- Cause: preprocessing grew (new features) while the budget stayed fixed.
- Check: per-leg timing split: preprocess vs model vs postprocess vs network.
- Fix: re-split the budget explicitly or move costly features to async paths.

## Streaming lag grows
- Cause: per-key state too large or late events reprocessed repeatedly.
- Check: state size, watermark lag, and reprocess counts per window.
- Fix: bound windows, checkpoint state, and pin the late-event policy.

## Version skew in responses
- Cause: mixed versions behind the balancer during a stepped shift.
- Check: version field distribution in responses over the shift window.
- Fix: pin balancer pools per version until the shift completes.

## Cold batch workers after scale-out
- Cause: new workers take partitions before warmup finishes.
- Check: per-worker latency by worker start time.
- Fix: gate partition assignment on readiness, as with online traffic.
