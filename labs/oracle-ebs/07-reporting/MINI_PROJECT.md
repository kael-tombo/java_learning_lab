# Lab 07: Reporting (BI Publisher) — Mini Project

## Goal
Build an AP aging report with categories, drill-down, and currency conversion
in 90 minutes, proving the numbers reconcile.

## Requirements
- R1: Aging base view using due date with spot rate as at the aging date.
- R2: Level 1 summary by supplier category with five buckets.
- R3: Level 2 by supplier within a category, passing `vendor_id`.
- R4: Level 3 invoice detail, passing no further keys.
- R5: Missing-rate exception query.
- R6: Partition test proving bucket sums equal the total.
- R7: Unmapped category with a visible `UNMAPPED` bucket.
- R8: Bind parameters for as-of date and category, no `SYSDATE` in SQL.

## Steps
1. Load AP payment schedules across three currencies and four categories.
2. Build the aging base view with rate-as-at-date resolution.
3. Write the Level 1 query with mutually exclusive buckets.
4. Run the partition test; confirm zero difference.
5. Write Level 2 and confirm it returns the vendor ID for the hyperlink.
6. Write Level 3 filtered by `vendor_id`.
7. Delete one exchange rate and confirm the missing-rate query catches it.
8. Leave 5 suppliers unmapped and confirm `UNMAPPED` appears.
9. Verify totals match the AP subledger balance.

## Acceptance criteria
- Every invoice lands in exactly one bucket; the partition test returns zero.
- Changing the as-of date changes the output; re-running with the same date
  does not.
- A missing rate produces NULL and appears in the exception report, not a
  1.0 conversion.
- Unmapped suppliers appear in a visible bucket.
- Drill-down passes `vendor_id`, never a name.
- Reported total equals the AP open balance.

## Stretch
- Demonstrate the `INNER JOIN` understatement, then fix it.
- Add a `TRUNC(due_date)` variant and compare EXPLAIN PLAN output.