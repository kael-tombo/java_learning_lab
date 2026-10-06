# Lab 07: APEX Advanced Components — Quiz

**1.** What single question decides IG vs IR?

A. How many rows
B. Does the user edit the data
C. How many columns
D. Report or form

<details><summary>Answer</summary><b>B</b> — Everything else is secondary. IG for editing, IR for read-only analysis.</details>

---

**2.** Why does an editable IG require a primary key?

A. For display ordering
B. Editing means the database must know which row to update; without a key APEX
   cannot address rows
C. For export
D. For aggregation

<details><summary>Answer</summary><b>B</b> — And a synthetic key is a warning sign that the data model is missing an identity.</details>

---

**3.** When does an IG actually write to the database?

A. On each cell edit
B. On one AJAX call when the user presses Save
C. On page navigation
D. On a timer

<details><summary>Answer</summary><b>B</b> — Which inverts user expectation. The UI and training must make "pending until Save" explicit.</details>

---

**4.** Why prefer cell validation over row validation where possible?

A. It is faster
B. It fires during editing while the user still has the context; row validation
   fires on Save after 30 more cells have been entered
C. It is required by APEX
D. Row validation does not work

<details><summary>Answer</summary><b>B</b> — Resolution time ~3 s versus ~40 s. It is a usability decision as much as a technical one.</details>

---

**5.** Why can a row validation not be moved to cell level?

A. It would be slower
B. It involves multiple rows or aggregate state, and a cell validation sees one cell
C. APEX limits cell validations
D. It would duplicate messages

<details><summary>Answer</summary><b>B</b> — A total discount across an order is not a property of any single cell.</details>

---

**6.** Why recalculate a computed column rather than store it?

A. Storing is slower
B. A stored value can disagree with its inputs when an input changes, creating a
   data integrity problem that needs a reconciliation job to fix
C. APEX cannot store computed values
D. It uses more space

<details><summary>Answer</summary><b>B</b> — Recalculation makes the discrepancy rate zero by construction.</details>

---

**7.** Why guard the row count on save?

A. To improve performance only
B. A user who has changed 5,000 cells has almost certainly erred, and saving
   would apply all of it
C. APEX limits it automatically
D. To reduce payload size only

<details><summary>Answer</summary><b>B</b> — Refusing in one second beats a 2.5 MB request timing out after applying 4,000 edits.</details>

---

**8:** When should aggregation live on the IG versus a separate chart region?

A. Always on the IG
B. Aggregation for exploration belongs on the IG (no round trip); a fixed chart
   for communication belongs in its own region so it can be linked from elsewhere
C. Always separate
D. It does not matter

<details><summary>Answer</summary><b>B</b> — Control breaks let the user change grouping interactively, which a static chart cannot.</details>

---

**9.** Why provide a reset action for per-user grid state?

A. It is required
B. A user whose columns are invisible cannot recover alone, so the alternative is
   a support ticket
C. State grows too large
D. It speeds up rendering

<details><summary>Answer</summary><b>B</b> — The reset matters more than tidying. State growth (~4 MB/year) is not the crisis.</details>

---

**10.** When does a plugin beat a shared component?

A. Always
B. When the same behaviour appears on three or more pages — ~2 days for a plugin
   versus ~1 day for shared components, break-even at ~6 APEX upgrades
C. Never
D. Only for region plugins

<details><summary>Answer</summary><b>B</b> — And never copy framework files: that breaks at the next upgrade and leaves you maintaining Oracle's code.</details>

---

## Scoring
- **9–10**: Ready to build advanced APEX applications.
- **7–8**: Solid; revisit validation placement and the save contract.
- **5–6**: Re-read THEORY on IG editing model and validation.
- **<5**: Work through EXERCISES 2, 4, and 5 again.