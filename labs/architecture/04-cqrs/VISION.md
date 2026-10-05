# Vision — CQRS (Command Query Responsibility Segregation)

## The Big Picture

CQRS separates the operations that read data (queries) from those that
write data (commands). This separation allows each side to be optimized
independently — writes can focus on business rules and consistency,
while reads can be denormalized for fast, flexible querying.

## Why This Matters

- **Independent optimization** — tune read and write models separately.
- **Scalability** — scale read and write workloads independently.
- **Simplified queries** — denormalized read models eliminate complex joins.
- **Security** — different authorization for reads vs writes.
- **Flexibility** — multiple read models for different query needs.

## Guiding Principles

1. **Commands change state** — they represent intent, not data transfer.
2. **Queries return data** — they never modify state.
3. **Models are separate** — read and write models serve different purposes.
4. **Eventual consistency is acceptable** — read models may lag write models.
5. **Right-size the pattern** — not every system needs full CQRS.

## Success Criteria

- Commands and queries are clearly separated in code.
- Read models are optimized for query performance.
- Write models enforce business invariants.
- Read models eventually reflect write model changes.
- The system scales reads and writes independently.

## Trade-offs to Keep in Mind

| Benefit | Cost |
|---------|------|
| Query performance | Data consistency complexity |
| Independent scaling | Infrastructure complexity |
| Simplified domain model | Eventual consistency challenges |
| Flexible read models | Learning curve |

## The Road Ahead

CQRS pairs naturally with Event Sourcing and Event-Driven Architecture.
Together they enable systems that are highly scalable, auditable, and
adaptable to changing query requirements.
