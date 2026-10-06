# Lab 04: Employee Lifecycle Management (HRMS) — Quiz

**1.** Why does each lifecycle event take 3–5 days to process manually?

A. The database is slow
B. There are no declared transitions or automated side effects
C. Employees are unavailable
D. Payroll runs monthly

<details><summary>Answer</summary><b>B</b> — The delay comes from performing state transitions by hand because they were never automated.</details>

---

**2.** What does `effective_end_date = DATE '9999-12-31'` signify?

A. The record is deleted
B. The record is the current, open assignment
C. The record is future-dated
D. The person is terminated

<details><summary>Answer</summary><b>B</b> — 9999-12-31 marks the open/current row in an effective-dated history.</details>

---

**3.** Why is `COUNT(*)` on `PER_ALL_ASSIGNMENTS_F` wrong for headcount?

A. It is slow
B. Each person has multiple effective-dated rows, inflating the count
C. It ignores terminated employees
D. It requires a hint

<details><summary>Answer</summary><b>B</b> — Use `COUNT(DISTINCT person_id)` with a date filter. Overstatement can exceed 100%.</details>

---

**4.** When transferring an employee, what must you do to the current assignment?

A. `UPDATE` the position
B. `DELETE` and re-insert
C. Close it with `effective_end_date` and open a new row
D. Nothing — it updates automatically

<details><summary>Answer</summary><b>C</b> — Never update or delete; `hr_assignment_api` closes the old row and opens the new one.</details>

---

**5.** What makes a trigger cascade safe to retry?

A. Running it inside a single large transaction
B. Idempotency via `MERGE` and a unique constraint on the side-effect key
C. Disabling other triggers
D. Increasing the timeout

<details><summary>Answer</summary><b>B</b> — Re-running must not duplicate downstream work.</details>

---

**6.** Why should country notice periods live in legislative configuration?

A. It is faster to query
B. It keeps compliance rules out of custom code and auditable in configuration
C. Oracle requires it
D. It reduces database size

<details><summary>Answer</summary><b>B</b> — Hardcoded country rules in code become an audit and maintenance liability.</details>

---

**7.** What is the most commonly skipped step in an ADP integration?

A. Sending hire records
B. Reconciling what was sent against what came back
C. Building the payload
D. Authenticating

<details><summary>Answer</summary><b>B</b> — Without reconciliation, payroll errors surface when an employee complains.</details>

---

**8.** At what offset should SSO revocation be scheduled after termination?

A. D+7
B. D+1
C. D+0 (same business day)
D. After payroll closes

<details><summary>Answer</summary><b>C</b> — Every day of lag is live exposure from former-employee accounts.</details>

---

**9.** What must the lifecycle audit trail permit?

A. `UPDATE` to correct mistakes
B. `DELETE` when retention expires
C. `INSERT` only
D. Nothing in restricted mode

<details><summary>Answer</summary><b>C</b> — Append-only with a retention period enforced by policy, not by ad-hoc deletion.</details>

---

**10.** A project reports "hold time down 80%" but never mentions error rate. What is the problem?

A. The metric is wrong
B. It may have traded speed for accuracy — both must be reported
C. It is too detailed
D. Error rate is not relevant to HR

<details><summary>Answer</summary><b>B</b> — Automation that speeds up wrong work increases the error volume, not reduces it.</details>

---

## Scoring
- **9–10**: Ready for a global HR lifecycle programme.
- **7–8**: Solid; revisit effective dating and idempotency.
- **5–6**: Re-read THEORY on triggers and legislative compliance.
- **<5**: Work through EXERCISES 2, 3, and 4 again.