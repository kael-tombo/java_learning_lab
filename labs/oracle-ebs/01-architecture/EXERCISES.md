# Exercises: EBS Multi-Tier Architecture

## Exercise 1: Design 3-Node Application Tier (Guided)
**Time**: 30 minutes  
**Difficulty**: Beginner-Intermediate

### Objective
Design the service distribution for a 3-node EBS cluster across US, EMEA, APAC.

### Steps
1. **Calculate Forms Processes**:
   - Total users: 5,000 (US: 2,500, EMEA: 1,500, APAC: 1,000)
   - Ratio: 1 Forms process per 50 users
   - Distribute proportionally
2. **Calculate OAF Threads**:
   - Ratio: 1 thread per 100 users
   - Distribute proportionally
3. **Assign Specialized Concurrent Managers**:
   - Report Manager → Node 1 (US)
   - Interface Manager → Node 2 (EMEA)
   - Batch Manager → Node 3 (APAC)
4. **Admin Server**: Active on Node 1, Passive on others
5. **Document** in architecture diagram

### Deliverable
```
Node 1 (US Primary):
  Forms: 50 processes
  OAF: 40 threads
  CM: Standard + Report Manager (6 specialized)
  Admin: ACTIVE

Node 2 (EMEA):
  Forms: 30 processes
  OAF: 25 threads
  CM: Standard + Interface Manager (3 specialized)
  Admin: PASSIVE

Node 3 (APAC):
  Forms: 20 processes
  OAF: 15 threads
  CM: Standard + Batch Manager (3 specialized)
  Admin: PASSIVE
```

### Verification
- [ ] Total Forms processes = 100 (supports 5,000 users)
- [ ] Total OAF threads = 80 (supports 5,000 users)
- [ ] Each region has specialized CM for local workload

---

## Exercise 2: Configure F5 BIG-IP Pools
**Time**: 25 minutes  
**Difficulty**: Intermediate

### Objective
Write tmsh commands for three load balancer pools with correct persistence.

### Steps
1. **Forms Pool** (`ebs_forms_pool`):
   - Members: 3 nodes on port 9001
   - Method: Least Connections
   - Persistence: Source IP, 30 min timeout
   - Monitor: HTTPS `/forms/frmservlet`

2. **OAF Pool** (`ebs_oaf_pool`):
   - Members: 3 nodes on port 8000
   - Method: Least Connections
   - Persistence: Cookie `OA7_sesid`
   - Monitor: HTTP `/OA_HTML/AppsLogin`

3. **CM Pool** (`ebs_cm_pool`):
   - Members: 3 nodes on CM port
   - Method: Round Robin
   - Persistence: None
   - Monitor: TCP only

### Deliverable
Complete `tmsh` script for all three pools

### Verification
- [ ] Forms pool uses Source IP persistence (sticky Forms sessions)
- [ ] OAF pool uses Cookie persistence (stateless OAF)
- [ ] CM pool has no persistence (internal traffic)
- [ ] Health checks are application-level (not TCP-only)

---

## Exercise 3: RAC Service Configuration
**Time**: 20 minutes  
**Difficulty**: Intermediate

### Objective
Create two RAC services: one for online workload, one for batch.

### Steps
1. **Online Service** (`EBSPROD_ONLINE`):
   ```sql
   -- Goal: SERVICE_TIME, CLB: LONG, Failover: SELECT/BASIC
   ```
2. **Batch Service** (`EBSPROD_BATCH`):
   ```sql
   -- Goal: THROUGHPUT, CLB: SHORT, Failover: NONE
   ```
3. **Explain** why different goals for each workload type

### Verification
- [ ] Online service uses GOAL_SERVICE_TIME + CLB_GOAL_LONG
- [ ] Batch service uses GOAL_THROUGHPUT + CLB_GOAL_SHORT
- [ ] Failover configured appropriately for each

---

## Exercise 4: Concurrent Manager Specialization
**Time**: 25 minutes  
**Difficulty**: Advanced

### Objective
Create specialized Concurrent Manager queues using PL/SQL API.

### Steps
1. **Create 3 Specialized Managers**:
   - Report Manager on Node 1 (max 20 processes)
   - Interface Manager on Node 2 (max 30 processes)
   - Batch Manager on Node 3 (max 25 processes)
2. **Use `FND_CONCURRENT_QUEUE_PUB.CREATE_QUEUE`** with `p_specialization_on => 'Y'`
3. **Set target nodes** correctly

### Verification
- [ ] All three queues created with correct node targeting
- [ ] Specialization enabled
- [ ] Max processes match regional capacity

---

## Exercise 5: Regional Work Shifts
**Time**: 20 minutes  
**Difficulty**: Intermediate

### Objective
Configure work shifts for STANDARD manager matching regional peaks.

### Steps
1. **US Peak**: 08:00-18:00 EST, max 40 processes
2. **EMEA Peak**: 02:00-12:00 EST (08:00-18:00 CET), max 25 processes
3. **APAC Peak**: 19:00-05:00 EST (08:00-18:00 SGT), max 20 processes
4. **Create shifts** using `FND_CONCURRENT_QUEUE_PUB.CREATE_SHIFT`
5. **Assign** to STANDARD queue

