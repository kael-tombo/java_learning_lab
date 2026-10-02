# Theory: EBS Multi-Tier High Availability Architecture

## The EBS R12.2 Multi-Tier Architecture

Oracle EBS R12.2 uses a **split-tier architecture** separating the application tier (middle tier) from the database tier. In HA deployments, both tiers are clustered.

```
┌─────────────────────────────────────────────────────────────────┐
│                        USERS (Global)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  F5 BIG-IP LTM  │  ← Global Server Load Balancing (GSLB)
                    │  (Active/Standby)│
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐    ┌───────▼───────┐    ┌───────▼───────┐
│   Node 1      │    │   Node 2      │    │   Node 3      │
│   (US Prim)   │    │   (EMEA)      │    │   (APAC)      │
│  HTTP/Forms   │    │  HTTP/Forms   │    │  HTTP/Forms   │
│  OAF/OC4J     │    │  OAF/OC4J     │    │  OAF/OC4J     │
│  CM (Report)  │    │  CM (Interface)│   │  CM (Batch)   │
│  Admin (Act)  │    │  Admin (Pas)  │    │  Admin (Pas)  │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Shared APPL_TOP │  ← NFS (NetApp) with noatime
                    │  (Dual FS: Run/  │
                    │   Patch Edition) │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Oracle RAC DB  │  ← 2-node RAC + 1 Physical Standby
                    │  (EBSPROD)      │
                    │  Services:      │
                    │  - EBSPROD_ONLINE│
                    │  - EBSPROD_BATCH │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Data Guard     │  ← SYNC transport, Fast-Start Failover
                    │  (Standby)      │
                    └─────────────────┘
```

## Application Tier Services

Each node runs Oracle HTTP Server (OHS), Forms, OAF (OC4J), Concurrent Manager, and Admin Server. **Specialization** prevents resource contention:

| Service | Node 1 (US) | Node 2 (EMEA) | Node 3 (APAC) |
|---------|-------------|---------------|---------------|
| OHS | Primary | Primary | Primary |
| Forms | 50 processes | 30 processes | 20 processes |
| OAF/OC4J | 40 threads | 25 threads | 15 threads |
| Concurrent Manager | Std + 6 Specialized | Std + 3 Specialized | Std + 3 Specialized |
| Admin Server | **Active** | Passive | Passive |

**Key Principle**: Admin Server runs on only ONE node (active). Others are passive — failover via clusterware.

## Load Balancer (F5 BIG-IP) Configuration

### Pool: ebs_forms_pool (Forms Traffic)
```
Method: Least Connections
Persistence: Source IP (sticky session 30 min)
Monitor: HTTPS /forms/frmservlet
Members: node1:9001, node2:9001, node3:9001
```

### Pool: ebs_oaf_pool (OAF/Self-Service Traffic)
```
Method: Least Connections
Persistence: Cookie (OA7_sesid)
Monitor: HTTP /OA_HTML/AppsLogin
Members: node1:8000, node2:8000, node3:8000
```

### Pool: ebs_cm_pool (Concurrent Manager - internal)
```
Method: Round Robin
Persistence: None
Monitor: TCP port check only
Members: node1:cm_port, node2:cm_port, node3:cm_port
```

**SSL Termination**: F5 terminates SSL, passes HTTP to app nodes. Re-encrypt for sensitive data.

**Health Check**: Must be **application-level** (HTTP 200 on /OA_HTML/AppsLogin), not just TCP. TCP-only misses hung JVMs.

## Database Tier: RAC + Data Guard

### RAC Services for Workload Isolation
```sql
-- Online (interactive) workload: optimize for response time
DBMS_SERVICE.CREATE_SERVICE(
    service_name    => 'EBSPROD_ONLINE',
    goal            => DBMS_SERVICE.GOAL_SERVICE_TIME,
    clb_goal        => DBMS_SERVICE.CLB_GOAL_LONG,
    failover_type   => DBMS_SERVICE.FAILOVER_TYPE_SELECT,
    failover_method => DBMS_SERVICE.FAILOVER_METHOD_BASIC,
    failover_retries => 30,
    failover_delay  => 5
);

-- Batch (concurrent) workload: optimize for throughput
DBMS_SERVICE.CREATE_SERVICE(
    service_name    => 'EBSPROD_BATCH',
    goal            => DBMS_SERVICE.GOAL_THROUGHPUT,
    clb_goal        => DBMS_SERVICE.CLB_GOAL_SHORT,
    failover_method => DBMS_SERVICE.FAILOVER_METHOD_NONE
);
```

