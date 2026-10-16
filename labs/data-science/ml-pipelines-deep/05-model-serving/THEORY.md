# Model Serving - Theory

Serving means answering prediction requests from a trained model. Three patterns cover the space.

## Serving patterns
- Batch inference scores stored rows on a schedule. Highest throughput, latency in minutes to hours.
- Online inference answers one request at a time over a request/response interface. Latency budget per request, usually summarized with p50 and p99.
- Streaming inference scores events as they flow through, keeping per-event state such as windows or counters.

## Latency vocabulary
- p50 is the median request latency; p99 is the value below which 99% of requests fall.
- Interactive use cases size timeouts and capacity from the tail (p99), not the mean, because one slow dependency stalls the response.
- Latency per request decomposes into preprocessing + model compute + postprocessing + network and queueing.

## Batching tradeoff
- Fixed per-call overhead is amortized over a batch: latency(batch) = overhead + batchSize * perItem.
- Throughput rises with batch size while latency also rises, so online paths cap batch size or wait time.
- Dynamic batching waits a bounded time to fill a batch; the bound keeps tail latency predictable.

## Versions and rollouts
- Every served model carries a version; requests and logs record which version answered.
- Shadow runs the new version alongside production without acting on its outputs, for comparison.
- Canary sends a small traffic share to the new version and compares error and latency distributions.
- Blue-green keeps two stacks and moves traffic between them so rollback is a routing change.

## Interfaces and operations
- Request/response schemas fix field names, types, units, and version handling for missing or extra fields.
- Warmup loads weights and runs sample inferences before the instance takes traffic, avoiding cold-start spikes.
- Resource sizing balances weight memory against preprocessing CPU; replicas scale with peak requests per second plus headroom.
