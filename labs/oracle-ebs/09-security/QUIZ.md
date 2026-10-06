# Lab 09: Security (SOD Remediation) — Quiz

**1.** Why can SOD not be fixed by removing individual permissions?

A. Permissions cannot be removed
B. Each step is legitimately permitted; the control is the separation between
   steps, not the absence of any step
C. Oracle prevents it
D. It is too slow

<details><summary>Answer</summary><b>B</b> — The fraud chain works because every individual action is allowed. Only the combination is the risk.</details>

---

**2.** What must exist before any SOD detection query can be written?

A. A list of users
B. An enumerated risk matrix mapping duties to conflicts
C. A list of responsibilities
D. A password policy

<details><summary>Answer</summary><b>B</b> — "SOD conflicts" is not enforceable until each conflict is specific and testable.</details>

---

**3.** Why does a responsibility-level query find nothing?

A. The data is missing
B. A violation is a property of a user's assignment set, not of any single
   responsibility — each one may be individually reasonable
C. Responsibilities cannot be joined
D. You need function security

<details><summary>Answer</summary><b>B</b> — The detection must self-join on `user_id` across responsibilities.</details>

---

**4.** What is the purpose of the `duty_a < duty_b` predicate?

A. Performance
B. Avoids reporting each conflict twice (A↔B and B↔A)
C. Filters to active duties
D. Orders results

<details><summary>Answer</summary><b>B</b> — Without it the violation count is doubled and the risk ranking is wrong.</details>

---

**5.** Why revoke only the conflicting responsibility?

A. It is faster
B. Revoking the whole role breaks the business and drives users to shared logins —
   a worse control than the original violation, since attribution is lost entirely
C. Oracle only allows one
D. It reduces the finding count more

<details><summary>Answer</summary><b>B</b> — Over-remediation is a real failure mode. In the lab, ~12 shared logins would result without alternate paths.</details>

---

**6:** Order remediation by what?

A. Alphabetical user name
B. User count, easiest first
C. Severity weighted by value at risk — 8 users carry ~65% of the exposure
D. Date hired

<details><summary>Answer</summary><b>C</b> — Tier 1 is 18% of the finding and ~65% of the value.</details>

---

**7.** Why are exceptions legitimate?

A. They let you avoid the work
B. Some conflicts are irreducible (a three-person finance team cannot separate
   duties) and a managed exception with compensating controls is stronger than an
   undocumented state
C. Auditors approve everything
D. They reduce query time

<details><summary>Answer</summary><b>B</b> — Exception counts rising from 0 to 7 is a positive outcome: previously invisible conflicts are now documented.</details>

---

**8.** What makes an exception valid?

A. A business reason
B. Compensating control, named owner, approval reference, and a non-indefinite expiry
C. A comment
D. A ticket number

<details><summary>Answer</summary><b>B</b> — "Indefinite" is not an exception; it is undocumented acceptance of risk. Enforce expiry with `NOT NULL` and an overdue report.</details>

---

**9:** Why is `FND_HIDE_DB_PASSWORD='N'` the highest priority finding?

A. It is easy to fix
B. It exposes the DB password, enabling direct schema access that bypasses
   function security, row-level security, and SOD entirely — making every other
   remediation irrelevant
C. It is a performance issue
D. It only affects diagnostics

<details><summary>Answer</summary><b>B</b> — A one-hour fix that defeats three weeks of SOD work if left open. Scan every profile level; a system-level `N` overrides a safe application-level `Y`.</details>

---

**10.** Why does certification need attestation?

A. Auditors require signatures
B. The report proves nothing without it — the value is the signed decision, and the
   evidence trail is what an auditor examines
C. Signatures are faster
D. It reduces certification cost

<details><summary>Answer</summary><b>B</b> — Who certified what, when, and with what decision. That is the audit artefact.</details>

---

## Scoring
- **9–10**: Ready to run a SOX SOD remediation engagement.
- **7–8**: Solid; revisit detection level and over-remediation.
- **5–6**: Re-read THEORY on the risk matrix and exceptions.
- **<5**: Work through EXERCISES 2, 4, and 8 again.