**Service Goals**:
- `GOAL_SERVICE_TIME` + `CLB_GOAL_LONG` = route to least busy node for short transactions
- `GOAL_THROUGHPUT` + `CLB_GOAL_SHORT` = route for long-running batch jobs

### Data Guard Configuration (Zero Data Loss)
```sql
-- Primary: SYNC transport for zero data loss
ALTER SYSTEM SET log_archive_dest_2='SERVICE=standby SYNC AFFIRM NET_TIMEOUT=30';

-- Standby: Real-time apply
ALTER DATABASE RECOVER MANAGED STANDBY DATABASE USING CURRENT LOGFILE DISCONNECT;

-- Fast-Start Failover (automatic)
CONFIGURE FAST_START FAILOVER;
ENABLE FAST_START FAILOVER;
ALTER SYSTEM SET fast_start_failover_threshold=30;  -- seconds

-- Monitor lag
SELECT name, value FROM v$dataguard_stats
WHERE name IN ('transport lag', 'apply lag');
```

**RPO < 5 min**: Achieved with SYNC + NET_TIMEOUT=30
**RTO < 30 min**: Fast-Start Failover + FAN notification to app tier

## Concurrent Manager Specialization

Prevents month-end close contention by isolating workloads:

```sql
-- Report Manager (heavy SQL, long-running)
FND_CONCURRENT_QUEUE_PUB.CREATE_QUEUE(
    p_queue_name => 'REPORT_MANAGER_NODE1',
    p_max_processes => 20,
    p_specialization_on => 'Y',
    p_target_node => 'node1.us.example.com'
);

-- Interface Manager (inbound/outbound, high volume)
FND_CONCURRENT_QUEUE_PUB.CREATE_QUEUE(
    p_queue_name => 'INTERFACE_MANAGER_NODE2',
    p_max_processes => 30,
    p_target_node => 'node2.emea.example.com'
);

-- Batch Manager (scheduled jobs)
FND_CONCURRENT_QUEUE_PUB.CREATE_QUEUE(
    p_queue_name => 'BATCH_MANAGER_NODE3',
    p_max_processes => 25,
    p_target_node => 'node3.apac.example.com'
);
```

### Work Shifts for Regional Peaks
```sql
-- US Peak: 8am-6pm EST
FND_CONCURRENT_QUEUE_PUB.CREATE_SHIFT(
    p_queue_name => 'STANDARD', p_shift_name => 'US_PEAK',
    p_start_time => '08:00', p_end_time => '18:00', p_max_processes => 40
);

-- EMEA Peak: 8am-6pm CET = 2am-12pm EST
FND_CONCURRENT_QUEUE_PUB.CREATE_SHIFT(
    p_queue_name => 'STANDARD', p_shift_name => 'EMEA_PEAK',
    p_start_time => '02:00', p_end_time => '12:00', p_max_processes => 25
);

-- APAC Peak: 8am-6pm SGT = 7pm-5am EST
FND_CONCURRENT_QUEUE_PUB.CREATE_SHIFT(
    p_queue_name => 'STANDARD', p_shift_name => 'APAC_PEAK',
    p_start_time => '19:00', p_end_time => '05:00', p_max_processes => 20
);
```

## FS_CLONE (Online Patching) — Zero Downtime

EBS R12.2 uses **dual file systems** (Run edition / Patch edition):

```
Run Edition (fs1)  ← Active production
Patch Edition (fs2) ← Patching target
```

### adop Phases
```
prepare → apply → finalize → cutover → cleanup
```

### Rolling Cutover Across Regions (Zero User Impact)
| Phase | Region | Timing | Impact |
|-------|--------|--------|--------|
| 1 | APAC | Sunday 2am SGT | APAC users on fs1, others unaffected |
| 2 | EMEA | Sunday 2am CET | EMEA users on fs1, others unaffected |
| 3 | US | Sunday 2am EST | US users on fs1, all on new edition |

**Key**: Users stay on Run edition during patching. Cutover is instant (file system switch).

## Environment Tuning (default.env)

