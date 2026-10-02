# Flashcards: EBS Multi-Tier Architecture

## Application Tier

---
**Q**: EBS R12.2 tier architecture?
**A**: Split-tier: Application tier (middle) + Database tier. Both clustered for HA.

---
**Q**: Three nodes across US, EMEA, APAC — how to distribute 5,000 users?
**A**: US: 2,500 (50%), EMEA: 1,500 (30%), APAC: 1,000 (20%). Size Forms/OAF proportionally.

---
**Q**: Forms processes per user ratio?
**A**: 1 process per 50 users. 5,000 users → 100 total Forms processes.

---
**Q**: OAF threads per user ratio?
**A**: 1 thread per 100 users. 5,000 users → 50 total threads (scale up for JVM overhead).

---
**Q**: Why specialize Concurrent Managers per node?
**A**: Prevents contention. Report storms don't block interfaces. Node 1=Reports, Node 2=Interfaces, Node 3=Batch.

---
**Q**: Admin Server HA model?
**A**: Active/Passive. Only ONE active cluster-wide. Failover via clusterware.

---
**Q**: Work shifts for regional peaks — key principle?
**A**: Define ALL shifts in DB time zone (EST). EMEA 08-18 CET = 02-12 EST. APAC 08-18 SGT = 19-05 EST.

---

## Load Balancer (F5 BIG-IP)

---
**Q**: Forms pool persistence?
**A**: Source IP, 30 min timeout. Forms = stateful socket connections.

---
**Q**: OAF pool persistence?
**A**: Cookie (`OA7_sesid`). OAF = stateless HTTP.

---
**Q**: CM pool persistence?
**A**: None (Round Robin). Internal traffic, no session affinity needed.

---
**Q**: Health check for Forms/OAF pools?
**A**: Application-level: HTTP 200 on `/OA_HTML/AppsLogin`. NOT TCP-only.

---
**Q**: SSL termination?
**A**: F5 terminates SSL, passes HTTP to app nodes. Re-encrypt for sensitive data.

---
**Q**: Connection drain before maintenance?
**A**: `session user-disabled` → wait 30 min → `state user-down`. Graceful session completion.

---

## Database Tier (RAC + Data Guard)

---
**Q**: RAC service for online workload?
**A**: `EBSPROD_ONLINE` — GOAL_SERVICE_TIME, CLB_GOAL_LONG, FAILOVER_TYPE_SELECT.

---
**Q**: RAC service for batch workload?
**A**: `EBSPROD_BATCH` — GOAL_THROUGHPUT, CLB_GOAL_SHORT, FAILOVER_METHOD_NONE.

---
**Q**: Why different CLB_GOAL for online vs batch?
**A**: Online = long-lived Forms connections (LONG affinity). Batch = short-lived CM connections (SHORT).

---
**Q**: Data Guard zero data loss config?
**A**: SYNC transport + AFFIRM + NET_TIMEOUT=30 + MaxAvailability mode.

---
**Q**: Fast-Start Failover threshold 30 means?
**A**: 30 seconds of lost contact before automatic failover.

---
**Q**: RPO < 5 min, RTO < 30 min — how achieved?
**A**: SYNC DG (RPO) + FSFO + FAN notification to app tier (RTO).

---
**Q**: Monitor DG lag query?
**A**: `SELECT name, value FROM v$dataguard_stats WHERE name IN ('transport lag', 'apply lag');`

---

## FS_CLONE (adop) Online Patching

---
**Q**: Dual file system model?
**A**: Run Edition (fs1) = production. Patch Edition (fs2) = patching target.

---
**Q**: adop phases?
**A**: prepare → apply → finalize → cutover → cleanup

---
**Q**: What happens at cutover?
**A**: Atomic file system swap. Run↔Patch editions switch. In-flight requests complete on old edition.

---
**Q**: Rolling cutover sequence for global instance?
**A**: APAC → EMEA → US (follows regional low-usage windows: 02:00 local time each).

---
**Q**: Rollback if cutover fails?
**A**: `adop phase=abort` — reverts to previous Run edition. Zero data loss.

---

## Environment & Performance

---
**Q**: Critical NFS mount option for APPL_TOP?
**A**: `noatime` — eliminates 3x metadata I/O from access time updates.

---
**Q**: Connection pool sizing?
**A**: `JTF_CONNECTION_POOL_SIZE=200`, `JTF_MAX_CONNECTIONS=500`

---
**Q**: Forms compression level?
**A**: 9 (max) — critical for WAN bandwidth reduction.

---
**Q**: JVM heap for OAF?
**A**: `-Xms1024m -Xmx2048m -XX:MaxPermSize=512m` + G1GC (`-XX:+UseG1GC -XX:MaxGCPauseMillis=200`)

---
**Q**: Forms session timeout?
**A**: 1800000 ms (30 min). `formsSession.timeout=1800000`

---

## Monitoring & Validation

---
**Q**: Forms sessions per node query?
**A**: `SELECT node_name, COUNT(*) FROM fnd_forms_sessions WHERE last_connect_date > SYSDATE - 1/24 GROUP BY node_name;`

---
**Q**: CM queue depth with wait time?
**A**: Join `fnd_concurrent_queues` + `fnd_concurrent_requests` where phase='P'. Avg wait = `AVG((SYSDATE - actual_start) * 24 * 60)`.

---
**Q**: OAF response time percentiles?
**A**: `PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) AS p95_ms`

---
**Q**: RAC load balance check?
**A**: `SELECT inst_id, COUNT(*) FROM gv$session GROUP BY inst_id;`

---
**Q**: Quarterly failover drill metrics?
**A**: Target RTO < 30 min, RPO < 5 min. Measure actual. Document in runbook.

---

## Troubleshooting

---
**Q**: Forms timeout — first check?
**A**: `fnd_forms_sessions` for long elapsed time. Network latency or DB contention.

---
**Q**: CM queue backup — cause?
**A**: Insufficient specialized managers, or long-running requests blocking queue.

---
**Q**: RAC imbalance — cause?
**A**: Wrong service goal (THROUGHPUT for online workload).

---
**Q**: DG lag > 5 sec — investigate?
**A**: Network bandwidth, storage I/O on standby, redo generation rate.

---
**Q**: NFS latency > 10 ms — fix?
**A**: Verify `noatime`, check NAS CPU, consider local SSD + rsync for APPL_TOP.

---

## Quick Reference: Key Commands

| Task | Command |
|------|---------|
| Check adop status | `$ADMIN_SCRIPTS_HOME/adop status` |
| Start all services | `$ADMIN_SCRIPTS_HOME/adstrtal.sh` |
| Stop all services | `$ADMIN_SCRIPTS_HOME/adstpall.sh` |
| F5 drain node | `tmsh modify ltm pool ebs_forms_pool members modify "node:port" session user-disabled` |
| RAC service status | `srvctl status service -d EBSPROD -s EBSPROD_ONLINE` |
| DG lag check | `DGMGRL> SHOW DATABASE 'EBSPROD_STANDBY' Lag` |
| FSFO status | `SELECT fsfo_status FROM v$database;` |
| NFS stats | `nfsiostat /u01/install/APPS` |

---

## Study Tips
1. **Draw the architecture** from memory — 3 nodes, F5, RAC, DG
2. **Memorize service goals** — ONLINE vs BATCH
3. **Practice adop phases** — know what each does
4. **Convert time zones** — all shifts in DB TZ
5. **Know `noatime`** — #1 EBS performance tweak
6. **Understand FAN** — how app tier learns of DB failures