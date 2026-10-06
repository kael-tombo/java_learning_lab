# Lab 06: APEX Migration — Quiz

**1.** Why must migration size be estimated from the Forms source rather than screen count?

A. Screens are hard to count
B. The application is 340 triggers, not 23 screens — screen-count estimation
   underestimates by 4.6×
C. Developers prefer source queries
D. The Forms source is more accurate

<details><summary>Answer</summary><b>B</b> — Triggers are the work; canvases are only the navigation.</details>

---

**2.** What percentage of trigger effort should be deletion?

A. 10%
B. ~43% — 165 of 380 trigger objects are POST-QUERY or KEY-QUERY
C. 90%
D. 0%

<details><summary>Answer</summary><b>B</b> — This reframes the project from "convert 340" to "delete 165, convert 213".</details>

---

**3.** What happens to most POST-QUERY triggers?

A. Converted to processes
B. Deleted — the region query with a join already does their work
C. Converted to Dynamic Actions
D. Rewritten in JavaScript

<details><summary>Answer</summary><b>B</b> — 50 records × 1 query becomes 1 query with joins. Often the largest performance win in a Forms migration.</details>

---

**4.** Why is client-tier business logic relocation the structural change?

A. APEX is faster
B. In Forms the logic lives on each user's workstation and can diverge; in APEX
   there is one implementation for everyone
C. APEX requires it
D. It reduces code

<details><summary>Answer</summary><b>B</b> — The benefit is correctness, not modernisation.</details>

---

**5.** What is a KEY-QUERY equivalent in APEX?

A. A before-header process
B. None — the region query is the query. Converting it would run it twice
C. A Dynamic Action
D. A validation

<details><summary>Answer</summary><b>B</b> — KEY-QUERY existed to populate a client-side record group that no longer exists.</details>

---

**6.** How should a PRE-INSERT validation be migrated?

A. As an APEX page validation only
B. As a database constraint (enforcement) plus an APEX validation (message) plus
   an item LOV or default (usability)
C. As a trigger on the table
D. As client-side JavaScript

<details><summary>Answer</summary><b>B</b> — All three homes. An APEX-only validation is bypassed by any direct insert.</details>

---

**7.** What must happen to level-3 constraint coverage during migration?

A. It should increase
B. It must stay identical — dropping it while adding APEX validations makes the
   system look safer while enforcing less
C. It can be replaced by validations
D. It is not relevant

<details><summary>Answer</summary><b>B</b> — What improves is levels 1 and 2. If level 3 drops, the migration made things worse.</details>

---

**8.** Why is a Forms savepoint not replicable in APEX?

A. It is complex
B. A stateless request model commits at request end; attempts produce a worse
   design for ~2 user-hours a week
C. APEX forbids it
D. It cannot be taught

<details><summary>Answer</summary><b>B</b> — Accept the loss and brief users. 20 days of design to save 2 hours a week is not a trade.</details>

---

**9.** Which Forms objects are hardest to migrate, and why?

A. POST-QUERY — they are complex
B. Return-value LOVs (7 of 48) — 65% of LOV effort in 17% of the objects,
   because Forms assigns return values automatically and APEX does not
C. Alerts — they need JavaScript
D. Menus — they are structural

<details><summary>Answer</summary><b>B</b> — This is where the migration actually gets stuck.</details>

---

**10.** What should the parallel-run cutover gate be?

A. Zero total discrepancies
B. Zero stop-the-line cases and zero "wrong data written" — a zero-discrepancy
   gate never ends because rounding differences are not bugs
C. Fewer than 10 discrepancies
D. The Forms team sign-off

<details><summary>Answer</summary><b>B</b> — Cosmetic and timing differences are expected; logic errors are not.</details>

---

## Scoring
- **9–10**: Ready to run a Forms-to-APEX migration.
- **7–8**: Solid; revisit classification and validation migration.
- **5–6**: Re-read THEORY on inventory, deletion, and staging.
- **<5**: Work through EXERCISES 1, 3, and 6 again.