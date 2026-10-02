# CODE_DEEP_DIVE — System Administration walkthrough code

All references are to `PROBLEM_WALKTHROUGH.md` in this lab.

## 1. `bulk_create_users` (Problem 1, lines 22–71)

- **Staging-driven cursor** (`xx_client_import_users WHERE processed_flag='N'`):
  the spreadsheet maps 1:1 to `FND_USER` columns; unprocessed-only filter
  gives free restartability.
- **`fnd_user_pkg.createuser`** returns `l_user_id`; note the plaintext
  `TemporaryPass123!` + 90-day lifespan — a cutover credential, not a
  permanent secret (rotation is the trainee's follow-up exercise).
- **`fnd_user_resp_groups_api.insert_assignment`** binds responsibility
  with `effective_date=SYSDATE, expiration=NULL` (open-ended). Country
  variance from the scenario (data groups per privacy law) is handled by
  the `data_group` column feeding assignment APIs — not shown inline, but
  the staging table carries it.
- **Per-iteration `EXCEPTION WHEN OTHERS`**: captures `SQLERRM` into
  `xx_client_import_errors(request_id, employee_number, …)`. Loop
  continues; single `COMMIT` at end. Trade-off to know: one commit means a
  crash loses all progress — batch commits every N rows bound the loss
  window (exercise 4).

## 2. Duplicate-line diagnosis + fix (Problem 2, lines 99–134)

- **Detection**: `GROUP BY je_header_id, je_line_num HAVING COUNT(*)>1`,
  scoped to unposted (`status='U'`) headers of `DEC-24`. Scoping matters:
  unscoped, this scans the whole lines table.
- **Fix**: `ROW_NUMBER() OVER (PARTITION BY je_header_id ORDER BY
  je_line_num, last_update_date)` assigns fresh unique numbers, applied by
  `ROWID` (fastest single-row address). `ORDER BY` keeps the fix stable
  across runs. `COMMIT` once after the loop.
- **Permanent fix** (prose, not code): feeder must call
  `GL_JOURNAL_LINES_S.NEXTVAL` — sequences guarantee uniqueness where
  application-side counters cannot under concurrency.

## 3. Profile/SOD audit (Problem 3, lines 161–195)

- **History query**: 90-day window on `fnd_profile_option_values_history`
  ordered newest-first — the auditor's first screen.
- **SOD query**: filters `fnd_user_resp_groups` to the two conflicting
  responsibilities, `LISTAGG`s them per user, `HAVING COUNT(DISTINCT…)>1`
  keeps only violators. (Note the walkthrough groups by both user *and*
  responsibility — collapsing to user-only is a suggested exercise.)
- **`fnd_profile.save('FND_HIDE_DB_PASSWORD','Y','SITE')` + `COMMIT`**:
  without the commit the fix evaporates on session end — a classic
  gotcha worth testing once in a sandbox and never forgetting.
