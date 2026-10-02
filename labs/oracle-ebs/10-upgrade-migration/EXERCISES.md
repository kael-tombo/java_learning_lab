# EXERCISES — Upgrade & Migration

## 1. Readiness gate (beginner)
Create 3 custom tables + 1 package in an `XX%` schema (one table already
editioned). Run the readiness query. Confirm exactly the 3 un-editioned
objects list. *Reflection: why must the gate be zero rows, not "mostly"?*

## 2. Edition a table safely (beginner)
Rename → editioning view → INSTEAD OF trigger with PK-scoped
UPDATE/DELETE (fill in the walkthrough's `…` placeholders). Prove
INSERT/UPDATE/DELETE through the view land correctly in `_tb`, then
demonstrate the failure mode of an unscoped `UPDATE _tb` (on test data!).

## 3. Deprecated-API sweep (intermediate)
Seed a schema with 10 procedures using `FND_FILE.PUT_LINE`,
`FND_GLOBAL.APPS_INIT`, and `LONG` declarations. Grep + compile in a 12.2
(or 19c-rules) sandbox, replace all three patterns, and show zero
remaining hits. Time the sweep — extrapolate to 500 customizations.

## 4. ELB flip drill (intermediate)
Snapshot the four agent-host profiles, flip both hosts to a test ELB DNS
via `fnd_profile.save` + `COMMIT`, verify via re-select, then roll back.
Document what breaks if the `COMMIT` is forgotten (session-scoped illusion
of success).

## 5. Standby-first cutover plan (advanced)
Write the 8-hour runbook for 11g→19c + app patching: preupgrd fixes,
deprecated-feature removals, AutoUpgrade with fallback, standby upgrade +
switchover, stats gathering, plan-baseline review, flashback fallback
trigger criteria. Include go/no-go gates per phase and the rehearsal-×3
schedule.
