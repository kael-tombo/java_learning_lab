# EXERCISES — APEX Administration

## 1. Provision a tenant (beginner)
Create workspace `ACME_DEV` + parsing schema + one developer + quota
500 MB. Log in as the developer; confirm workspace-admin screens are
invisible. *Reflection: which role boundary did you just test?*

## 2. Posture audit (beginner)
Read all instance password/session/HTTPS/outbound parameters. Score
against the §2 checklist. Harden every FAIL in a dev instance and
re-run the audit to all-PASS.

## 3. Slow-page hunt (intermediate)
Using the activity log, find the top-3 slowest page renders of the last
7 days. `APEX_DEBUG`-trace the worst one, identify the slow region
(report query vs process), and propose the fix (index vs pagination vs
caching). Verify with a second timed run.

## 4. Allow-list block (intermediate)
Remove a test host from the outbound allow-list (both ORDS + DB ACL).
Run the lab-05 payment-gateway call pattern against it; capture the exact
error at each layer. Restore, confirm success, and document which layer
blocked first and how you knew.

## 5. Backup/restore + patch rehearsal (advanced)
Full cycle on a scratch workspace: DB backup → app + workspace exports →
record parameter snapshot → apply a settings change (the "patch") →
verify app behavior matrix (login, REST call, report) → roll back via
imports + snapshot → re-verify. Time each phase; write the go/no-go gates
for a production window.
