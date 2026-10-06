# Lab 06: Customization (OAF) — Quiz

**1.** What is the correct dependency direction in OAF?

A. VO depends on Controller
B. Upper layers (View, Controller) depend on lower (AM, VO), never the reverse
C. All layers are independent
D. AM depends on Controller

<details><summary>Answer</summary><b>B</b> — A VO calling controller logic is a design error that surfaces as class-loading or transaction bugs.</details>

---

**2.** Why is extension strongly preferred over customisation?

A. Extensions are faster to build
B. Extensions survive upgrades; customisations require a manual merge at every patch
C. Extensions need less code
D. Customisations are unsupported

<details><summary>Answer</summary><b>B</b> — Extension: 44 hrs over 5 years. Customisation: 90 hrs. Customisation is faster to build and slower to own.</details>

---

**3.** Why are literals forbidden in VO SQL?

A. Oracle rejects them
B. Each literal is a distinct statement causing a hard parse per request and
   library cache latch contention
C. They cannot use indexes
D. Bind variables are faster to write

<details><summary>Answer</summary><b>B</b> — 50,000 annual hard parses in the lab scenario, with the latch contention being the real risk.</details>

---

**4**: What does VO layering buy you, besides organisation?

A. Fewer classes
B. Query count reduction — ~10× in the lab (41 queries → 4)
C. Automatic indexing
D. Better security

<details><summary>Answer</summary><b>B</b> — Layering saved ~740 ms of a 3,000 ms budget. It is a performance technique.</details>

---

**5.** Where does transaction control belong?

A. The controller
B. The View Object
C. The Application Module
D. The page

<details><summary>Answer</summary><b>C</b> — The AM is the transaction boundary. VOs and controllers must not commit.</details>

---

**6.** Why must approval complete the workflow activity rather than set `APPROVAL_STATUS`?

A. The workflow table is faster
B. A status update orphans the workflow item — the document looks approved while
   the workflow still waits for a human
C. Oracle forbids it
D. It is required for reporting

<details><summary>Answer</summary><b>B</b> — The next approver never sees it. The document and the workflow disagree permanently.</details>

---

**7.** Why structured reject reason codes instead of free text?

A. Free text is too long
B. Structured codes make rejection data analysable — 63% concentration identifies
   the highest-value process fix
C. Structured codes are faster
D. Free text cannot be indexed

<details><summary>Answer</summary><b>B</b> — Free text yields no extractable theme and therefore no action.</details>

---

**8.** Why must the audit log share the approval's transaction?

A. It is faster
B. A log that survives a rolled-back approval makes the audit trail actively misleading
C. It reduces storage
D. It is required by SOX

<details><summary>Answer</summary><b>B</b> — Worse than no log. Log through the AM so both commit or roll back together.</details>

---

**9.** What does per-function security prevent that page-level security cannot?

A. Slow pages
B. A read-only user approving — 80% over-provisioning in the lab
C. SQL injection
D. Slow queries

<details><summary>Answer</summary><b>B</b> — Granting the page grants everything on it. Function-level grants plus a controller check reduce it to zero.</details>

---

**10.** Why re-check the workflow item state inside the transaction before completing?

A. It is faster
B. Two approvers loading the same invoice both see pending; without a re-check one
   silently overwrites the other (~4,000 conflicts/year in the lab)
C. It reduces locking
D. The workflow API requires it

<details><summary>Answer</summary><b>B</b> — Concurrent approval is a routine event, not an edge case. The re-check turns silent data loss into a clean message.</details>

---

## Scoring
- **9–10**: Ready to build production OAF customizations.
- **7–8**: Solid; revisit layering and workflow integration.
- **5–6**: Re-read THEORY on extension economics and failure paths.
- **<5**: Work through EXERCISES 4, 6, and 9 again.