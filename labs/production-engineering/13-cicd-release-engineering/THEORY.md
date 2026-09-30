# THEORY: Release Engineering & Deployment Strategies
## Lab 13 | Production Engineering Academy

---

## 1. Zero-Downtime Deployment Archetypes

```
1. Rolling Update:
   Pod 1 (v1 -> v2) -> Pod 2 (v1 -> v2) -> Pod 3 (v1 -> v2)
   Risk: Fleet runs mixed versions (v1 and v2 simultaneously); DB schema must support both.

2. Blue/Green:
   [Blue Fleet (v1) - 100% Traffic]     [Green Fleet (v2) - 0% Traffic]
                     \                  /
                      [Router / Ingress]
   Switch router instant cutover: 100% traffic flips to Green.
   Risk: Requires 2x infrastructure cost; instant cutover can shock downstream caches.

3. Canary Deployment (Gold Standard):
   95% Traffic -> Baseline (v1)
    5% Traffic -> Canary (v2)
   Automated metric analysis (Prometheus SLO / error rate / latency) runs for 30 minutes.
   If healthy: step up 10% -> 25% -> 50% -> 100%. If unhealthy: automated instant rollback.
```

---

## 2. Database Schema Migration Invariants (The Expand-Contract Pattern)

A database schema change and application code change must **never** be coupled in the same deployment:

1. **Step 1 (Expand)**: Add the new column/table as optional or nullable. Deploy to database. (Both v1 and v2 code can run).
2. **Step 2 (Dual-Write)**: Deploy v2 application code that writes to BOTH old and new schemas, reading from the old schema.
3. **Step 3 (Backfill)**: Run asynchronous migration script to populate older historical records into the new schema.
4. **Step 4 (Read New)**: Deploy v3 application code that reads from the new schema and writes to both.
5. **Step 5 (Contract)**: Stop writing to the old schema. Drop the old column/table in the database.

---

## 3. GitOps & Declarative Delivery (ArgoCD)

- Git is the single source of truth for desired infrastructure and application state.
- ArgoCD running inside Kubernetes continuously reconciles live cluster state against the Git repository.
- Drift Detection: Any manual `kubectl edit` or uncommitted modification is automatically overwritten by the GitOps operator.
- Rollback is simply a `git revert` commit.
