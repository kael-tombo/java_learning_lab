# Code Deep Dive: EBS Architecture Configuration Internals

## F5 BIG-IP Pool Configuration (tmsh)

### Forms Pool with Source IP Persistence
```bash
# Create pool
tmsh create ltm pool ebs_forms_pool \
    load-balancing-mode least-connections-member \
    members add { node1.us.example.com:9001 node2.emea.example.com:9001 node3.apac.example.com:9001 } \
    monitor https

# Source IP persistence (30 min timeout)
tmsh create ltm persistence source-addr forms_persist \
    timeout 1800 \
    match-across-services enabled

# Assign to pool
tmsh modify ltm pool ebs_forms_pool persistence add { forms_persist }

# Health monitor (deeper than TCP)
tmsh create ltm monitor https forms_monitor \
    interval 10 \
    timeout 31 \
    send "GET /forms/frmservlet HTTP/1.1\r\nHost: ebs.example.com\r\nConnection: Close\r\n\r\n" \
    receive "HTTP/1.1 200"
```

### OAF Pool with Cookie Persistence
```bash
tmsh create ltm pool ebs_oaf_pool \
    load-balancing-mode least-connections-member \
    members add { node1:8000 node2:8000 node3:8000 } \
    monitor http

tmsh create ltm persistence cookie oaf_persist \
    cookie-name OA7_sesid \
    expiration 1800 \
    method insert

tmsh modify ltm pool ebs_oaf_pool persistence add { oaf_persist }
```

### Connection Draining (Maintenance)
```bash
# Graceful drain (30 min)
tmsh modify ltm pool ebs_forms_pool members modify "node1:9001" session user-disabled
# Wait for active sessions to complete
# Then: state user-down for hard removal
tmsh modify ltm pool ebs_forms_pool members modify "node1:9001" state user-down
```

## RAC Service Configuration Deep Dive

### Service Attributes Explained
```sql
DBMS_SERVICE.CREATE_SERVICE(
    service_name    => 'EBSPROD_ONLINE',
    network_name   => 'EBSPROD_ONLINE',  -- TNS alias
    goal           => DBMS_SERVICE.GOAL_SERVICE_TIME,    -- Minimize response time
    clb_goal       => DBMS_SERVICE.CLB_GOAL_LONG,        -- Long connection affinity
    failover_method => DBMS_SERVICE.FAILOVER_METHOD_BASIC,  -- Reconnect on failure
    failover_type  => DBMS_SERVICE.FAILOVER_TYPE_SELECT,    -- SELECT failover
    failover_retries => 30,                                   -- Retry 30 times
    failover_delay  => 5,                                     -- 5 sec between retries
    edition        => 'ORA$BASE',
    pdl_goal       => DBMS_SERVICE.PDL_GOAL_NONE
);
```

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `GOAL_SERVICE_TIME` | Online workload | Route to node with best response time |
| `GOAL_THROUGHPUT` | Batch workload | Route for max throughput |
| `CLB_GOAL_LONG` | Online | Long-lived connections (Forms) |
| `CLB_GOAL_SHORT` | Batch | Short-lived connections (CM) |
| `FAILOVER_TYPE_SELECT` | SELECT statements | Transparent failover for reads |
| `FAILOVER_TYPE_SESSION` | Full session | Full session failover (more overhead) |

### Service Modification
```sql
-- Modify existing service
DBMS_SERVICE.MODIFY_SERVICE(
    service_name => 'EBSPROD_ONLINE',
    goal         => DBMS_SERVICE.GOAL_SERVICE_TIME,
    clb_goal     => DBMS_SERVICE.CLB_GOAL_LONG
);

-- Delete service
DBMS_SERVICE.DELETE_SERVICE(service_name => 'OLD_SERVICE');
```

### Client-Side TNS Entry (apps tier)
```tns
EBSPROD_ONLINE =
  (DESCRIPTION =
    (LOAD_BALANCE = ON)
    (FAILOVER = ON)
    (ADDRESS = (PROTOCOL = TCP)(HOST = rac-scan)(PORT = 1521))
    (CONNECT_DATA =
      (SERVICE_NAME = EBSPROD_ONLINE)
      (FAILOVER_MODE =
        (TYPE = SELECT)
        (METHOD = BASIC)
        (RETRIES = 30)
        (DELAY = 5)
      )
    )
  )
```

