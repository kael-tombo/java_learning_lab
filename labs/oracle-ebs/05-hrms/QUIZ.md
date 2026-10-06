# Lab 05: HRMS Data Migration — Quiz

**1.** What is the single most important structural decision in a migration?

A. Choosing the fastest load method
B. Where invalid data is allowed to fail — staging, not the target
C. The number of parallel workers
D. The target release

<details><summary>Answer</summary><b>B</b> — Failing in staging is cheap, repeatable, and visible. Failing in the target is partial loads and opaque API failures.</details>

---

**2.** Why validate by domain rather than per record?

A. It is faster
B. HRMS rules are domain-specific, and grouping tells each owning team what to fix
C. Records are too many
D. Oracle requires it

<details><summary>Answer</summary><b>B</b> — A flat check cannot express the model, and the report becomes unactionable.</details>

---

**3.** What makes an error message actionable?

A. It says "invalid record"
B. Row number, offending value, rule violated, expected format, machine code
C. It is written in plain English
D. It includes a stack trace

<details><summary>Answer</summary><b>B</b> — Specificity turns a multi-day investigation into a minutes-long fix.</details>

---

**4.** Why must supervisors load after assignments?

A. HRMS rejects the order
B. `manager_id` references assignments; loading earlier leaves NULL everywhere
   with a silent failure
C. Supervisors are bigger tables
D. It is faster

<details><summary>Answer</summary><b>B</b> — The failure is silent (zero rows updated), which is why a pre-flight assertion is needed.</details>

---

**5.** `03/04/2026` in a file with no stated convention. Correct action?

A. Interpret as MM/DD (US default)
B. Interpret as DD/MM (EU default)
C. Reject as ambiguous and request the source convention
D. Store as text

<details><summary>Answer</summary><b>C</b> — A guessed date 40 days wrong surfaces at payroll. Rejecting is cheaper than being wrong.</details>

---

**6.** Why validate the national ID checksum, not just its format?

A. Checksums are required by Oracle
B. Shape-valid but checksum-invalid IDs indicate transcription errors and block tax filing
C. Checksums are faster
D. Format alone is enough

<details><summary>Answer</summary><b>B</b> — In the lab, ~5% of Singapore records pass shape but fail checksum. Those would have blocked payroll tax.</details>

---

**7.** What to do with an orphaned `manager_id`?

A. Set NULL
B. Drop the assignment
C. Create a clearly marked placeholder person to preserve hierarchy
D. Fail the whole migration

<details><summary>Answer</summary><b>C</b> — Placeholders keep every employee loadable and the org chart intact, and make the gap a tracked exception.</details>

---

**8.** Why mark placeholders explicitly?

A. Style
B. Unmarked placeholders become silent data defects in headcount and approval routing
C. Oracle requires it
D. To speed up queries

<details><summary>Answer</summary><b>B</b> — Marking turns a ghost record into a visible, owned exception.</details>

---

**9.** Is 99% first-pass acceptance a good migration result?

A. Yes, if the remaining 1% is documented
B. No — first-pass rate is a vanity metric; the tail is the schedule risk
C. Yes, 99% is above the 95% target
D. It depends on the industry

<details><summary>Answer</summary><b>B</b> — By pass 2 you can be at 88% and still face 2,400 records. Effort per record rises sharply in the tail.</details>

---

**10.** Why load through `hr_people_api` rather than direct DML?

A. Direct DML is slower
B. APIs validate, propagate cross-entity changes, log, and survive patches
C. APIs are required for licensing
D. Direct DML does not work

<details><summary>Answer</summary><b>B</b> — ~9 hours of API time buys correctness that direct DML cannot, at the price of permanent data corruption.</details>

---

## Scoring
- **9–10**: Ready to run a fixed-go-live enterprise migration.
- **7–8**: Solid; revisit dependency ordering and date ambiguity.
- **5–6**: Re-read THEORY on staging and convergence.
- **<5**: Work through EXERCISES 3, 4, and 6 again.