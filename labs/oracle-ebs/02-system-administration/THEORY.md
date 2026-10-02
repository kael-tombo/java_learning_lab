# THEORY — EBS System Administration

## 1. The FND security model in one picture

Every EBS login resolves through four layers: **User → Responsibility →
Menu/Functions → Data/Security groups**. A responsibility is a job-role
bundle (functions + menus); data groups scope *which rows* a responsibility
sees per country/legal entity. The walkthrough's 500-user problem exists
because Form `FNDSCAUS` does this one row at a time (~15 min/user) with no
bulk path — hence `FND_USER_PKG.createuser` in a cursor loop.

## 2. Why per-row exception isolation

The provisioning loop wraps each user in its own `BEGIN…EXCEPTION…END`
and logs to `xx_client_import_errors` instead of rolling back. One bad
email or duplicate username must not abort 499 good creates. The final
`COMMIT` is outside the loop — partial success is the *requirement*, and
`processed_flag='Y'` + `user_id` on the staging table makes the job
re-runnable (idempotency via state, the same principle as the GL feeder
fix in §4).

## 3. Concurrent programs: requests, logs, and ORA-00001

A concurrent program is a registered executable + parameters, run by the
concurrent manager; every request writes a log + output file. `GL_POST`
fails with `ORA-00001` on `GL_JE_LINES_U1 (JE_HEADER_ID, JE_LINE_NUM)` —
a uniqueness violation means the feeder generated the same
`(header, line)` pair twice. Diagnosis order is fixed: log file first
(exact error + parameters), then the duplicate-detection `GROUP BY`
query scoped to the failing period, then the feeder code. The quick fix
re-sequences with `ROW_NUMBER() OVER (PARTITION BY je_header_id ORDER BY
je_line_num, last_update_date)`; the permanent fix uses the sequence
`GL_JOURNAL_LINES_S.NEXTVAL` at generation time so duplicates are
structurally impossible.

## 4. Profile option inheritance and the credential leak

Profile options resolve most-specific-wins:
SITE < Application < Responsibility < User. A user-level value silently
overrides site security — which is how 15 AP users accumulated conflicting
responsibilities. `FND_HIDE_DB_PASSWORD=N` at SITE is worse: every debug
log on every tier prints DB credentials. The audit query on
`FND_PROFILE_OPTION_VALUES_HISTORY` (90-day window) plus the `LISTAGG`
SOD-conflict query turns "trust me" into evidence; `fnd_profile.save(...,
'SITE')` + `COMMIT` is the remediation, and the drift-report program makes
it stick.