## Forms Configuration (formsweb.cfg)

### Node-Specific Settings
```properties
# Node 1 - US Primary
formsListener.listenAddress=node1.us.example.com
formsListener.listenPort=9001
formsSession.maxConnections=500
formsSession.minConnections=50
formsSession.timeout=1800000  # 30 min
formsSession.caching=enabled
formsCompression.level=9
formsNetwork.jpiSpeed=14
formsNetwork.trace=false

# Metrics collection for OAM
formsMetric.enabled=true
formsMetric.interval=60
formsMetric.destination=OAM_REPOSITORY
```

### Key Parameters
| Parameter | Recommended | Impact |
|-----------|-------------|--------|
| `maxConnections` | 500 (US), 300 (EMEA), 200 (APAC) | Concurrent Forms sessions |
| `minConnections` | 10% of max | Pre-spawned processes |
| `compression.level` | 9 | WAN bandwidth reduction |
| `session.timeout` | 1800000 ms | 30 min idle timeout |

## OAF/OC4J Configuration (default.env)

### JVM Tuning for OAF
```bash
# Heap sizing (per OC4J instance)
JAVA_OPTIONS="-Xms1024m -Xmx2048m -XX:MaxPermSize=512m"

# GC tuning for low pause
JAVA_OPTIONS="${JAVA_OPTIONS} -XX:+UseG1GC -XX:MaxGCPauseMillis=200"

# Connection pooling
JTF_CONNECTION_POOL_SIZE=200
JTF_MAX_CONNECTIONS=500
JTF_CONNECTION_TIMEOUT=30000

# EBS-specific
FND_CONC_MIN_THREADS=20
FND_CONC_MAX_THREADS=100
```

### OC4J Instance Count
```bash
# Per node (adjust by region capacity)
# Node 1 (US): 4 OC4J instances × 10 threads = 40
# Node 2 (EMEA): 3 × 8 = 24
# Node 3 (APAC): 2 × 8 = 16
```

## Concurrent Manager Deep Dive

### Queue Creation with Specialization
```sql
BEGIN
    FND_CONCURRENT_QUEUE_PUB.CREATE_QUEUE(
        p_queue_name         => 'REPORT_MANAGER_NODE1',
        p_application_id     => 0,
        p_max_processes      => 20,        -- Max concurrent requests
        p_running_processes  => 15,        -- Target running
        p_queue_size         => 200,       -- Pending request buffer
        p_specialization_on  => 'Y',       -- Only specialized requests
        p_enabled_flag       => 'Y',
        p_target_node        => 'node1.us.example.com',
        p_cache_size         => 10,        -- Request cache
        p_sleep_seconds      => 60,        -- Poll interval
        p_hold_flag          => 'N'
    );
END;
/
```

### Work Shift Assignment
```sql
BEGIN
    FND_CONCURRENT_QUEUE_PUB.CREATE_SHIFT(
        p_queue_name    => 'REPORT_MANAGER_NODE1',
        p_shift_name    => 'US_PEAK',
        p_start_time    => '08:00',
        p_end_time      => '18:00',
        p_max_processes => 40,   -- Double capacity during peak
        p_enabled       => 'Y'
    );
    
    -- Assign shift to queue
    FND_CONCURRENT_QUEUE_PUB.UPDATE_QUEUE(
        p_queue_name    => 'REPORT_MANAGER_NODE1',
        p_shift_name    => 'US_PEAK',
        p_enabled       => 'Y'
    );
END;
/
```

### Queue Monitoring Query
```sql
SELECT 
    cq.concurrent_queue_name,
    cq.target_node,
    cq.max_processes,
    cq.running_processes,
    (SELECT COUNT(*) 
     FROM fnd_concurrent_requests cr
     WHERE cr.concurrent_queue_id = cq.concurrent_queue_id
       AND cr.phase_code = 'P'
       AND cr.hold_flag = 'N') AS pending_requests,
    (SELECT AVG((SYSDATE - cr.actual_start_date) * 24 * 60)
     FROM fnd_concurrent_requests cr
     WHERE cr.concurrent_queue_id = cq.concurrent_queue_id
       AND cr.phase_code = 'R'
       AND cr.actual_start_date > SYSDATE - 1) AS avg_runtime_min
FROM fnd_concurrent_queues cq
WHERE cq.enabled_flag = 'Y'
ORDER BY pending_requests DESC;
```

