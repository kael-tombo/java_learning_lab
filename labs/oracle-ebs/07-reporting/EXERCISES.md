# Lab 07: Reporting (BI Publisher) — Exercises

## Exercise 1: Justify the Aging Basis
**Time**: 20 minutes | **Difficulty**: Intermediate

### Objective
Argue due-date aging over invoice-date aging with numbers.

### Steps
1. Take three invoices with different payment terms.
2. Compute aging on both bases at one date.
3. Identify which invoices are misclassified by the invoice-date basis.
4. State which basis suits cash forecasting.

### Verification
- [ ] Both bases computed for the same set
- [ ] At least one invoice shown misclassified
- [ ] Due-date basis justified for payables management

---

## Exercise 2: Build the Aging Base View
**Time**: 30 minutes | **Difficulty**: Intermediate

### Objective
Create a view with due-date aging and as-at-date currency conversion.

### Steps
1. Join `ap_payment_schedules` to `ap_invoices_all`.
2. Resolve the closing rate as `MAX(rate_date) <= :p_as_of_date`.
3. Return NULL, never 1.0, when no rate exists.
4. Add indexes supporting the range predicate.

### Verification
- [ ] Aging basis is `due_date`
- [ ] Only `rate_type = 'C'` used
- [ ] Missing rate produces NULL
- [ ] Index supports `due_date < :as_of + 1`

---

## Exercise 3: Build Buckets and Prove the Partition
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Define mutually exclusive buckets and verify reconciliation.

### Steps
1. Implement Current / 0-30 / 31-60 / 61-90 / 90+.
2. Run the partition test comparing bucket sums to the total.
3. Introduce a deliberate boundary overlap.
4. Confirm the test catches it.

### Verification
- [ ] Buckets cover all integer day values exactly once
- [ ] Partition test returns zero difference
- [ ] Deliberate overlap is detected

---

## Exercise 4: Missing Rate Exception Handling
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Ensure a missing exchange rate cannot silently misstate the report.

### Steps
1. Delete one currency's rate for the aging date.
2. Run the report and confirm NULL amounts.
3. Run the exception query and confirm the row appears.
4. Compare the misstatement that `NVL(rate, 1)` would have produced.

### Verification
- [ ] Report shows NULL, not 1.0 conversion
- [ ] Exception query returns the row
- [ ] Misstatement magnitude quantified

---

## Exercise 5: Supplier Category Mapping
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Group by category without hiding unmapped suppliers.

### Steps
1. Create the mapping table and map 93% of suppliers.
2. Run the report with `LEFT JOIN` + `COALESCE`.
3. Run it with `INNER JOIN` and compare the total.
4. Quantify the understatement.

### Verification
- [ ] `UNMAPPED` bucket visible in the correct version
- [ ] Understatement quantified for the `INNER JOIN` version
- [ ] Correct version reconciles to the subledger

---

## Exercise 6: Three-Level Drill-Down
**Time**: 30 minutes | **Difficulty**: Intermediate

### Objective
Build drill-down passing stable identifiers.

### Steps
1. Level 1 returns category and aggregates in SQL.
2. Level 2 filters on `pCategory` and returns `vendor_id`.
3. Level 3 filters on `pSupplierId`.
4. Rename a supplier and confirm the Level 2 link still works.

### Verification
- [ ] Each level passes an ID, not a name
- [ ] Rename does not break navigation
- [ ] Aggregation happens in SQL at every level

---

## Exercise 7: Performance at Production Volume
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Prove the query is index-friendly at scale.

### Steps
1. Load 250,000 open invoices across 14 currencies.
2. Run with `due_date < :as_of + 1`; capture the plan.
3. Run with `TRUNC(due_date) <= :as_of`; capture the plan and time.
4. Compare elapsed time and rows examined.

### Verification
- [ ] Correct form produces an index range scan
- [ ] `TRUNC()` form produces a full scan
- [ ] Both elapsed times measured and compared

---

## Exercise 8: Layout, Conditional Formatting, and Bursting
**Time**: 30 minutes | **Difficulty**: Intermediate

### Objective
Deliver the report with a severity scale and safe bursting.

### Steps
1. Build the RTF layout with the five bands colour-coded as a ramp.
2. Add the base information header stating date, basis, and currency.
3. Create the recipient table and the bursting definition.
4. Attempt to burst with a NULL category; confirm the guard refuses.

### Verification
- [ ] Colour scale reads as a severity ramp
- [ ] Header states aging basis, rate basis, and currency
- [ ] Bursting guard blocks the all-category send
- [ ] Recipients sourced from configuration, not hardcoded

---

## Exercise 9: Reproducibility Test
**Time**: 20 minutes | **Difficulty**: Intermediate

### Objective
Prove the same as-at date always yields the same output.

### Steps
1. Run with a fixed as-at date twice; compare outputs.
2. Change the as-at date and confirm the output changes.
3. Add an exchange rate that did not exist at the first as-at date.
4. Confirm the historical run is unaffected.

### Verification
- [ ] Identical output for identical parameters
- [ ] Different output for a different as-at date
- [ ] Later data does not alter historical results