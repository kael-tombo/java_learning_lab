# QUIZ — System Administration

## 1. Why does the provisioning loop catch exceptions per row instead of once outside?
<details><summary>Answer</summary>One bad row (duplicate username, bad email) must not abort 499 good creates. Per-row isolation + error table = partial success with full audit.</details>

## 2. What does `processed_flag='N'` buy you?
<details><summary>Answer</summary>Idempotent restarts — re-running the program processes only leftovers, never duplicating the 499 already created.</details>

## 3. `GL_POST` dies with ORA-00001 on GL_JE_LINES_U1. What does that constraint key on, and what does the violation prove?
<details><summary>Answer</summary>`(JE_HEADER_ID, JE_LINE_NUM)`. Some feeder generated the same line number twice under one header — an application uniqueness bug, not a database bug.</details>

## 4. Why scope the duplicate query to `status='U'` + one period?
<details><summary>Answer</summary>Posted journals are immutable history; scanning them wastes I/O and risks touching closed periods. Scope to what the failing program actually wrote.</details>

## 5. Why update by `ROWID` in the fix?
<details><summary>Answer</summary>ROWID is the fastest single-row address — no secondary index lookup per row in a potentially large correction set.</details>

## 6. Permanent fix for duplicate line numbers?
<details><summary>Answer</summary>Generate numbers from `GL_JOURNAL_LINES_S.NEXTVAL` in the feeder. Sequences are concurrency-safe; `MAX()+1` races under parallel sessions.</details>

## 7. Profile resolution order, most-specific wins?
<details><summary>Answer</summary>User > Responsibility > Application > Site. A user-level value silently overrides site security — the mechanism behind the 15-user SOD drift.</details>

## 8. Why is `FND_HIDE_DB_PASSWORD=N` at SITE critical?
<details><summary>Answer</summary>Every debug log on every tier prints DB credentials in cleartext — a credential-sprawl incident, not a cosmetic flag.</details>

## 9. `fnd_profile.save(...)` without `COMMIT` — effect?
<details><summary>Answer</summary>None persists — the change evaporates at session end. The fix must commit; test it once in a sandbox.</details>

## 10. One commit at end vs batch commits: trade-off?
<details><summary>Answer</summary>Single commit = atomic all-or-logged-nothing (crash loses everything). Batch commits bound crash loss but leave partial state — choose by re-runnability of the job (this one is re-runnable, so batching is safe).</details>