## FS_CLONE (adop) Commands

### Status Check
```bash
$ADMIN_SCRIPTS_HOME/adop status
# Output shows: Current Run Edition (fs1 or fs2), Patch Edition, Phase
```

### Phase Execution
```bash
# Phase 1: Prepare (create patch edition snapshot)
$ADMIN_SCRIPTS_HOME/adop phase=prepare

# Phase 2: Apply (apply patches to patch edition)
$ADMIN_SCRIPTS_HOME/adop phase=apply patches=<patch_list>

# Phase 3: Finalize (compile, generate jars)
$ADMIN_SCRIPTS_HOME/adop phase=finalize

# Phase 4: Cutover (switch editions - DOWNTIME WINDOW)
$ADMIN_SCRIPTS_HOME/adop phase=cutover

# Phase 5: Cleanup (remove old patch edition)
$ADMIN_SCRIPTS_HOME/adop phase=cleanup
```

### Rolling Cutover Script
```bash
#!/bin/bash
# Regional cutover sequence

# Phase 1: APAC (Sunday 02:00 SGT)
echo "Cutover APAC nodes..."
ssh node3.apac "$ADMIN_SCRIPTS_HOME/adop phase=cutover"
sleep 300  # 5 min validation

# Phase 2: EMEA (Sunday 02:00 CET)  
echo "Cutover EMEA nodes..."
ssh node2.emea "$ADMIN_SCRIPTS_HOME/adop phase=cutover"
sleep 300

# Phase 3: US (Sunday 02:00 EST)
echo "Cutover US nodes..."
ssh node1.us "$ADMIN_SCRIPTS_HOME/adop phase=cutover"

# Verify all on new edition
for node in node1.us node2.emea node3.apac; do
    ssh $node "$ADMIN_SCRIPTS_HOME/adop status | grep 'Run Edition'"
done
```

## Data Guard Fast-Start Failover

### Configuration
```sql
-- On Primary
ALTER SYSTEM SET dg_broker_start=TRUE SCOPE=BOTH;

-- Configure broker
DGMGRL> CONNECT sys/password@primary
DGMGRL> CREATE CONFIGURATION 'ebs_dg' AS PRIMARY DATABASE IS 'EBSPROD' CONNECT IDENTIFIER IS 'EBSPROD_PRIMARY';
DGMGRL> ADD DATABASE 'EBSPROD_STANDBY' AS CONNECT IDENTIFIER IS 'EBSPROD_STANDBY' MAINTAINED AS PHYSICAL;
DGMGRL> ENABLE CONFIGURATION;

-- Fast-Start Failover
DGMGRL> EDIT CONFIGURATION SET PROTECTION MODE AS MaxAvailability;
DGMGRL> EDIT DATABASE 'EBSPROD' SET PROPERTY FastStartFailoverTarget = 'EBSPROD_STANDBY';
DGMGRL> EDIT DATABASE 'EBSPROD_STANDBY' SET PROPERTY FastStartFailoverTarget = 'EBSPROD';
DGMGRL> ENABLE FAST_START FAILOVER;
DGMGRL> EDIT CONFIGURATION SET PROPERTY FastStartFailoverThreshold = '30';
```

### Monitoring
```sql
-- Check FSFO status
SELECT fsfo_status, target_standby, observer_host
FROM v$database;

-- Check lag (should be < 5 sec for MaxAvailability)
SELECT name, value, time_computed
FROM v$dataguard_stats
WHERE name IN ('transport lag', 'apply lag', 'estimated startup time');

-- Observer status (if used)
DGMGRL> SHOW FAST_START FAILOVER;
```

## Health Check Script (Application Tier)

