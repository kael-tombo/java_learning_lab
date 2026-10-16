# Model Serving - Performance

## Budgets
- Interactive paths budget per-request p99; background paths budget items per hour.
- Split the budget across preprocessing, model compute, postprocessing, and network.
- Measure the tail under peak load, not average load.

## Batching
- Larger batches raise throughput and latency together; cap batch by the latency budget.
- Bound the batch-wait time so low-traffic periods do not stall.
- Keep batch buffers preallocated to avoid per-request allocation spikes.

## Sizing
- Memory follows weight size plus batch and scratch buffers; CPU follows preprocessing cost.
- Replicate stateless servers with peak load plus headroom; queueing explodes near saturation.
- Warmup before traffic; cold instances show the worst p99.

## What to watch
- p50, p99, timeout rate, and queue depth per model version.
- Version-tagged metrics so canary regressions are visible separately.

## Measurement method
- Load from warmed instances at peak-like concurrency; cold numbers mislead sizing.
- Record per-leg timings on every request, sampled when full capture costs too much.
- Compare versions on identical traffic shape before declaring a winner.

## Batch tuning loop
- Start from the latency cap, derive the max batch, then measure realized throughput.
- If throughput trails the formula, suspect buffer allocation or shard imbalance.
- Re-tune when preprocessing changes: new features move overhead and per-item cost.

## Streaming steadiness
- Bound per-key state so restarts replay minutes, not hours, of windows.
- Prefer dropping or updating late events over unbounded reprocessing.
- Track watermark lag as the streaming analogue of queue depth.

## Regression guards
- Gate promotion on p50/p99 per version staying inside budget at canary share.
- Alert when timeout rate moves before users report; timeouts precede complaints.
- Keep one dashboard per version during shifts so regressions cannot hide in blends.

## Cold-start control
- Warmup sample count scales with model size: bigger weights need more fills.
- Stagger replica restarts so the fleet never cools all at once.
- Verify p99 in the first minutes after deploy, not only at steady state.
