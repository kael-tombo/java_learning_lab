# Lab 10: Upgrade & Migration — Mini Project

## Goal
Plan and rehearse a full 12.1.3 to 12.2.10 upgrade with `ADOP` editioning in
90 minutes, and produce a runbook with rollback at every step.

## Requirements
- R1: A version inventory listing DB, app, and patch levels plus all custom code.
- R2: A prerequisite patch matrix in correct apply order.
- R3: An `ADOP` phase plan (prepare, apply, finalize, cutover, cleanup) with the
      command for each phase.
- R4: A rolling cutover sequence with the drain/validate/monitor steps.
- R5: A rollback procedure for each `ADOP` phase, including `phase=abort`.
- R6: A pre-upgrade validation script (row counts, key totals, checksums).
- R7: A post-upgrade validation script producing a comparable snapshot.
- R8: A timed cutover runbook with named decision points and go/no-go gates.

## Steps
1. Record the current environment: versions, patch levels, custom objects.
2. Search for custom code touching objects the upgrade will change.
3. Build the prerequisite matrix and confirm apply order.
4. Write the `ADOP` phase plan with exact commands and expected duration.
5. Design the cutover sequence including F5 drain and pool re-admission.
6. Write rollback for each phase; confirm `abort` is safe mid-sequence.
7. Build pre-upgrade validation capturing counts, totals, and checksums.
8. Build the matching post-upgrade validation and diff the snapshots.
9. Rehearse the cutover on a copy and record actual timings.

## Acceptance criteria
- Every custom object is classified as safe, fix, or replace.
- Each `ADOP` phase has a command, an expected duration, and a rollback.
- Pre/post validation diffs to zero unexplained rows.
- The runbook has a go/no-go decision point before each irreversible step.

## Stretch
- Add a DMS replication cutover plan with a sub-2-hour target and a fallback.
- Draft the 11.2 to 19c RAC upgrade sequence and name the 19c incompatibilities
  that need testing.