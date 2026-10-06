# Lab 09: Security (SOD Remediation) — Mini Project

## Goal
Detect, remediate, and prevent SOD conflicts for a small user population in
90 minutes, with evidence.

## Requirements
- R1: A duty catalogue and conflict matrix with at least 6 duties and 5 conflicts.
- R2: A detection query operating at the user-assignment level.
- R3: A demonstration that responsibility-level queries find nothing.
- R4: Risk ranking by severity weighted by value at risk.
- R5: A remediation procedure removing only the conflicting responsibility.
- R6: A preventive control that blocks a conflicting grant.
- R7: An exception table with `NOT NULL` expiry and an overdue report.
- R8: Password visibility scan across all profile levels.

## Steps
1. Define duties and conflicts in tables; load 8 duties and 6 conflicts.
2. Create 20 users with deliberately conflicting responsibility assignments.
3. Run the detection query; confirm the violations found.
4. Run the responsibility-level query; confirm it returns nothing.
5. Risk-rank the violations by severity and value.
6. Remediate the top three, recording alternate paths.
7. Attempt a conflicting assignment; confirm the block fires.
8. Create two time-bound exceptions and run the overdue query.
9. Scan all profile levels for `FND_HIDE_DB_PASSWORD='N'`.
10. Re-run detection and confirm zero open high-severity violations.

## Acceptance criteria
- The detection query finds violations; the responsibility-level query finds none.
- Remediation removes only the conflicting responsibility, not the whole role.
- A conflicting assignment is blocked with a message naming both duties.
- Exceptions cannot be created without an expiry date.
- The password scan finds and reports the misconfigured profile level.
- Re-running detection returns zero open high-severity violations.

## Stretch
- Add a certification workflow and produce an outstanding-items report.
- Demonstrate the over-remediation failure mode and explain why it is worse.