```bash
# Connection pooling
JTF_CONNECTION_POOL_SIZE=200
JTF_MAX_CONNECTIONS=500
JTF_CONNECTION_TIMEOUT=30000

# Concurrent Manager threads
FND_CONC_MIN_THREADS=20
FND_CONC_MAX_THREADS=100

# Forms performance
FORMS60_BUFFER_PAGES=50000
FORMS60_CACHE_SIZE=10000
FORMS60_RECORD_GROUP_SIZE=1000
formsCompression.level=9

# NFS mount options (critical!)
# mount -o rw,bg,hard,nointr,rsize=32768,wsize=32768,noatime,timeo=600
```

**`noatime` on NFS**: Eliminates 3x I/O overhead from access time updates on APPL_TOP reads.

## Failover Architecture

### Application Tier Failover (Script + F5)
```bash
#!/bin/bash
SERVICES=("httpd" "forms_server" "oaf_server" "concurrent_manager")
for svc in "${SERVICES[@]}"; do
  if ! pgrep -x "$svc" > /dev/null; then
    # Drain from F5 pool
    tmsh modify ltm pool ebs_forms_pool members modify "node1:9001" state user-down
    # Attempt restart
    $ADMIN_SCRIPTS_HOME/adstrtal.sh -service $svc
    sleep 30
    if pgrep -x "$svc" > /dev/null; then
      tmsh modify ltm pool ebs_forms_pool members modify "node1:9001" state user-up
    fi
  fi
done
```

### Database Tier Failover
1. **RAC Node Failure**: FAN event → app tier redirects connections to surviving node
2. **Site Failure**: Data Guard Fast-Start Failover → automatic standby promotion
3. **Connection Drain**: 30-min window for planned maintenance

## Monitoring Queries

### Forms Sessions per Node
```sql
SELECT node_name, COUNT(*) AS session_count,
       AVG(elapsed_time_seconds) AS avg_session_time
FROM fnd_forms_sessions
WHERE last_connect_date > SYSDATE - 1/24
GROUP BY node_name ORDER BY session_count DESC;
```

### Concurrent Manager Queue Depth
```sql
SELECT cm.concurrent_queue_name, cm.target_node,
       COUNT(cqh.request_id) AS queue_depth,
       AVG((SYSDATE - cqh.actual_start_date) * 24 * 60) AS avg_wait_min
FROM fnd_concurrent_queues cm
LEFT JOIN fnd_concurrent_requests cqh
  ON cm.concurrent_queue_id = cqh.concurrent_queue_id
  AND cqh.phase_code = 'P' AND cqh.hold_flag = 'N'
WHERE cm.enabled_flag = 'Y'
GROUP BY cm.concurrent_queue_name, cm.target_node
ORDER BY avg_wait_min DESC;
```

### OAF Response Times
```sql
SELECT apps_node,
       AVG(response_time_ms) AS avg_ms,
       PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) AS p95_ms
FROM fnd_oaf_response_times
WHERE measurement_time > SYSDATE - 1/24
GROUP BY apps_node;
```

### Data Guard Lag
```sql
SELECT name, value FROM v$dataguard_stats
WHERE name IN ('transport lag', 'apply lag');
```

## Capacity Planning

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU (peak) | > 60% avg | Add node |
| Forms response | > 2 sec | Scale Forms processes |
| CM queue wait | > 30 min | Add specialized managers |
| NFS latency | > 5 ms | Move to local SSD + rsync |
| Data Guard lag | > 5 sec | Investigate network/storage |

## Security

- **TLS Everywhere**: F5 terminates, re-encrypt to app nodes
- **Network Segmentation**: DMZ → App Tier VLAN → DB Tier VLAN
- **Least Privilege**: App tier DB accounts minimal grants
- **Audit Logging**: FND logging → SIEM (Splunk/ELK)

## Summary: HA Checklist

- [ ] 3+ app nodes behind F5 with health checks
- [ ] Specialized CMs per node + regional work shifts
- [ ] 2-node RAC + 1 Standby with SYNC Data Guard
- [ ] RAC services: ONLINE (SERVICE_TIME) + BATCH (THROUGHPUT)
- [ ] FS_CLONE dual FS with rolling regional cutover
- [ ] NFS `noatime`, connection pool 200+, FAN enabled
- [ ] Quarterly failover drills with RTO/RPO measurement
- [ ] Monitoring: Forms sessions, CM queues, OAF response, DG lag