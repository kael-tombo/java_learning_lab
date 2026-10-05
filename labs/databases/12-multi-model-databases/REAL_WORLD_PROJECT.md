# Multi Model Databases — Real World Project

## Scenario
Design and implement a production-shaped system where multi model databases is a first-class requirement: correctness under failure, measurable performance, and safe rollout.

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
- F1: multi model databases capability 1 with acceptance test.
- F2: multi model databases capability 2 with acceptance test.
- F3: multi model databases capability 3 with acceptance test.
- F4: multi model databases capability 4 with acceptance test.
- F5: multi model databases capability 5 with acceptance test.
- F6: multi model databases capability 6 with acceptance test.
- F7: multi model databases capability 7 with acceptance test.
- F8: multi model databases capability 8 with acceptance test.
- F9: multi model databases capability 9 with acceptance test.
- F10: multi model databases capability 10 with acceptance test.
- NF1: p95 latency, backup RPO/RTO, and security baseline for multi model databases.
- NF2: p95 latency, backup RPO/RTO, and security baseline for multi model databases.
- NF3: p95 latency, backup RPO/RTO, and security baseline for multi model databases.
- NF4: p95 latency, backup RPO/RTO, and security baseline for multi model databases.
- NF5: p95 latency, backup RPO/RTO, and security baseline for multi model databases.
- NF6: p95 latency, backup RPO/RTO, and security baseline for multi model databases.

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
