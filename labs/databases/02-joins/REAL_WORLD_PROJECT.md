# Joins — Real World Project

## Scenario
Design and implement a production-shaped system where joins is a first-class requirement: correctness under failure, measurable performance, and safe rollout.

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
- F1: joins capability 1 with acceptance test.
- F2: joins capability 2 with acceptance test.
- F3: joins capability 3 with acceptance test.
- F4: joins capability 4 with acceptance test.
- F5: joins capability 5 with acceptance test.
- F6: joins capability 6 with acceptance test.
- F7: joins capability 7 with acceptance test.
- F8: joins capability 8 with acceptance test.
- F9: joins capability 9 with acceptance test.
- F10: joins capability 10 with acceptance test.
- NF1: p95 latency, backup RPO/RTO, and security baseline for joins.
- NF2: p95 latency, backup RPO/RTO, and security baseline for joins.
- NF3: p95 latency, backup RPO/RTO, and security baseline for joins.
- NF4: p95 latency, backup RPO/RTO, and security baseline for joins.
- NF5: p95 latency, backup RPO/RTO, and security baseline for joins.
- NF6: p95 latency, backup RPO/RTO, and security baseline for joins.

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
