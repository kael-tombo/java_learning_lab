# Lab 01: EBS Architecture — Real World Project

## Scenario
A retail client runs EBS 12.2 on-prem with 2,000 concurrent users on a single
application-tier node. During month-end, concurrent request completion time
increases by 400% and users report forms timeouts. The database is a dedicated
Exadata at 60% utilisation while the app tier is pegged at 100%. The CM log
shows `JTF_QUEUE_LOCK` contention. You are the consultant who has to fix it
without an outage.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/racad/
- https://docs.oracle.com/technologies/ebs/ (EBS High Availability guide)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/

## Architecture
```
Users ──► F5 ──► App Node 1 (existing)  ──┬── Standard CM  ◄── contention
              App Node 2 (new)            └── Report CM
              App Node 3 (new)            └── Interface CM
                        │
                  Shared APPL_TOP (NFS, noatime)
                        │
                   RAC DB (Exadata)
```

## Implementation sketch
```sql
-- Diagnose: queue depth and wait time per manager
SELECT cm.concurrent_queue_name,
       COUNT(*) pending,
       AVG((SYSDATE - cr.actual_start_date) * 24 * 60) avg_wait_min
  FROM fnd_concurrent_requests cr
  JOIN fnd_concurrent_queues cm
    ON cm.concurrent_queue_id = cr.concurrent_queue_id
 WHERE cr.phase_code = 'P' AND cr.hold_flag = 'N'
 GROUP BY cm.concurrent_queue_name;

-- JTF_QUEUE_LOCK contention from the wait history
SELECT COUNT(*) lock_events
  FROM v$active_session_history
 WHERE event LIKE 'enq: TX - Row lock contention%'
   AND sql_id IN (SELECT sql_id FROM v$sql
                   WHERE sql_text LIKE '%JTF_QUEUE_LOCK%');
```

## Requirements
- F1: Two-tier evidence gathering using AWR and OATM for both tiers.
- F2: Constraint diagnosis naming app tier saturation with supporting metrics.
- F3: Concurrent Manager audit identifying the single-queue configuration.
- F4: 3-node application tier added behind the existing load balancer.
- F5: Specialised Concurrent Managers per node with target node assignment.
- F6: JTF clustering enabled for calendar-based conflict resolution.
- F7: Work shifts throttling non-critical requests during month-end peaks.
- F8: Load test using the Concurrent Program Load Testing tool.
- F9: Before/after comparison with measured completion time and wait time.
- F10: Rollback plan for every configuration change.
- NF1: Month-end completion time reduced by at least 50%.
- NF2: No user-visible downtime during the remediation.
- NF3: App tier CPU peak below 60% at month-end.
- NF4: CM queue wait under 30 minutes at peak.
- NF5: Security baseline — no new DB accounts, least privilege maintained.
- NF6: RPO/RTO unchanged and a restore drill performed.

## Milestones
- Week 1: Evidence gathering and constraint diagnosis.
- Week 2: Non-production node clone and CM specialisation.
- Week 3: Load test and tuning iteration.
- Week 4: Production rollout node by node, one region at a time.
- Week 5: Work shifts tuned against real month-end data.
- Week 6: Monitoring in place and before/after report delivered.

## Verification
- Concurrent Program Load Testing at 1.5x peak with measured completion time.
- Failure injection: kill a node, confirm work redistributes without data loss.
- Restore drill verifying CM configuration survives recovery.
- Client sign-off on the before/after measurement.

## Rollback
New nodes are added, not replaced; CM queues are disabled rather than deleted;
work shifts are configuration. Document rollback steps for every change.