### Verification
- [ ] Three shifts created with correct times (all in EST)
- [ ] Peak capacity matches regional user distribution
- [ ] No overlap conflicts

---

## Exercise 6: FS_CLONE Rolling Cutover Plan
**Time**: 30 minutes  
**Difficulty**: Advanced

### Objective
Design a zero-downtime patching plan using adop rolling cutover.

### Steps
1. **Identify low-usage windows** per region:
   - APAC: 02:00-05:00 SGT (Sun)
   - EMEA: 22:00-02:00 CET (Sat/Sun)
   - US: 02:00-05:00 EST (Sun)
2. **Sequence cutover**: APAC → EMEA → US
3. **Document** each phase with timing and validation steps
4. **Rollback plan** if cutover fails

### Deliverable
```markdown
# Rolling Cutover Plan

## Pre-requisites
- Patches applied to Patch Edition (fs2)
- adop phase=finalize complete on all nodes
- Validation scripts ready

## Phase 1: APAC Cutover (Sunday 02:00 SGT)
- Drain APAC node from F5 pools
- Run: adop phase=cutover on node3
- Validate: Forms login, OAF access, CM processing
- Re-add to F5 pools
- Monitor 30 min

## Phase 2: EMEA Cutover (Sunday 02:00 CET)
- [Same steps for node2]

## Phase 3: US Cutover (Sunday 02:00 EST)
- [Same steps for node1]

## Rollback Procedure
- If validation fails: adop phase=abort
- Revert F5 pool membership
- All users remain on Run Edition (fs1)
```

### Verification
- [ ] Cutover sequence follows regional low-usage windows
- [ ] Each phase includes drain, cutover, validate, monitor
- [ ] Rollback procedure documented

---

## Exercise 7: Monitoring Dashboard Queries
**Time**: 20 minutes  
**Difficulty**: Intermediate

### Objective
Write SQL queries for real-time architecture health monitoring.

### Steps
1. **Forms Sessions per Node** (last hour)
2. **Concurrent Manager Queue Depth** with avg wait time
3. **OAF Response Times** (avg, p95, max) per node
4. **Data Guard Lag** (transport + apply)
5. **RAC Load Distribution** (sessions per instance)

### Deliverable
5 SQL queries ready for OEM/Cloud Control or custom dashboard

### Verification
- [ ] All queries execute without error
- [ ] Results show actionable metrics
- [ ] Thresholds documented for alerting

---

## Exercise 8: NFS Mount Optimization
**Time**: 15 minutes  
**Difficulty**: Intermediate

### Objective
Configure optimal NFS mount options for shared APPL_TOP.

### Steps
1. **Current mount**: `rw,bg,hard,intr,rsize=32768,wsize=32768`
2. **Optimize**: Add `noatime`, adjust `timeo`, `retrans`
3. **Explain** why `noatime` critical for EBS

### Deliverable
```bash
# Optimal mount command
mount -o rw,bg,hard,nointr,rsize=32768,wsize=32768,noatime,timeo=600,retrans=2 \
  nas-server:/vol/ebs_appl /u01/install/APPS
```

### Verification
- [ ] `noatime` included (eliminates 3x metadata I/O)
- [ ] `timeo=600` (60 sec timeout for WAN)
- [ ] `retrans=2` (retry twice before error)

---

## Exercise 9: Data Guard Failover Test Plan
**Time**: 25 minutes  
**Difficulty**: Advanced

### Objective
Design quarterly failover drill procedure.

### Steps
1. **Planned Failover** (Primary → Standby):
   - Verify DG lag < 5 sec
   - `DGMGRL> SWITCHOVER TO EBSPROD_STANDBY`
   - Validate app tier reconnects via FAN
   - Measure RTO
   - Switch back

2. **Unplanned Failover Simulation**:
   - Shutdown primary DB
   - Verify Fast-Start Failover triggers
   - Measure actual RTO/RPO

3. **Document** metrics: target RTO < 30 min, RPO < 5 min

### Verification
- [ ] Both planned and unplanned scenarios covered
- [ ] RTO/RPO measurement method defined
- [ ] Validation steps for app tier connectivity

---

## Exercise 10: Capacity Planning Model
**Time**: 20 minutes  
**Difficulty**: Advanced

### Objective
Build growth model for 20% YoY user increase.

### Steps
1. **Current**: 5,000 users, 3 nodes, 55% CPU peak
2. **Year 1**: 6,000 users → Project CPU, add node?
3. **Year 2**: 7,200 users
4. **Year 3**: 8,640 users
5. **Trigger**: Add node when avg CPU > 60% during peak
6. **Seasonal**: 2x capacity for month-end/quarter-end/year-end

### Deliverable
```markdown
| Year | Users | Peak CPU | Nodes Needed | Action |
|------|-------|----------|--------------|--------|
| 0    | 5,000 | 55%      | 3            | Current |
| 1    | 6,000 | 66%      | 4            | Add node |
| 2    | 7,200 | 79%      | 5            | Add node |
| 3    | 8,640 | 95%      | 6            | Add node |

Seasonal Buffer: 2x nodes during close periods
```

### Verification
- [ ] Model shows node addition triggers
- [ ] Seasonal spikes accounted for
- [ ] Cost estimation included