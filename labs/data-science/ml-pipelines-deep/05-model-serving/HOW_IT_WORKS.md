# Model Serving - How It Works

## Online request path
1. Request arrives with a versioned schema; validation rejects malformed fields.
2. Preprocessing builds the feature vector (same code path as training features).
3. Warmed model scores the vector; postprocessing maps raw output to labels or probabilities.
4. Response returns prediction plus model version; the pair is logged for replay.

## Batch path
1. Scheduler selects the input partition and model version.
2. Worker shards scan rows, score them, and write predictions with keys.
3. Validation counts rows in versus rows out and checks score distribution.

## Streaming path
1. Events arrive continuously; per-key state holds windows and counters.
2. Each event is scored against current state; state updates after scoring.
3. Late events follow a fixed policy (drop, update, or reprocess window).

## Rollout flow
1. New version deploys beside production and warms up.
2. Shadow or canary phase compares error and latency distributions.
3. Traffic shifts in steps; rollback returns routing to the prior version.

## Caching path
1. Gateway hashes the request plus model and schema versions into a cache key.
2. Hits return the stored prediction without scoring; misses flow through the online path.
3. Promotion invalidates entries whose version no longer serves traffic.

## Failure path
1. Preprocessing rejection returns a validation error with field and reason.
2. Model timeout triggers the fallback named in the serving contract.
3. Logger outage buffers events in memory and drains when the sink recovers.

## Capacity check
1. Measure per-replica throughput on warmed instances at peak-like load.
2. Divide peak requests per second by that number and add headroom.
3. Watch queue depth in production; rising queues precede timeout storms.

## Contract migration
1. New schema version deploys alongside the old; both validate.
2. Rejection logs by client version show who still sends the old shape.
3. Old version retires only after client metrics confirm migration.
