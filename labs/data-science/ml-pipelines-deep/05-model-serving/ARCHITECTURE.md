# Model Serving - Architecture

## Components
- Gateway: validates schema, enforces auth and rate limits, routes to versions.
- Preprocessor: builds features with the same logic used in training.
- Model server: holds warmed weights in memory and answers score calls.
- Postprocessor: converts raw outputs to decisions and probabilities.
- Logger: records request, prediction, version, and latency per call.

## Data flow
- Online: gateway -> preprocessor -> model server -> postprocessor -> response, with async logging.
- Batch: partition reader -> sharded scorers -> prediction sink plus validation counts.
- Streaming: event bus -> stateful scorer -> action sink and state store.

## Versioning
- Model registry stores versioned artifacts; serving config maps traffic shares to versions.
- Shadow, canary, and blue-green are routing policies over these versions.
- Rollback changes routing only; no redeploy of the old artifact is needed.

## Scaling
- Stateless replicas scale horizontally with requests per second; batch workers scale with partition count.
- Keep preprocessing and model compute co-located to avoid extra hops.
- Isolate warmup and health checks from live traffic paths.

## Health and readiness
- Liveness says the process runs; readiness says warmed weights plus
  preprocessing are loaded and sample scores succeeded.
- Only readiness gates traffic; a live-but-cold instance stays out of rotation.
- Health responses include model version so load balancers detect version skew.

## Failure domains
- Preprocessing failure returns a validation error, never a guessed score.
- Model-compute failure triggers timeout plus fallback per the serving contract.
- Logger failure must not fail the response; events buffer and drain async.

## Capacity planning
- Size replicas from peak requests per second divided by per-replica throughput, plus headroom.
- Rehearse the peak with the warmed artifact, not a smaller stand-in, before declaring headroom.
- Queue depth is the early warning: rising queues precede timeout storms.

## Contract evolution
- Additive field changes stay backward compatible; renames and unit changes need a new version.
- Keep the previous schema version serving until client metrics show migration is complete.
- Rejection logs grouped by client version reveal who still sends the old shape.
