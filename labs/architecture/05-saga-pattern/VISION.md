# Vision — Saga Pattern

## The Big Picture

The Saga pattern manages distributed transactions across multiple services
without distributed locks. Instead of ACID transactions spanning services,
a saga is a sequence of local transactions where each step triggers the
next. If a step fails, compensating transactions undo the previous steps.

## Why This Matters

- **No distributed locks** — services remain autonomous.
- **Eventual consistency** — acceptable for many business scenarios.
- **Scalability** — each service handles its own local transaction.
- **Resilience** — failures are handled through compensation, not rollback.
- **Real-world fit** — matches how businesses actually operate across boundaries.

## Guiding Principles

1. **Local transactions** — each step is a local ACID transaction in one service.
2. **Compensating actions** — every step has a corresponding undo operation.
3. **Orchestration or choreography** — sagas can be coordinated centrally or through events.
4. **Idempotency** — steps may retry; they must be safe to repeat.
5. **Observability** — track saga state across all participating services.

## Success Criteria

- Business operations complete successfully across services.
- Failures trigger appropriate compensating actions.
- No distributed locks are required.
- Saga state is observable and debuggable.
- The system reaches a consistent state even after failures.

## Trade-offs to Keep in Mind

| Benefit | Cost |
|---------|------|
| Service autonomy | Eventual consistency |
| No distributed locks | Compensation logic complexity |
| Scalability | Debugging distributed flows |
| Resilience | Potential temporary inconsistency |

## The Road Ahead

Sagas are essential for microservices architectures where distributed
transactions are impractical. Combined with event-driven patterns, they
enable reliable business processes across service boundaries.
