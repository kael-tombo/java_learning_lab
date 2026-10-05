# Vision — Saga Orchestration

## The Big Picture

Saga Orchestration is a centralized approach to managing distributed
transactions. An orchestrator (coordinator) directs the sequence of
steps across services, tracking state and triggering compensating
actions when steps fail. Unlike choreography, orchestration provides
explicit control and visibility.

## Why This Matters

- **Explicit control** — the orchestrator defines the exact sequence.
- **Visibility** — centralized state tracking and monitoring.
- **Simpler debugging** — clear flow of execution.
- **Complex workflows** — supports conditional logic and parallel steps.
- **Compensation management** — orchestrator handles rollbacks.

## Guiding Principles

1. **Centralized coordination** — orchestrator manages the saga flow.
2. **State persistence** — orchestrator state is persisted for recovery.
3. **Compensating actions** — each step has a corresponding undo.
4. **Idempotency** — steps and compensations must be idempotent.
5. **Timeout handling** — steps have SLAs; timeouts trigger compensation.

## Success Criteria

- Orchestrator correctly sequences all saga steps.
- State is persisted and recoverable after crashes.
- Compensating actions execute in correct order on failure.
- Steps and compensations are idempotent.
- Saga state is observable and debuggable.

## Trade-offs to Keep in Mind

| Benefit | Cost |
|---------|------|
| Explicit control | Orchestrator is a single point of failure |
| Visibility | Additional infrastructure complexity |
| Simpler debugging | Potential orchestrator bottleneck |
| Complex workflows | Tight coupling to orchestrator |

## The Road Ahead

Saga Orchestration is ideal for complex, long-running business processes
that require explicit control and visibility. It's commonly used in
financial services, travel booking, and order management.
