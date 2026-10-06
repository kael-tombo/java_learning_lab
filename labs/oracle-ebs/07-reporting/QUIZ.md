# Lab 07: Reporting (BI Publisher) — Quiz

**1.** Why age AP on due date rather than invoice date?

A. Due date is easier to query
B. Invoice-date aging counts invoices that are not yet due as overdue,
   misstating liability timing
C. Oracle requires it
D. Due date buckets are more granular

<details><summary>Answer</summary><b>B</b> — A net-60 invoice dated January is "not due" for two months. Counting it as overdue distorts cash forecasting.</details>

---

**2.** What makes a bucket definition correct?

A. It covers the common cases
B. Mutually exclusive and exhaustive — every row lands in exactly one bucket
C. It has five buckets
D. It matches the standard report

<details><summary>Answer</summary><b>B</b> — Overlaps double-count; gaps under-count. The partition test proves both.</details>

---

**3.** `BETWEEN 0 AND 30` and `BETWEEN 30 AND 60` — what is wrong?

A. Nothing
B. Day 30 is counted in both buckets, overstating the total
C. They are too slow
D. Oracle rejects it

<details><summary>Answer</summary><b>B</b> — Due dates cluster on payment terms, so day 30 can hold a significant share of invoices.</details>

---

**4.** Why is the aging date a parameter rather than `SYSDATE`?

A. Parameters are faster
B. Period-end aging must stay reproducible; hardcoding `SYSDATE` makes a signed-off
   report change when re-run
C. `SYSDATE` cannot be filtered
D. Oracle restricts it

<details><summary>Answer</summary><b>B</b> — Without it, a report whose numbers move on re-run cannot be signed off, and trend analysis is impossible.</details>

---

**5.** What must happen when no exchange rate exists for a currency?

A. Convert at 1.0
B. Use the previous available rate
C. Return NULL and surface it in an exception report
D. Omit the invoice

<details><summary>Answer</summary><b>C</b> — `NVL(rate, 1)` on ¥12M misstates by $11.9M invisibly. This is a financial reporting defect.</details>

---

**6.** Which rate type and date basis?

A. Any rate, today's date
B. `rate_type = 'C'` resolved as `MAX(rate_date) <= as_of_date`
C. The invoice's original rate only
D. Average rate

<details><summary>Answer</summary><b>B</b> — Consistent type and date resolution is what makes the output reproducible.</details>

---

**7.** Why `LEFT JOIN` with `COALESCE(...,'UNMAPPED')` rather than `INNER JOIN`?

A. `LEFT JOIN` is faster
B. `INNER JOIN` hides unmapped suppliers and understates the total with no error
C. Oracle recommends it
D. It uses less memory

<details><summary>Answer</summary><b>B</b> — 3.7% of AP ($18.4M) silently missing is unreconcilable. `UNMAPPED` reconciles *and* surfaces the gap.</details>

---

**8.** Why pass `vendor_id` rather than supplier name in drill-down?

A. IDs are shorter
B. Names are not unique and break links when renamed
C. Names cannot be passed as parameters
D. IDs render faster

<details><summary>Answer</summary><b>B</b> — A rename silently breaks every saved link with no error.</details>

---

**9.** Why aggregate in SQL rather than the template?

A. RTF cannot sum
B. Shipping 250,000 rows to aggregate 4 in the layout is a 4,000× waste
C. SQL aggregation is always required
D. Templates cannot group

<details><summary>Answer</summary><b>B</b> — 33 minutes of CPU per month versus 5.6 hours. The layout choice has an instance-level cost.</details>

---

**10:** What does `WHERE TRUNC(due_date) <= :d` do to an index?

A. Nothing
B. Disables it — the function is applied to the column, forcing a full scan
   (4M rows / 4.5 s versus 250K rows / 0.3 s)
C. Speeds it up
D. Creates a hint

<details><summary>Answer</summary><b>B</b> — Use `due_date < :d + 1` to keep the range predicate index-friendly.</details>

---

## Scoring
- **9–10**: Ready to build production BI Publisher reports.
- **7–8**: Solid; revisit bucket definitions and currency handling.
- **5–6**: Re-read THEORY on aging semantics and reconciliation.
- **<5**: Work through EXERCISES 1, 3, and 4 again.