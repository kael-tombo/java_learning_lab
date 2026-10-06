# Lab 02: System Administration — Mini Project

## Goal
Provision 500 users, fix a failing nightly job, and clear an SOD finding in
90 minutes.

## Requirements
- R1: A CSV of 500 warehouse users with username, full name, email, and role.
- R2: A staging table and a load procedure using `FND_USER_PKG`.
- R3: Post-load validation — duplicate check, profile assignment check, count
      reconciliation between rows loaded and users created.
- R4: A diagnostic query set for `ORA-00001` in `GL_POST`, including the
      request-id lookup into `FND_CONCURRENT_REQUESTS`.
- R5: A dedupe/fix procedure that is safe to run more than once.
- R6: An SOD conflict query listing users with mutually exclusive responsibilities.
- R7: A remediation script that revokes the conflicting responsibility and
      records who approved it.
- R8: A check that surfaces any profile with `FND_HIDE_DB_PASSWORD='N'`.

## Steps
1. Create the staging table and load the CSV, validating rows before load.
2. Call `FND_USER_PKG.Create_User` per row inside a controlled loop.
3. Reconcile: rows in file vs users created vs duplicates skipped.
4. Reproduce the `ORA-00001` and read the concurrent request log.
5. Identify the duplicate journal line and write the fix.
6. Re-run the job and confirm it completes successfully.
7. Run the SOD conflict query and rank the violations by risk.
8. Revoke one responsibility per violation, recording approval metadata.
9. Scan profile options for the password-visibility misconfiguration.

## Acceptance criteria
- The 500-user count reconciles exactly, with duplicates explained.
- `GL_POST` completes on a re-run after the dedupe fix.
- Every SOD violation has either been remediated or has a documented exception.
- No profile remains with the password exposed.

## Stretch
- Wrap the whole flow in a concurrent program with a proper error log.
- Add a re-validation job that reports drift weekly without changing anything.