```bash
#!/bin/bash
# /u01/scripts/health_check.sh - Runs every 5 min via cron

LOG="/u01/logs/health_check_$(date +%Y%m%d).log"
NODE=$(hostname -s)

check_service() {
    local svc=$1
    local port=$2
    if ! pgrep -x "$svc" > /dev/null; then
        echo "$(date): $svc DOWN on $NODE" >> $LOG
        # Drain from F5
        tmsh modify ltm pool ebs_forms_pool members modify "${NODE}:${port}" state user-down
        # Attempt restart
        $ADMIN_SCRIPTS_HOME/adstrtal.sh -service $svc >> $LOG 2>&1
        sleep 30
        if pgrep -x "$svc" > /dev/null; then
            tmsh modify ltm pool ebs_forms_pool members modify "${NODE}:${port}" state user-up
            echo "$(date): $svc RESTORED on $NODE" >> $LOG
        else
            echo "$(date): $svc FAILED TO RESTART on $NODE" >> $LOG
            # Alert: send to PagerDuty/OpsGenie
        fi
    fi
}

check_service "httpd" 8000
check_service "forms_server" 9001
check_service "oaf_server" 8000
check_service "concurrent_manager" 0  # No port, process check only
```

## FAN (Fast Application Notification) Setup

### Enable FAN on RAC
```sql
-- On each RAC node
ALTER SYSTEM SET service_names='EBSPROD_ONLINE,EBSPROD_BATCH' SCOPE=BOTH;

-- Enable FAN events
ALTER SYSTEM SET cluster_database=true SCOPE=SPFILE;

-- Configure ONS (Oracle Notification Service)
srvctl modify nodeapps -onsport 6200
```

### App Tier FAN Configuration (default.env)
```bash
# Enable FAN subscription
FAN_ENABLED=TRUE
ONS_HOSTS="rac1:6200,rac2:6200"
```

## Performance Benchmarks Validation

### Baseline Collection
```sql
-- Forms response time by region
SELECT node_name, 
       AVG(response_time_ms) AS avg_ms,
       PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) AS p95_ms,
       MAX(response_time_ms) AS max_ms
FROM fnd_forms_response_times
WHERE measurement_time > SYSDATE - 1
GROUP BY node_name;

-- Concurrent request throughput
SELECT 
    TRUNC(actual_start_date, 'HH') AS hour,
    COUNT(*) AS requests_completed,
    AVG((actual_completion_date - actual_start_date) * 24 * 60) AS avg_duration_min
FROM fnd_concurrent_requests
WHERE phase_code = 'C' 
  AND actual_start_date > SYSDATE - 7
GROUP BY TRUNC(actual_start_date, 'HH')
ORDER BY hour;
```

## Troubleshooting Common Issues

| Symptom | Diagnostic Query | Likely Cause |
|---------|------------------|--------------|
| Forms timeout | `SELECT * FROM fnd_forms_sessions WHERE elapsed_time_seconds > 1800` | Network latency, DB contention |
| CM queue backup | `SELECT * FROM fnd_concurrent_requests WHERE phase_code='P' AND hold_flag='N'` | Insufficient CM processes, long queries |
| RAC imbalance | `SELECT inst_id, COUNT(*) FROM gv$session GROUP BY inst_id` | Service goal misconfiguration |
| DG lag > 5s | `SELECT * FROM v$dataguard_stats WHERE name='apply lag'` | Network, storage I/O, redo rate |
| NFS latency | `nfsiostat /u01/install/APPS` | Missing `noatime`, undersized NAS |

## Key Configuration Files Locations

| File | Location | Purpose |
|------|----------|---------|
| `formsweb.cfg` | `$FORMS_WEB_CONFIG_FILE` | Forms Listener config |
| `default.env` | `$APPL_TOP/admin/$CONTEXT_NAME.env` | App tier environment |
| `context.xml` | `$INST_TOP/ora/10.1.3/j2ee/oacore/config/` | OC4J data sources |
| `adopmnctl.sh` | `$ADMIN_SCRIPTS_HOME/` | OPMN control |
| `adstrtal.sh` | `$ADMIN_SCRIPTS_HOME/` | Start all services |
| `adstpall.sh` | `$ADMIN_SCRIPTS_HOME/` | Stop all services |