# RUNBOOK: Distributed Data Inconsistencies & Saga Reconciliation
## Lab 17 | Production Engineering Academy

---

## RUNBOOK 01: Reconciling Stuck / Uncompensated Sagas

**Severity**: P2 (Data Inconsistency)  
**Alert**: `SagaOrchestrator_StuckCompensatingState_Count > 10`.

### Step 1: Query Stuck Saga Instances
```sql
SELECT saga_id, order_id, state, failure_reason, updated_at
FROM saga_log
WHERE state = 'COMPENSATING'
  AND updated_at < NOW() - INTERVAL '10 minutes'
ORDER BY updated_at ASC;
```

### Step 2: Trigger Out-of-Band Compensation Replayer
Run the administrative reconciliation CLI:
```bash
java -jar /opt/admin/saga-reconciler.jar --retry-compensating --max-batch=100
```
Inspect logs for payment gateway or inventory API responses.

### Step 3: Manual Compensation if Partner Rejects API Refund
If the third-party payment processor permanently rejects automated refund due to account closure:
1. Transition state in database to `MANUAL_INTERVENTION_REQUIRED`.
2. Push ticket to customer operations finance queue for manual wire transfer.

---

## RUNBOOK 02: PostgreSQL Read Replica Lag Triage
Check replication lag in seconds:
```sql
SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds;
```
If lag $> 30\text{s}$: Temporarily force traffic router to direct critical reads to primary database.
