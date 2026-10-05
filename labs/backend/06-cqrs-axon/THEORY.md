# Theory — CQRS with Axon Framework

## Why it exists
Separate writes and reads with commands, events, and projections.

## Core model
Every backend topic reduces to resources, operations, invariants, and failure modes.
For CQRS with Axon Framework the core model centres on:
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
- Consistency is a spectrum; pick deliberately (event sourcing as an append-only log; read-model lag as a distribution).

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
