# EBS Upgrade and Migration — Mini Project

## Goal
Plan and rehearse an R12.1 to R12.2 upgrade using `ADOP` editioning in
90 minutes, with a runbook that can be handed to someone else.

## Requirements
- R1: An upgrade assessment listing versions, patch levels, and custom code.
- R2: The chosen upgrade path with the reason it applies here.
- R3: A prerequisite patch list in correct apply order.
- R4: An `ADOP` phase plan with commands and expected durations.
- R5: A rolling cutover sequence with drain, cutover, validate, and monitor.
- R6: A rollback procedure per phase, noting when rollback stops being possible.
- R7: A pre/post validation script producing comparable snapshots.
- R8: A Cloud Manager lifecycle task defined for one environment.

## Steps
1. Capture the environment: DB version, app version, patch level, custom objects.
2. Classify each custom object as compatible, needs fixing, or must be replaced.
3. Select the upgrade path and record why the alternatives do not apply.
4. Build the prerequisite list and confirm ordering constraints.
5. Write the `ADOP` phase plan with commands and realistic durations.
6. Design the cutover sequence, including node drain and pool re-admission.
7. Write rollback per phase; state explicitly that after `cleanup` it is a restore.
8. Build pre/post validation and diff the two snapshots.
9. Define a Cloud Manager lifecycle task and its schedule.
10. Walk the runbook end to end as if you were the person executing it.

## Acceptance criteria
- Every custom object has an explicit upgrade disposition.
- Each `ADOP` phase has a command, a duration estimate, and a rollback.
- The runbook names a go/no-go decision point before each irreversible step.
- Validation snapshots diff to zero unexplained rows.

## Stretch
- Add a downtime patch path and explain when you would choose it instead.
- Estimate the total window for a 4 TB database and justify the estimate.