# EBS Upgrade and Migration — Real World Project

## Scenario
A global manufacturer is upgrading a 12 TB EBS database from 12.1.3 to 12.2.10
inside a 4-day window that is contractually fixed. The instance carries 610
customizations, 4 of which modify standard objects and have already failed once
in testing. Separately, the infrastructure team wants the same instance lifted
to OCI with under 2 hours of downtime. You own both programmes and must not
discover a problem during the production window.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- (link removed) (EBS upgrade and lifecycle)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/upgrd/ (Database Upgrade Guide)
- (link removed)

## Architecture
```
Assessment ─► Compatibility matrix ─► Prerequisite patches
                                          │
                                          ▼
              ADOP: prepare ─► apply ─► finalize ─► cutover ─► cleanup
                     │            │           │          │
              (run FS)      (patch FS)  (merge)   (switch)  (no rollback)
                                          │
Pre-upgrade validation snapshot ◄──────────┤
                                           ▼
                              Post-upgrade diff ──► go/no-go sign-off
```

## Implementation sketch
```bash
# ADOP phase sequence — rollback available only until cleanup
$ADOP_TOP/adop -c prepare  -R run_online -P fs2 -m prepare
$ADOP_TOP/adop -c apply    -R run_online -P fs2 -b 12.2.10
$ADOP_TOP/adop -c finalize -R run_online -P fs2
$ADOP_TOP/adop -c cutover  -R run_online          # users switch here
$ADOP_TOP/adop -c abort    -R run_online          # rollback if validation fails
$ADOP_TOP/adop -c cleanup  -R run_online          # irreversible
```

## Requirements
- F1: Full upgrade assessment with per-object custom code disposition.
- F2: Version compatibility matrix across DB, app, and Fusion Middleware.
- F3: `ADOP` upgrade executed within the 4-day contractual window.
- F4: Rolling regional cutover with per-phase rollback and go/no-go gates.
- F5: Two complete rehearsals in non-production with findings remediated.
- F6: Pre/post validation pack proving zero unexplained data differences.
- F7: Tested restore point available and verified before every cutover.
- F8: OCI lift-and-shift plan with a sub-2-hour downtime budget.
- F9: Cutover runbooks with named owners, timings, and a comms plan.
- F10: Post-upgrade performance comparison proving no regression.
- NF1: Upgrade completed inside the contractual 4-day window.
- NF2: Zero production defects attributable to custom code.
- NF3: Availability SLA of 99.95% maintained across the programme.
- NF4: RPO/RTO satisfied with a restore drill performed before cutover.
- NF5: Security baseline — credentials rotated post-upgrade.
- NF6: Documented rollback for every phase, with the irreversible step named.

## Milestones
- Week 1–2: Assessment, compatibility matrix, and custom code disposition.
- Week 3–4: First full rehearsal; remediate all findings.
- Week 5: Second rehearsal with operations team running the runbook.
- Week 6: Production cutover, validation, and sign-off.

## Verification
- Two rehearsals must both complete inside the estimated window.
- Pre/post validation diffs reconcile to zero unexplained rows.
- Restore drill from the pre-cutover backup, verified before proceeding.
- Performance comparison against the pre-upgrade baseline.

## Rollback
`ADOP` supports `abort` until `cleanup`; afterwards recovery is a restore from
the verified backup point. Document rollback steps for every phase.