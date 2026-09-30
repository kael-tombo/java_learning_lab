# RUNBOOK: Database Connection Starvation & Incident Triage
## Lab 05 | Production Engineering Academy

---

## RUNBOOK 01: Connection Pool Saturation (`ConnectionTimeoutException`)

**Severity**: P1 (App unable to query DB)  
**Primary Alert**: `HikariPool - Connection is not available, request timed out after 30000ms`.

### Step 1: Check Current Database Connection Counts
Connect to PostgreSQL host:
```sql
SELECT count(*), state, wait_event_type, wait_event 
FROM pg_stat_activity 
GROUP BY state, wait_event_type, wait_event 
ORDER BY count(*) DESC;
```
If `state = 'active'` count is high: check which queries are running:
```sql
SELECT pid, now() - query_start AS duration, query, state, wait_event
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC
LIMIT 10;
```

### Step 2: Check for Uncommitted / Idle in Transaction Connections
```sql
SELECT pid, now() - xact_start AS xact_duration, query, state
FROM pg_stat_activity
WHERE state = 'idle in transaction'
ORDER BY xact_duration DESC;
```
*Action*: If transactions are open for $> 60\text{s}$ holding locks, terminate the blocker:
```sql
SELECT pg_terminate_backend(<pid>);
```

### Step 3: Mitigate in Application Pods
If connection leak was introduced by recent deploy:
- Enable HikariCP leak detection dynamically:
  `-Dcom.zaxxer.hikari.leakDetectionThreshold=2000`
- Check logs for:
  `Apparent connection leak detected at com.learning.OrderService.processOrder(OrderService.java:42)`
- Roll back deployment if a rogue unclosed connection or unbounded query is found.

---

## RUNBOOK 02: Emergency Mitigation for PostgreSQL Lock Deadlocks
Check active lock graph:
```sql
SELECT blocked_locks.pid     AS blocked_pid,
       blocking_locks.pid    AS blocking_pid,
       blocked_activity.query    AS blocked_statement,
       blocking_activity.query   AS current_statement_in_blocking_process
FROM  pg_catalog.pg_locks         blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks         blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```
Cancel blocking query:
```sql
SELECT pg_cancel_backend(blocking_pid);
```
