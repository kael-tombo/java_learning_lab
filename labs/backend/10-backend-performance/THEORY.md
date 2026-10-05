# Theory — Backend Performance

## Why it exists
Profile, benchmark, and tune Java services for latency and throughput.

## Core model
Every backend topic reduces to resources, operations, invariants, and failure modes.
For Backend Performance the core model centres on:
- resources and their identifiers
- operations and their semantics
- failure modes and retries
- observability signals

## Mechanics
1. Define the resource/operation surface.
2. Pick the right Spring abstraction.
3. Wire scope, lifecycle, and configuration.
4. Add validation and error handling.
5. Make it observable and testable.

## Mental models
- The controller/service boundary is a contract.
- Idempotency and retries change correctness, not just performance.
- Consistency is a spectrum; pick deliberately (queueing theory and percentiles over averages).

## Common pitfalls
- N+1 queries and chatty remote calls.
- Hidden mutable shared state.
- Treating config as code and vice versa.
- Missing timeouts/backpressure on I/O.

## Trade-off table
| Option | Latency | Complexity | When to choose |
| --- | --- | --- | --- |
| Simple sync | low | low | small load, simple ops |
| Async/reactive | med | med | high concurrency, I/O bound |
| Batch/stream | high setup | med | bulk, throughput oriented |

## Checklist
- [ ] Surface is documented and versioned
- [ ] Errors are classified and mapped
- [ ] Timeouts and retries are explicit
- [ ] Tests cover the boundary
