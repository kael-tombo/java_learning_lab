# Lab 07: Reporting (BI Publisher) — VISION

## Where this lab takes you
From "the CFO wants AP aging by category with drill-down" to a report whose
numbers reconcile, are reproducible, and state their own basis.

## The Arc
1. **Semantics** — aging on due date, stated and documented.
2. **Partition** — mutually exclusive, exhaustive buckets that reconcile.
3. **Parameters** — aging date as an input, never `SYSDATE`.
4. **Currency** — spot rate as at date, missing rates surfaced.
5. **Mapping** — supplier category with a visible unmapped fallback.
6. **Drill-down** — passing IDs across three levels.
7. **Aggregation** — sum in SQL, not in the template.
8. **Delivery** — severity colour scale and configuration-driven bursting.

## Milestones (checkable)
- [ ] M1: Justify due-date aging over invoice-date with a worked example.
- [ ] M2: Build the aging base view with rate-as-at-date resolution.
- [ ] M3: Write the partition test and prove bucket sums equal the total.
- [ ] M4: Produce the missing-rate exception report and route it.
- [ ] M5: Prove a mapping with `INNER JOIN` understates, and that is visible.
- [ ] M6: Build three drill levels passing IDs, and break a link with a rename.
- [ ] M7: Aggregate in SQL and show the row reduction.
- [ ] M8: Configure bursting from a recipient table with a guard against all-category sends.

## Anti-Goals
- Aging on invoice date while presenting it as a payables report.
- Overlapping bucket boundaries such as `0-30` and `30-60`.
- Hardcoding `SYSDATE` so period-end aging is irreproducible.
- Converting at `NVL(rate, 1)` when a rate is missing.
- Using `INNER JOIN` to the category mapping so totals quietly understate.
- Filtering with `TRUNC(due_date)` and disabling the index.
- Aggregating 40,000 rows in the RTF template.
- Passing supplier names in drill-down hyperlinks.

## The one-sentence thesis
A report is correct when its numbers reconcile to the ledger and stay
reproducible — which means mutually exclusive buckets, stated rate basis,
visible gaps, and no silent defaults.