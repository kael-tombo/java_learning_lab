# Lab 01: EBS Multi-Tier Architecture — Real World Project

## Scenario
A global manufacturer runs EBS R12.2 for 9,400 named users across 14 countries.
Month-end close takes 11 days, the app tier saturates at 100% CPU while the
database sits near 60%, and the concurrent manager backs up every night. You are
hired to redesign the topology — not to rewrite SQL — so that close finishes in
5 days with no data loss on failover.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/racad/
- https://docs.oracle.com/en/database/oracle/oracle-database/19/dbforu/
- https://docs.oracle.com/technologies/ebs/ (EBS High Availability guide)

## Architecture
```
Users ─► GSLB ─┬─► App Node US    (OHS, Forms, OAF, Report CM, Admin ACTIVE)
               ├─► App Node EMEA  (OHS, Forms, OAF, Interface CM)
               └─► App Node APAC  (OHS, Forms, OAF, Batch CM)
                        │
                  Shared APPL_TOP (NFS, noatime)
                        │
        ┌───────────────┴───────────────┐
   RAC 2-node (EBSPROD)            Physical Standby
   svc: _ONLINE / _BATCH           SYNC + FSFO
```

## Implementation sketch
```sql
-- Online: response-time goal, long-lived Forms affinity
BEGIN DBMS_SERVICE.CREATE_SERVICE(
  service_name => 'EBSPROD_ONLINE',
  goal => DBMS_SERVICE.GOAL_SERVICE_TIME,
  clb_goal => DBMS_SERVICE.CLB_GOAL_LONG,
  failover_type => DBMS_SERVICE.FAILOVER_TYPE_SELECT,
  failover_method => DBMS_SERVICE.FAILOVER_METHOD_BASIC,
  failover_retries => 30, failover_delay => 5);
END;
/
-- Zero-loss DR
ALTER SYSTEM SET log_archive_dest_2 =
  'SERVICE=standby SYNC AFFIRM NET_TIMEOUT=30';
```

## Requirements
- F1: 4-node app tier with region-aware service assignment and F5 pools whose
     persistence matches traffic statefulness.
- F2: RAC workload isolation so batch can never starve interactive Forms.
- F3: Specialized Concurrent Managers + work shifts covering all three peaks.
- F4: Data Guard SYNC/FSFO with measured RPO under 5 minutes.
- F5: Rolling `adop` cutover plan that patches without a global outage.
- F6: Monitoring pack reporting Forms sessions, CM queue depth, OAF p95, DG lag.
- F7: Quarterly failover drill with written RTO/RPO evidence.
- F8: Capacity model projecting 24 months of growth.
- F9: NFS `noatime` and connection-pool tuning documented and justified.
- F10: Runbook for node drain, service restart, and pool re-admission.
- NF1: Close completes within 5 business days.
- NF2: 99.95% availability with planned maintenance excluded.
- NF3: p95 interactive response under 2 seconds at peak.
- NF4: CM queue wait under 30 minutes at peak.
- NF5: Security baseline — segmented tiers, TLS, least-privilege DB accounts.
- NF6: Every tier change ships with a rollback procedure.

## Milestones
- Week 1: Baseline capture — AWR/OATM both tiers, CM queue export, close calendar.
- Week 2: Service split and pool redesign in the DR environment.
- Week 3: Specialized CM rollout and shift configuration, one region at a time.
- Week 4: Data Guard SYNC/FSFO tuning and first failover drill.
- Week 5: `adop` rolling cutover rehearsal in non-production.
- Week 6: Production cutover, monitoring pack, and signed-off runbooks.

## Verification
- Load test at 1.5x peak concurrent users with CM backlog held under 30 minutes.
- Failure injection: kill one app node, one RAC instance, and the primary DB.
- Backup/restore drill plus a full failover rehearsal with measured RTO/RPO.
- Close calendar re-run showing the 11-day figure reduced to target.

## Rollback
Each milestone has an inverse: pools revert to the previous config, CM queues are
disabled rather than deleted, and the RAC service change is a `MODIFY_SERVICE`.
Document rollback steps for every schema or service change.