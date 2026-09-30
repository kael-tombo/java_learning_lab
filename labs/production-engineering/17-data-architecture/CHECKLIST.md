# CHECKLIST: Data Architecture & Persistence Readiness
## Lab 17 | Production Engineering Academy

---

## 1. Distributed Transaction & Saga Hygiene
- [ ] No 2PC / XA transactions spanning microservice boundaries.
- [ ] Every step in a Saga has a corresponding compensating transaction.
- [ ] All forward and compensating actions verified to be strictly idempotent.
- [ ] Saga state persisted to database before and after each external call.
- [ ] Background reconciler job exists to pick up stuck or retrying compensating transactions.

## 2. CQRS & Read Consistency
- [ ] Read-Your-Own-Writes mechanism implemented for user profile and state updates.
- [ ] Replication lag alerting configured on all database read replicas (page if lag $> 10\text{s}$).
- [ ] Read models can be completely rebuilt from scratch via Kafka replay or CDC snapshots.

## 3. Database Sharding & Partitioning
- [ ] Sharding key chosen with high entropy (e.g. `tenant_id` or `user_uuid`).
- [ ] No cross-shard distributed transactions or cross-shard SQL joins.
