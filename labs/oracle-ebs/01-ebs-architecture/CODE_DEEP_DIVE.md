# Lab 01: EBS Architecture — Code Deep Dive

## 1. Baseline Evidence Queries

### App tier and database utilisation side by side
```sql
-- Database side: sessions and wait class, month-end window
SELECT wait_class, COUNT(*) sessions, ROUND(AVG(percent_time_waited),2) avg_pct
  FROM v$system_event
 GROUP BY wait_class
 ORDER BY sessions DESC;
```

### Concurrent Manager queue depth and wait
```sql
SELECT cm.concurrent_queue_name,
       cm.max_workers,
       COUNT(cr.request_id) AS pending_requests,
       ROUND(AVG((SYSDATE - cr.actual_start_date) * 24 * 60), 1) AS avg_wait_min,
       MAX((SYSDATE - cr.actual_start_date) * 24 * 60) AS max_wait_min
  FROM fnd_concurrent_queues cm
  LEFT JOIN fnd_concurrent_requests cr
    ON cm.concurrent_queue_id = cr.concurrent_queue_id
   AND cr.phase_code = 'P'          -- Pending
   AND cr.hold_flag  = 'N'
 GROUP BY cm.concurrent_queue_name, cm.max_workers
 ORDER BY avg_wait_min DESC NULLS LAST;
```

### Single-queue confirmation
```sql
-- If this returns one row, every request shares one queue
SELECT concurrent_queue_name, enabled_flag, max_workers
  FROM fnd_concurrent_queues
 WHERE enabled_flag = 'Y' AND specialized_flag = 'N';
```

## 2. Diagnosing `JTF_QUEUE_LOCK` Contention

### Find the SQL touching the lock table
```sql
SELECT sql_id, plan_hash_value, executions, elapsed_time/1e6 elapsed_sec
  FROM v$sql
 WHERE sql_text LIKE '%JTF_QUEUE_LOCK%'
 ORDER BY executions DESC;
```

### Active session history — spinning on the lock
```sql
SELECT sample_time, session_id, event, sql_id, blocking_session
  FROM v$active_session_history
 WHERE sample_time BETWEEN SYSDATE - 1 AND SYSDATE
   AND (event LIKE 'enq: TX%' OR sql_id IN (
         SELECT sql_id FROM v$sql WHERE sql_text LIKE '%JTF_QUEUE_LOCK%'))
 ORDER BY sample_time DESC;
```

### Blocking session detail
```sql
SELECT s.sid, s.serial#, s.username, s.program, s.machine,
       s.blocking_session, s.event, s.sql_id
  FROM v$session s
 WHERE s.blocking_session IS NOT NULL;
```

## 3. Creating Specialised Concurrent Managers

```sql
-- Report Manager: heavy SQL, long-running, isolated on node1
BEGIN
  FND_CONCURRENT_QUEUE_PUB.CREATE_QUEUE(
    queue_name        => 'REPORT_MANAGER_NODE1',
    max_sleep_seconds => 3600,
    max_servers      => 20,
    min_servers      => 2,
    max_process_flag => 'Y',
    min_process_flag => 'Y',
    target_node      => 'node1.us.example.com',
    specialization_on => 'Y',
    p_sleep_flag      => 'Y'
  );
END;
/

-- Interface Manager: high volume, latency sensitive, node2
BEGIN
  FND_CONCURRENT_QUEUE_PUB.CREATE_QUEUE(
    queue_name         => 'INTERFACE_MANAGER_NODE2',
    max_servers       => 30,
    min_servers       => 5,
    target_node       => 'node2.emea.example.com',
    specialization_on => 'Y',
    p_sleep_flag      => 'N'      -- interfaces must not sleep
  );
END;
/

-- Batch Manager: scheduled throughput work, node3
BEGIN
  FND_CONCURRENT_QUEUE_PUB.CREATE_QUEUE(
    queue_name         => 'BATCH_MANAGER_NODE3',
    max_servers       => 25,
    min_servers       => 2,
    target_node       => 'node3.apac.example.com',
    specialization_on => 'Y'
  );
END;
/
```

### Disable (not delete) for rollback safety
```bash
$AD_TOP/bin/fndlmsrv -g APPLICATION_SHORT_NAME -n manager_name -M STOP
# Rollback path is STOP + leave in place; DELETE removes the definition.
```

## 4. Work Shifts

```sql
-- All shifts expressed in DB time zone (assume EST)
BEGIN
  FND_CONCURRENT_QUEUE_PUB.CREATE_SHIFT(
    queue_name     => 'STANDARD',
    shift_name     => 'US_PEAK',
    start_time     => '08:00:00',
    end_time       => '18:00:00',
    max_processes  => 40
  );
END;
/
-- EMEA 08:00-18:00 CET = 02:00-12:00 EST
-- APAC 08:00-18:00 SGT = 19:00-05:00 EST (wraps midnight)
```

## 5. JTF Clustering

### Check current cluster assignment
```bash
$APPL_TOP/admin/admnsrvmgr/utils/adopcmnltn.sh
# Or via the Concurrent Manager Node Monitor form
```

### Enable clustering in the context file
```bash
# glps - The JTF cluster parameter
jtf_cluster=1
```

### Verify a CM is using the cluster
```sql
SELECT node_name, concurrent_queue_name, process_active_flag
  FROM fnd_concurrent_queues
 WHERE specialization_on = 'Y';
```

## 6. Forms Session Distribution

```sql
SELECT apps_node_name AS node,
       COUNT(*) AS sessions,
       ROUND(AVG((SYSDATE - last_connect_date) * 24 * 60), 1) avg_session_min
  FROM fnd_forms_sessions
 WHERE last_connect_date > SYSDATE - 1/24
 GROUP BY apps_node_name
 ORDER BY sessions DESC;
```

## 7. Load Balancing Check (RAC)

```sql
-- Service-level distribution across RAC instances
SELECT inst_id, COUNT(*) sessions,
       ROUND(AVG(CASE WHEN service_name LIKE '%ONLINE%' THEN 1 ELSE 0 END),3) online_ratio
  FROM gv$session
 WHERE username = 'APPS'
 GROUP BY inst_id ORDER BY inst_id;
```

## 8. Root Cause Summary Query

```sql
-- One-query diagnosis: is the CM the constraint?
SELECT
  (SELECT COUNT(*) FROM fnd_concurrent_queues
    WHERE enabled_flag='Y' AND specialized_flag='N')  AS standard_queues,
  (SELECT COUNT(*) FROM fnd_concurrent_requests
    WHERE phase_code='P' AND hold_flag='N')          AS pending_requests,
  (SELECT ROUND(AVG((SYSDATE-actual_start_date)*24*60),1)
     FROM fnd_concurrent_requests
    WHERE phase_code='P' AND hold_flag='N')          AS avg_wait_min,
  CASE WHEN (SELECT COUNT(*) FROM fnd_concurrent_queues
              WHERE enabled_flag='Y' AND specialized_flag='N') = 1
       THEN 'SINGLE QUEUE — specialise'
       ELSE 'Multiple queues — investigate target_node and JTF'
  END AS diagnosis
FROM dual;
```