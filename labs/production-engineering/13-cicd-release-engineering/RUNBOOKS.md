# RUNBOOKS: CI/CD, GitOps & Enterprise Release Operations
## Lab 13 | Production Engineering Academy — Top 0.0001% Engineering

---

## Runbook 01: Executing an Emergency GitOps Rollback via ArgoCD

### 1. Severity & Trigger Condition
- **Severity**: P1 / SEV-1
- **Condition**: A newly deployed service exhibits elevated error rates ($> 1\%$) or latency spikes within 30 minutes of a GitOps sync.

### 2. Execution Runbook

#### Option A: Immediate Fast-Rollback via ArgoCD CLI (Sub-Minute)
If time is critical and customer transactions are failing:
```bash
# Rollback the application to the previous successful GitOps revision
argocd app rollback payment-service --to-info
# Or explicitly roll back to previous sync ID:
argocd app rollback payment-service <SYNC_ID>
```
*Note*: This temporarily disables auto-sync to prevent Git from immediately re-applying the bad commit.

#### Option B: Clean GitOps Rollback via Git Revert (Standard)
```bash
# In the gitops-manifests repository:
git checkout main
git pull origin main
git log -n 5 --oneline
# Revert the faulty image bump commit
git revert --no-edit <FAULTY_COMMIT_SHA>
git push origin main
```
ArgoCD will detect the revert commit within 60 seconds and initiate an automated roll back across all worker nodes.

---

## Runbook 02: Aborting and Rolling Back a Failed Argo Rollouts Canary

### 1. Symptoms & Alert
- Prometheus alert: `CanaryAnalysisFailed` or `CanaryHttp5xxRateElevated`.
- Argo Rollouts is paused waiting on manual intervention or automated analysis limit breach.

### 2. Live Triage & Abort

#### Step 1: Inspect Live Canary Rollout Status
```bash
# View real-time canary weight, active pods, and Prometheus metric status
kubectl argo rollouts get rollout payment-service-rollout -n production
```

#### Step 2: Manually Abort Canary (If Not Auto-Aborted)
If the automated analyzer has not triggered but engineers observe business anomalies:
```bash
kubectl argo rollouts abort payment-service-rollout -n production
```
Argo Rollouts immediately flips the traffic weight from the Canary **back to 100% Stable (Baseline)** in $\approx 1\text{ second}$.

#### Step 3: Clean Up Aborted Rollout
```bash
# Set back to stable baseline revision
kubectl argo rollouts undo payment-service-rollout -n production
```

---

## Runbook 03: Resolving a Stuck Flyway Database Migration Table Lock

### 1. Symptoms
- The database migration Kubernetes Job is stuck in `Running` or failed with:
  ```text
  Migration failed !
  Waiting for changelog lock....
  org.flywaydb.core.api.FlywayException: Unable to obtain table lock: flyway_schema_history
  ```
- Application pods are blocked from upgrading because the migration job has not succeeded.

### 2. Forensic Investigation & Remediation

#### Step 1: Inspect Locked PID in PostgreSQL
Connect to the database via psql:
```sql
SELECT pid, query_start, state, query 
FROM pg_stat_activity 
WHERE query LIKE '%flyway_schema_history%' OR state = 'active';
```

#### Step 2: Check for Abandoned Locks
If a previous migration job pod was killed by Kubelet mid-execution:
```sql
-- Check Flyway lock table:
SELECT * FROM flyway_schema_history WHERE success = false;
```

#### Step 3: Clear the Stuck Lock
1. Terminate the blocking PID if active:
   ```sql
   SELECT pg_terminate_backend(<BLOCKING_PID>);
   ```
2. Repair the Flyway schema history table:
   ```bash
   # Run flyway repair command via dedicated one-off container
   kubectl run flyway-repair --rm -it --restart=Never \
     --image=flyway/flyway:10.8.0 -- \
     repair -url=jdbc:postgresql://postgres.database.svc:5432/payments \
     -user=postgres -password=secret
   ```
3. Re-trigger the migration Job:
   ```bash
   kubectl delete job db-migration-job -n production
   argocd app sync payment-service --resource batch:Job:db-migration-job
   ```

---

## Runbook 04: Troubleshooting Kyverno Admission Image Verification Failures

### 1. Symptoms
- Pod creation fails with admission webhook denial:
  ```text
  Error from server: admission webhook "validate.kyverno.svc" denied the request: 
  image ghcr.io/corp/payment:v3.4.0 failed signature verification: 
  no matching signatures found
  ```

### 2. Diagnostic Workflow

#### Step 1: Verify Cosign Signature on the Container Image
Run Cosign verify manually from terminal:
```bash
cosign verify \
  --certificate-identity-regexp "https://github.com/corp/.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/corp/payment:v3.4.0
```
- If verification fails with `no signatures found`: The CI signing step was skipped or failed.
- If verification fails with `issuer mismatch`: The GitHub Actions workflow branch or repository identity did not match the Kyverno policy regex.

#### Step 2: Re-Sign the Container Image in CI
Re-trigger the GitHub Actions release workflow to rebuild and cryptographically sign the container image using keyless OIDC authentication before retrying the deployment.

---

## Runbook 05: Safe Database Column Renaming Execution (Expand-Contract Runbook)

### 1. Pre-Conditions
- Schema mutation required: Rename `users.phone` to `users.mobile`.
- System SLA: $100\%$ zero-downtime; rolling update of 50 pods.

### 2. Execution Phases (Minimum 7-Day Window)

#### Day 1: Phase 1 (Expand)
1. Execute PreSync migration adding new column:
   ```sql
   ALTER TABLE users ADD COLUMN mobile VARCHAR(32);
   ```
2. Deploy Application Release v2 configured with **Dual-Write**:
   - Updates write to both `phone` and `mobile`.
   - Reads continue from `phone`.

#### Day 2: Phase 2 (Async Backfill)
Run background batch backfill during low-traffic window:
```sql
UPDATE users 
SET mobile = phone 
WHERE mobile IS NULL 
AND id BETWEEN 1 AND 50000;
-- Iterate in 50k row batches until 0 rows updated
```

#### Day 4: Phase 3 (Read Switch via Feature Flag)
Flip feature flag `read-from-new-mobile-schema = true` on $10\%$ of traffic, evaluate error rates, then promote to $100\%$.

#### Day 14: Phase 4 (Contract)
Deploy Application Release v3 (stops writing to legacy `phone`). Execute final DDL:
```sql
ALTER TABLE users DROP COLUMN phone;
```
Zero dropped queries, zero application downtime.
