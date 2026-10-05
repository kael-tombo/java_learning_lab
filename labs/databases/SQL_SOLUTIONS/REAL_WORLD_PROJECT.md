# SQL SOLUTIONS — Real World Project

## Scenario
Design and implement a production-shaped system where sql solutions is a first-class requirement: correctness under failure, measurable performance, and safe rollout.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://www.postgresql.org/docs/
- https://use-the-index-luke.com/

## Architecture
```
App (Spring Boot) → Repo/JDBC → Database → Replication/Backup → Observability
```

## Implementation sketch
```java
@Repository
public interface OrderRepo extends JpaRepository<Order, Long> {
    @Query("select o from Order o where o.status = :s")
    List<Order> findByStatus(String s);
}
```

## Requirements
- F1: sql solutions capability 1 with acceptance test.
- F2: sql solutions capability 2 with acceptance test.
- F3: sql solutions capability 3 with acceptance test.
- F4: sql solutions capability 4 with acceptance test.
- F5: sql solutions capability 5 with acceptance test.
- F6: sql solutions capability 6 with acceptance test.
- F7: sql solutions capability 7 with acceptance test.
- F8: sql solutions capability 8 with acceptance test.
- F9: sql solutions capability 9 with acceptance test.
- F10: sql solutions capability 10 with acceptance test.
- NF1: p95 latency, backup RPO/RTO, and security baseline for sql solutions.
- NF2: p95 latency, backup RPO/RTO, and security baseline for sql solutions.
- NF3: p95 latency, backup RPO/RTO, and security baseline for sql solutions.
- NF4: p95 latency, backup RPO/RTO, and security baseline for sql solutions.
- NF5: p95 latency, backup RPO/RTO, and security baseline for sql solutions.
- NF6: p95 latency, backup RPO/RTO, and security baseline for sql solutions.

## Milestones
- Week 1: deliver increment 1 with tests and a short design note.
- Week 2: deliver increment 2 with tests and a short design note.
- Week 3: deliver increment 3 with tests and a short design note.
- Week 4: deliver increment 4 with tests and a short design note.
- Week 5: deliver increment 5 with tests and a short design note.
- Week 6: deliver increment 6 with tests and a short design note.

## Verification
- Load test, failure injection, backup restore drill — all must pass before sign-off.

- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
- Ops note: document rollback steps for every schema change.
