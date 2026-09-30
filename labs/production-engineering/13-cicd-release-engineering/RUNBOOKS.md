# RUNBOOK: Deployment Failures & Emergency Rollback
## Lab 13 | Production Engineering Academy

---

## RUNBOOK 01: Emergency Abort and Rollback of Argo Rollout

**Severity**: P1  
**Trigger**: Canary error rate exceeds threshold or manual abort required.

### Step 1: Immediately Abort Active Rollout
```bash
# Aborts the rollout and points 100% of traffic back to stable baseline
kubectl argo rollouts abort payment-service-rollout
```

### Step 2: Force Rollback to Previous Stable Git Revision
In GitOps, all state is governed by Git:
```bash
git checkout main
git revert HEAD --no-edit
git push origin main
```
ArgoCD will automatically reconcile and deploy the previous stable commit.

---

## RUNBOOK 02: Failed Database Migration Recovery
If Liquibase/Flyway fails midway through deployment:
1. Identify the failed changeset:
   ```sql
   SELECT * FROM databasechangelog ORDER BY orderexecuted DESC LIMIT 5;
   ```
2. If locks are held on the database:
   ```sql
   SELECT * FROM databasechangeloglock;
   -- If locked due to terminated pod:
   UPDATE databasechangeloglock SET locked = false, lockedby = null WHERE id = 1;
   ```
3. Inspect and correct SQL constraint errors. Never manually edit migration files that have already run on other environments.
