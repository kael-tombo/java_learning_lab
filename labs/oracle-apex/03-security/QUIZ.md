# QUIZ — APEX Security

## 1. LDAP-then-local: why try LDAP inside its own exception block?
<details><summary>Answer</summary>Directory outages must degrade to local fallback, not propagate. Any LDAP exception → FALSE → local path decides.</details>

## 2. Why check lockout *before* verifying the password?
<details><summary>Answer</summary>Locked accounts skip expensive hashing (DoS resistance) and leak no timing signal distinguishing locked from wrong-password.</details>

## 3. `NO_DATA_FOUND` → logged FALSE. Why not raise?
<details><summary>Answer</summary>Unknown users must be indistinguishable from bad passwords (no user-enumeration oracle), and the attempt still audits.</details>

## 4. Salt's exact job?
<details><summary>Answer</summary>Identical passwords hash differently → rainbow tables useless. (Iteration count is what slows brute force — different mechanism.)</details>

## 5. Permissions granted per role, not computed by tree-walk. Why?
<details><summary>Answer</summary>Explicit rows are auditable and immediate; tree-walking at request time is slower and harder to certify for SOX.</details>

## 6. `INSTR(','||list||',', ',X,')` — why the comma armor?
<details><summary>Answer</summary>Prevents substring false positives (`EDIT` matching `RE_EDIT_X`). Delimiters on both sides make matching exact.</details>

## 7. VPD returns `'1=0'` for whom, and what does it do?
<details><summary>Answer</summary>Users with no branch and non-ADMIN: predicate false for every row — total invisibility, enforced in the database.</details>

## 8. `update_check => TRUE`: what hole does it close?
<details><summary>Answer</summary>Writes that would move rows outside the read policy (e.g. changing branch_id) — without it, VPD is read-only decoration.</details>

## 9. UI hiding without server-side schemes: verdict?
<details><summary>Answer</summary>Decoration, not security — direct URLs/AJAX bypass it. Every hidden component needs the same scheme server-side (pitfall #2/#5).</details>

## 10. Audit table partitioned daily + indexed: why?
<details><summary>Answer</summary>Security events are append-only and unbounded — partitioning keeps inserts fast and age-out cheap; indexes serve the two hot queries (by user, by date).</details>
