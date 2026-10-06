# Lab 04: Supply Chain (Cycle Counting) — Quiz

**1.** Why is an annual physical count not an adequate inventory control?

A. It is too expensive
B. It measures accuracy once a year, so losses accumulate unseen and the
causing transactions are too old to investigate
C. It is inaccurate
D. It requires a shutdown

<details><summary>Answer</summary><b>B</b> — The annual count is a detection failure: by the time you find $2M of loss, you cannot tell when or why it happened.</details>

---

**2.** What is the real value of cycle counting?

A. 100% inventory accuracy
B. Bounding how long an error can hide, so loss is detected small and recent
C. Reducing headcount
D. Eliminating auditors

<details><summary>Answer</summary><b>B</b> — Perfect accuracy is unattainable. Bounded loss window is the achievable and quantifiable benefit.</details>

---

**3.** Which metric should drive ABC classification?

A. Item unit count
B. Annual dollar usage
C. Physical volume
D. Purchase order date

<details><summary>Answer</summary><b>B</b> — Annual dollar usage reflects what actually drives cost and variance.</details>

---

**4.** What is the limitation of pure ABC classification?

A. It is too complex
B. It ignores movement — a mid-value, high-transaction item is under-protected
C. It requires a database upgrade
D. It only works for class A

<details><summary>Answer</summary><b>B</b> — Transaction count is a second dimension. High-movement low-value items often have the highest shrinkage rate.</details>

---

**5.** Formula for the maximum count interval from materiality?

**A**: `Materiality / (discrepancy rate × monthly value throughput)`
**B**: `Materiality × monthly value`
**C**: `Value / SKU count`
**D**: `12 / accuracy target`

<details><summary>Answer</summary><b>A</b> — Solve for the interval so expected unreconciled loss stays below materiality.</details>

---

**6.** Why should tolerance use both a percentage and a value cap?

A. To reduce database size
B. Because 5% of a $2M item is a management decision, not a floor-level approval
C. Oracle requires it
D. Percentages are unreliable

<details><summary>Answer</summary><b>B</b> — Percentage alone hides that a small percentage can be a large absolute amount.</details>

---

**7.** What is the main problem with a very wide tolerance?

A. It is slow to calculate
B. It misses real discrepancies inside the tolerance band without any visibility
C. It breaks the database
D. It prevents counting

<details><summary>Answer</summary><b>B</b> — With 3% true discrepancy rate and 5% tolerance, everything from 0–5% is auto-approved and invisible.</details>

---

**8.** Why rotate the counter as well as the location?

A. For fairness only
B. Coverage — fixed locations never get counted, and a fixed counter loses independence
C. To reduce scanner cost
D. Oracle limits per-user counts

<details><summary>Answer</summary><b>B</b> — Rotation prevents blind spots and the loss of counting independence.</details>

---

**9.** Why is root-cause coding mandatory rather than optional?

A. It satisfies auditors
B. Without it you count forever and learn nothing — it is what turns measurement into prevention
C. It reduces database size
D. It speeds up counting

<details><summary>Answer</summary><b>B</b> — 60% coded as `CYCLE_SHRINK` reveals a security problem that counting cannot fix.</details>

---

**10.** If `CYCLE_SHRINK` dominates the cause Pareto, what is the correct response?

A. Count more frequently
B. Tighten tolerance to zero
C. Route to security with access controls — counting will not fix theft
D. Increase scanner numbers

<details><summary>Answer</summary><b>C</b> — Unrecorded removal is a security control failure, not a counting process failure.</details>

---

## Scoring
- **9–10**: Ready to run a cycle counting programme.
- **7–8**: Solid; revisit frequency derivation and tolerance design.
- **5–6**: Re-read THEORY on bounded loss and root-cause coding.
- **<5**: Work through EXERCISES 2, 3, and 7 again.