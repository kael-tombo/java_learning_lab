# Lab 09: Administration — Real World Project

## Scenario
A platform team has grown to 34 APEX applications across 9 workspaces and has
been administering the instance ad hoc for two years. Workspace schemas can see
each other, the password policy is still the APEX default, users report login
failures nobody has investigated, and the last patch upgrade was applied without
a tested restore point — recovery from that would have taken a day. There is no
monitoring. The head of engineering has asked for the instance to be run as a
platform: provisioned, monitored, backed up, and patchable.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX administration)
- (link removed) (backup)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/admin/

## Architecture
```
APEX instance
  │
  ├─ Workspaces (9) ──► each with its own schema
  │     └─ Cross-schema grants REMOVED; isolation enforced
  │
  ├─ Security posture
  │     ├─ Password policy: complexity, ageing, lockout
  │     ├─ Session limits + idle timeout
  │     ├─ HTTPS required, HTTP refused
  │     └─ Outbound allow-list (approved hosts only)
  │
  ├─ Observability
  │     ├─ APEX activity log → slowest pages, login failures, errors
  │     ├─ Daily metrics snapshot for trend
  │     └─ Alerting on error rate and lockout spikes
  │
  └─ Lifecycle
        ├─ Declarative app export (34 apps) — versioned in source control
        ├─ Database backup — nightly, tested monthly
        ├─ Restore drill — quarterly, timed
        └─ Pre-upgrade checklist — mandatory before any patch
```

## Implementation sketch
```sql
-- Slowest pages: the activity log is the primary performance evidence
SELECT workspace_id,
       application_id,
       page_id,
       ROUND(AVG(elapsed_time), 1)  avg_ms,
       MAX(elapsed_time)            max_ms,
       COUNT(*)                     executions
  FROM apex_user_activity_log
 WHERE logon_user_id IS NOT NULL
   AND view_time  > SYSDATE - 7
   AND application_id IN (SELECT application_id FROM apex_application p
                           WHERE p.owner = 'ADMIN')
 GROUP BY workspace_id, application_id, page_id
HAVING AVG(elapsed_time) > 3000
 ORDER BY avg_ms DESC;
```

## Requirements
- F1: Workspace provisioning standard with per-team schemas.
- F2: Cross-schema grants removed; isolation verified by test.
- F3: Instance password policy with complexity, ageing, and lockout.
- F4: Session limits and idle timeout enforced.
- F5: HTTPS enforced; HTTP refused.
- F6: Outbound allow-list restricting external calls.
- F7: Activity log monitoring with slowest pages, login failures, and errors.
- F8: Daily metrics snapshot for trend analysis and alerting.
- F9: Declarative export of all 34 applications into source control.
- F10: Nightly backup with a monthly tested restore.
- F11: Quarterly full restore drill with recorded RTO.
- F12: Mandatory pre-upgrade checklist.
- NF1: Zero cross-schema access between workspaces.
- NF2: Every login failure accounted for; no unexplained lockout spikes.
- NF3: p95 page response under 3 seconds across all applications.
- NF4: Restore drill RTO under 4 hours, evidenced.
- NF5: Security baseline — hardened posture verified by scan, not assertion.
- NF6: Every patch preceded by a verified restore point.

## Milestones
- Week 1: Baseline inventory — applications, workspaces, schemas, logins.
- Week 2: Workspace isolation and provisioning standard.
- Week 3: Security posture hardening and verification.
- Week 4: Observability — monitoring views, snapshots, alerting.
- Week 5: Backup, export, and the first full restore drill.
- Week 6: Pre-upgrade checklist, first patch, and handover documentation.

## Verification
- Isolation test: each workspace attempts to read another workspace's table.
- Password policy test including lockout and ageing.
- Restore drill: database plus one application, end to end, timed.
- Alert test: inject an error and confirm the alert fires.
- Patch rehearsal in a non-production clone before production.

## Rollback
Schema grants are reversible; application exports are versioned so any app can be
restored to a prior state; instance settings capture prior values before change.
Document rollback steps for every change.