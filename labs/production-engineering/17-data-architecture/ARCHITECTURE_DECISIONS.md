# ARCHITECTURE DECISIONS: Distributed Data Architecture Standards
## Lab 17 | Production Engineering Academy

---

## ADR-01: Distributed Consistency Standard (Saga vs 2PC)

### Status: ACCEPTED

### Context
Cross-service transactional workflows previously locked database rows across services, leading to deadlocks and availability drops during network degradation.

### Decisions
1. **Two-Phase Commit (2PC / XA) Strictly Banned**:
   - No distributed transactions spanning separate microservice database boundaries.
2. **Saga Pattern Mandate**:
   - All multi-service business workflows must be implemented as Sagas.
   - Sagas must record their execution log in persistent storage before invoking remote steps.
   - All forward and compensating actions must be strictly idempotent.
3. **CQRS & Read-Your-Own-Writes**:
   - For CQRS systems, user-facing mutation responses must include a version token to route immediate subsequent reads to the primary database until read models catch up.

### Consequences
- Eliminates cross-network row lock deadlocks.
- High availability preserved during network partitions.
