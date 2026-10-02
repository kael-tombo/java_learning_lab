# QUIZ — Upgrade & Migration

## 1. What makes a custom table ADOP-safe, in three steps?
<details><summary>Answer</summary>Rename to `_tb`, create same-named EDITIONING VIEW, add INSTEAD OF trigger replaying DML. Un-editioned objects break online patching.</details>

## 2. The readiness query hunts what, and what is the gate?
<details><summary>Answer</summary>`XX%` objects with `edition_name IS NULL` — every row is a patch-cycle breaker. Gate: zero rows, in dev, before prod.</details>

## 3. Why is an unscoped `UPDATE _tb` in the trigger catastrophic?
<details><summary>Answer</summary>One row's update rewrites the whole table. WHERE must scope to the row's PK — fill in the walkthrough's placeholders per table.</details>

## 4. `FND_FILE.PUT_LINE` → what, and why does ADOP care?
<details><summary>Answer</summary>`FND_LOG.STRING(LEVEL_STATEMENT, module, msg)`. Deprecated calls inside online patches abort the ADOP cycle — the 14 h estimate assumes cleanup done.</details>

## 5. DMS cutover: why is the outage <2 h for a 5 TB move?
<details><summary>Answer</summary>Bulk + catch-up replication run online for hours; the outage covers only stop-replication → promote RDS → flip endpoints.</details>

## 6. Why point apps at ELB DNS, not instance IPs?
<details><summary>Answer</summary>ASG churn replaces instances constantly — ELB DNS absorbs it; IPs would rot on every scale event.</details>

## 7. `fnd_profile.save` without `COMMIT`?
<details><summary>Answer</summary>Session-scoped illusion — reverts on disconnect. Same gotcha as the sysadmin lab's `FND_HIDE_DB_PASSWORD` fix.</details>

## 8. 11g→19c: which deprecated features must die first?
<details><summary>Answer</summary>Advanced replication, streams, LONG-in-PL/SQL (→CLOB), old text/rewrite paths — audit via `dba_feature_usage_statistics` + `preupgrd.sql`.</details>

## 9. Post-upgrade stats order, and why?
<details><summary>Answer</summary>Fixed-object stats, then dictionary `GATHER STALE`. Without them the 19c optimizer guesses — plan regressions blamed on "the upgrade".</details>

## 10. Why three dress rehearsals, not one?
<details><summary>Answer</summary>First finds the unknowns, second validates the fixes, third proves the 8-hour/4-day budget under clock. One rehearsal only finds problems.</details>
