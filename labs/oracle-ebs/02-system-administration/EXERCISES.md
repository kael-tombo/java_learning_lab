# EXERCISES — System Administration

## 1. Dry-run the bulk loader (beginner)
Create `xx_client_import_users` with 5 rows (one duplicate username, one
bad email). Run a copy of `bulk_create_users` against a sandbox. Verify:
4 users created, 1 error row, `processed_flag` set only on successes.
*Reflection: why must the error insert be inside the loop's exception
handler, not after it?*

## 2. Batch-commit window (beginner)
Modify the procedure to `COMMIT` every 100 rows. Kill the session
mid-run (or simulate with `RAISE` at row 150). Compare lost work vs the
single-commit version. When is each appropriate?

## 3. Duplicate hunt (intermediate)
Seed `gl_je_lines` test data with 3 duplicate `(header, line)` pairs in a
`DEC-24`-like period. Run the detection query — confirm exactly 3 groups.
Apply the `ROW_NUMBER()` fix, re-run detection (expect 0), and prove
re-runnability (second run changes nothing).

## 4. Sequence-hardened feeder (intermediate)
Write a feeder insert that computes `MAX(je_line_num)+1` (racy) vs one
using `GL_JOURNAL_LINES_S.NEXTVAL`. Simulate 10 concurrent sessions each
inserting 100 lines; count duplicates per approach. Explain why the
sequence version cannot duplicate.

## 5. SOD collapse + drift monitor (advanced)
(a) Rewrite the SOD query grouped by user only (one row per violator with
the full conflicting set). (b) Build the drift-report program: nightly
job comparing current `FND_PROFILE_OPTION_VALUES` against a baseline
table, alerting on any `FND_HIDE_*` or money-movement profile change.
Include the `fnd_profile.save` remediation path and a test proving the
`COMMIT` requirement.
