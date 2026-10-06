# Lab 10: Upgrade & Migration — Real World Project

## Scenario
A multinational manufacturer faces three consecutive programmes: a 12 TB EBS
database upgrading 12.1.3 to 12.2.10 inside a 4-day window; an on-prem to AWS
migration that must complete in under 2 hours of downtime at 99.95% uptime; and
an 11.2.0.4 to 19c RAC upgrade on the same database, patched in the same 8-hour
outage as the application. You own all three cutovers.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/dbforu/
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS upgrade)
- https://docs.oracle.com/database/121/UPGRD/ (database upgrade guide)

## Architecture
```
Baseline inventory ─► compatibility matrix ─► prerequisite patches
        │                                            │
        ▼                                            ▼
  ADOP prepare ─► apply ─► finalize ─► cutover ─► cleanup
        │              (dual FS: Run / Patch edition)   │
        │                                               ▼
Pre-upgrade validation snapshot ──────────────────► Post-upgrade diff
                                                       │
Migration path:  DMS full load ─► incremental ─► cutover ─► validate
```

## Implementation sketch
```bash
# ADOP phases — each has an inverse before cleanup
$ADOP_TOP/adop -c prepare  -R run_online  -P fs2
$ADOP_TOP/adop -c apply    -R run_online  -P fs2 -b <patch>
$ADOP_TOP/adop -c finalize -R run_online  -P fs2
$ADOP_TOP/adop -c cutover  -R run_online
$ADOP_TOP/adop -c abort    -R run_online     # rollback before cleanup
```

## Requirements
- F1: Complete customisation inventory with a per-item upgrade disposition.
- F2: Version compatibility matrix across DB, app, Fusion Middleware, reports.
- F3: 12.1.3 → 12.2.10 upgrade executed via `ADOP` within the 4-day window.
- F4: Rolling regional cutover with per-phase rollback and go/no-go gates.
- F5: On-prem → AWS migration using DMS with cutover under 2 hours.
- F6: 11.2.0.4 → 19c RAC upgrade within the same 8-hour outage as app patching.
- F7: Pre/post validation pack proving zero unexplained data differences.
- F8: Tested restore point available before every irreversible step.
- F9: Cutover runbooks with named owners, timings, and comms plan.
- F10: Post-upgrade performance comparison proving no regression.
- NF1: Each cutover completes inside its contracted window.
- NF2: Availability SLA of 99.95% maintained across all three programmes.
- NF3: RPO/RTO satisfied with a documented restore drill per environment.
- NF4: Security baseline — credentials rotated, no `FND_HIDE_DB_PASSWORD=N`.
- NF5: Audit evidence for every change window.
- NF6: Documented rollback for every phase of every cutover.

## Milestones
- Week 1–2: Baseline inventory and compatibility matrix for the 12.2 upgrade.
- Week 3–4: Rehearse the 12.2 upgrade twice in non-production; fix findings.
- Week 5: Production 12.2 cutover with rolling regional validation.
- Week 6: DMS migration rehearsal; 19c compatibility testing in parallel.

## Verification
- Two full rehearsals before any production cutover; timings recorded each time.
- Pre/post validation diffs must reconcile to zero unexplained rows.
- Restore drill from the pre-cutover backup, verified before proceeding.
- Performance comparison against pre-upgrade baselines with no regression.

## Rollback
`ADOP` supports `abort` until cleanup; after cleanup the rollback is a restore
from the tested backup. DMS cutover rolls back by pointing DNS and connection
strings back at the on-prem endpoint. Document rollback steps for every phase.