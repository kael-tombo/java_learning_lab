# Quiz: EBS Multi-Tier Architecture

---

## Question 1: Application Tier Specialization
**Why specialize Concurrent Managers per node instead of running all managers on all nodes?**

A) Reduces total number of processes
B) **Prevents resource contention (e.g., month-end reports don't block interfaces)**
C) Simplifies patching
D) Required by Oracle licensing

**Answer: B**

**Explanation**: Specialization isolates workloads. Heavy reports on Node 1 don't consume Interface Manager slots on Node 2. Without specialization, a report storm on one node starves all managers cluster-wide.

---

## Question 2: F5 Persistence for Forms
**Which persistence method is correct for Oracle Forms traffic through F5 BIG-IP?**

A) Cookie persistence (OA7_sesid)
B) **Source IP persistence (30 min timeout)**
C) No persistence (Round Robin)
D) SSL Session ID persistence

**Answer: B**

**Explanation**: Forms maintains stateful connections via socket. Source IP persistence keeps a user's session on the same Forms process. Cookie persistence is for stateless OAF. No persistence breaks Forms sessions.

---

## Question 3: RAC Service Goals
**What is the correct `GOAL` and `CLB_GOAL` for an EBS online (interactive) service?**

A) `GOAL_THROUGHPUT`, `CLB_GOAL_SHORT`
B) **`GOAL_SERVICE_TIME`, `CLB_GOAL_LONG`**
C) `GOAL_SERVICE_TIME`, `CLB_GOAL_SHORT`
D) `GOAL_THROUGHPUT`, `CLB_GOAL_LONG`

**Answer: B**

**Explanation**: Online workload (Forms/OAF) needs low response time → `GOAL_SERVICE_TIME`. Long-lived Forms connections benefit from `CLB_GOAL_LONG` (connection affinity). Batch workload uses THROUGHPUT/SHORT.

---

## Question 4: Data Guard Zero Data Loss
**Which configuration achieves RPO < 5 minutes with Data Guard?**

A) ASYNC transport, MaxPerformance mode
B) **SYNC transport, MaxAvailability mode, NET_TIMEOUT=30**
C) SYNC transport, MaxProtection mode, no timeout
D) ASYNC transport, real-time apply

**Answer: B**

**Explanation**: `SYNC` + `AFFIRM` ensures redo written to standby before commit ack. `NET_TIMEOUT=30` limits primary wait. MaxAvailability allows primary to continue if standby unreachable (after timeout). MaxProtection shuts down primary.

---

## Question 5: FS_CLONE Cutover
**During `adop phase=cutover`, what actually happens?**

A) Patches are applied to the database
B) **File system editions are swapped (Run ↔ Patch)**
C) Application tier services are restarted
D) Database is upgraded

**Answer: B**

**Explanation**: Cutover is an atomic file system switch. Run edition becomes Patch edition and vice versa. No database changes. Services stay running (users on old edition until next request). Zero downtime for in-flight requests.

---

## Question 6: NFS Mount Option Critical for EBS
**Which mount option eliminates 3x I/O overhead on shared APPL_TOP?**

A) `hard`
B) `bg`
C) **`noatime`**
D) `intr`

**Answer: C**

**Explanation**: Without `noatime`, every file read updates access time (metadata write). EBS reads thousands of files per request. `noatime` disables this, reducing NAS I/O by ~66%. Always use on EBS APPL_TOP mounts.

---

## Question 7: Fast-Start Failover Threshold
**What does `FastStartFailoverThreshold = 30` mean?**

A) Wait 30 minutes before failover
B) **Wait 30 seconds before failover**
C) Failover after 30 redo logs
D) Check standby lag every 30 seconds

**Answer: B**

**Explanation**: Threshold is in **seconds**. After 30 seconds of lost contact with primary, observer initiates failover. Set based on RTO requirements. Typical: 30-60 seconds.

---

## Question 8: Concurrent Manager Work Shifts
**EMEA peak is 08:00-18:00 CET. What is the equivalent EST time for shift definition?**

A) 08:00-18:00 EST
B) **02:00-12:00 EST**
C) 14:00-00:00 EST
D) 20:00-06:00 EST

**Answer: B**

**Explanation**: CET = EST + 6 hours (standard time). 08:00 CET = 02:00 EST. Work shifts in EBS are defined in the database time zone (typically EST/UTC). Must convert all regional peaks to DB time zone.

---

## Question 9: Admin Server HA
**How many nodes run the Admin Server in active state in a 3-node cluster?**

A) 3 (all active)
B) 2 (active/active)
C) **1 (active/passive)**
D) 0 (not needed in R12.2)

**Answer: C**

**Explanation**: Admin Server is singleton — only ONE active instance cluster-wide. Others are passive (standby). Failover via clusterware (e.g., Oracle Clusterware, Veritas, or custom script). Running multiple causes metadata corruption.

---

## Question 10: Rolling adop Cutover Sequence
**For a global instance with US, EMEA, APAC nodes, what is the correct rolling cutover order?**

A) US → EMEA → APAC
B) **APAC → EMEA → US**
C) EMEA → US → APAC
D) All simultaneously

**Answer: B**

**Explanation**: Cutover follows regional **low-usage windows**:
- APAC: Sunday 02:00 SGT (US Saturday afternoon, EMEA Saturday evening)
- EMEA: Sunday 02:00 CET (US Saturday evening, APAC Sunday morning)
- US: Sunday 02:00 EST (EMEA Sunday morning, APAC Sunday afternoon)
This minimizes user impact per region.

---

## Answer Key
1. B | 2. B | 3. B | 4. B | 5. B | 6. C | 7. B | 8. B | 9. C | 10. B