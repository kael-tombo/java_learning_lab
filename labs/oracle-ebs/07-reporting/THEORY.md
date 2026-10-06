# Lab 07: Reporting (BI Publisher) — Theory

## The Scenario

A CFO wants an AP Aging report showing aging buckets by supplier category, with
drill-down to invoice detail. The standard Oracle AP Aging report supports
neither supplier categorisation nor drill-down. It must be deployed as an EBS
concurrent program.

Requirements: buckets 0-30 / 31-60 / 61-90 / 90+ days, grouping by category
(Raw Materials, MRO, Services, Utilities), drill-down category → supplier →
invoice, multi-currency conversion to USD, and aging based on **due date**.

## Principle 1: "Aging" is ambiguous and the choice is consequential

Two defensible definitions:

| Basis | Measures | Use case |
|-------|----------|----------|
| **Invoice date** | How old the invoice is | Vendor document age |
| **Due date** | How overdue the payment is | **Payables management** |

For AP aging intended to drive collections and cash planning, **due date is
correct**:

```
Invoice date basis:  Invoice dated Jan 1, net 60 → "0-30 days" on Jan 5.
                     But payment isn't due until Mar 2. Calling it current is
                     misleading if you are forecasting cash.

Due date basis:      Same invoice on Jan 5 → "Not due".
                     On Apr 1 → "60+ overdue". Accurate.
```

**Getting this wrong is the most common defect in AP aging reports**, and it
misstates liability timing in either direction. Decide explicitly, document the
basis in the report header, and never mix them.

## Principle 2: Bucket boundaries must be mutually exclusive and exhaustive

A classic bug: `BETWEEN 0 AND 30` and `BETWEEN 31 AND 60` leave day 30.5
unclassified — or with integer days, `BETWEEN 1 AND 30` and `BETWEEN 30 AND 60`
double-counts day 30.

```
Clean definition using half-open intervals:
  Current      : days_due <= 0
  0-30         : days_due BETWEEN  1 AND 30
  31-60        : days_due BETWEEN 31 AND 60
  61-90        : days_due BETWEEN 61 AND 90
  90+          : days_due >  90
```

Verify with a **partition test**: every row must land in exactly one bucket, and
the sum across buckets must equal the unclassified total.

```
SUM(bucket amounts) == SUM(all invoice amounts)   ← non-negotiable
```

If they differ, a boundary overlaps or a case is unhandled. This check belongs in
a test, not in someone's head.

## Principle 3: Aging "as at" is a parameter, not `SYSDATE`

Hardcoding `SYSDATE` makes a report irreproducible. Finance routinely needs:

- "Aging as at period end" (for statutory reporting)
- "Aging as at today" (for management)
- "Aging as at 90 days ago" (for trend analysis)

```sql
WHERE TRUNC(ps.due_date) <= :p_as_of_date
```

**Period-end aging must not change tomorrow.** A report whose numbers move when
you re-run it cannot be signed off.

## Principle 4: Currency conversion must be stated, dated, and consistent

Aging a multi-currency AP balance means choosing a rate basis:

| Basis | Source | Use |
|-------|--------|-----|
| **Spot rate as at aging date** | `GL_DAILY_RATES` | Management reporting |
| Original transaction rate | Invoice header | Statutory |
| Current rate | `GL_DAILY_RATES` at report run | Working capital |

For management aging, spot rate as at the aging date:

```sql
JOIN gl_daily_rates r
  ON r.set_of_books_id   = :p_ledger
 AND r.currency_code     = i.invoice_currency_code
 AND r.rate_date         = (SELECT MAX(r2.rate_date) FROM gl_daily_rates r2
                             WHERE r2.set_of_books_id = r.set_of_books_id
                               AND r2.currency_code = r.currency_code
                               AND r2.rate_date <= :p_as_of_date)
 AND r.rate_type         = 'C'
```

**Three rules that make the number defensible:**

1. State the rate basis on the report.
2. Use `rate_type = 'C'` (closing) consistently.
3. Handle a missing rate explicitly — never silently convert at 1.0.

```sql
-- Missing rate must be VISIBLE, not defaulted
CASE WHEN r.rate_type IS NULL THEN NULL ELSE amount * r.conversion_rate END
```

**A silent 1.0 conversion understates or overstates the liability without any
visible error.** This is a financial reporting defect, not a cosmetic one.

## Principle 5: Drill-down needs a key, not a guess

Drill-down from category → supplier → invoice works only if each level passes a
**stable identifier** forward:

```
Level 1: Category   → passes :p_category
Level 2: Supplier   → passes :p_supplier_id
Level 3: Invoice    → no further link needed
```

Two rules:

1. **Pass IDs, not names.** A supplier name is not unique; `vendor_id` is.
2. **Return the same columns.** Each level's query must project the level's own
   key so the next hyperlink has something to pass.

```sql
-- BI Publisher hyperlink parameter
<a href="...?pSupplierId=[vendorId]&pCategory=[category]">
```

This means three data models (or one model with a level parameter). A single
query cannot produce three drill levels — each level is a separate result set.

## Principle 6: Grouping by supplier category requires a mapping

Supplier category is not a standard field. It must be derived:

- A flexfield segment on the supplier master, or
- A cross-reference table, or
- Derived from the PO category

```sql
LEFT JOIN xx_supplier_category sc ON sc.vendor_id = v.vendor_id
```

**Handle the unmapped case.** A `LEFT JOIN` with no fallback makes unmapped
suppliers disappear from the report — silently understating the total.

```sql
COALESCE(sc.category_name, 'UNMAPPED')    -- visible gap, not a hidden one
```

An unmapped supplier bucket is a data-quality finding. Hiding it produces a
report that reconciles to nothing.

## Principle 7: Report performance is a design property

AP aging touches large tables. The query shape determines whether it is usable.

```sql
-- BAD: function on the filter column prevents index use
WHERE TRUNC(due_date) <= :p_as_of_date
WHERE NVL(category, 'X') = :p_category

-- GOOD: make the data fit the index
WHERE due_date < :p_as_of_date + 1
WHERE category = :p_category
```

Rules:

1. **No functions on filtered columns** — use range predicates instead.
2. **Filter in SQL, not in the template.** Post-filtering in the layout processes
   every row and discards most.
3. **Aggregate as late as possible.** If you only need totals by category, sum in
   SQL; do not ship 200,000 detail rows to sum in RTF.
4. **Test with production volume.** A report that runs in 2 seconds on the test
   dataset and 4 minutes on production is not working.

```
Detail rows shipped:  200,000
Aggregated in SQL:    4 categories
Reduction:            50,000×
```

## Principle 8: Conditional formatting encodes policy

RTF conditional formatting is not decoration — it is how a report communicates
priority.

```
Current (green)      — no action
0-30 (yellow)        — monitor
31-60 (orange)       — escalate
61-90 (red)          — intervene
90+ (bold red)       — executive escalation
```

This gives the reader the report's conclusion without needing to interpret
numbers. Design the colours as a **severity scale**, not a category list.

## Principle 9: Bursting delivers to the reader

A report nobody receives is not deployed. Bursting sends each section to a
different recipient:

| Section | Recipient | Schedule |
|---------|-----------|----------|
| Total | CFO | Monthly |
| Raw Materials | Category manager | Monthly |
| MRO | Category manager | Monthly |
| Services | Category manager | Monthly |

Bursting uses a **query-driven XML** mapping sections to recipients:

```xml
<bursting>
  <xapi:request select="SELECT 'TOTAL' section, 'cfo@company.com' recipient
                         FROM dual
                       UNION ALL
                       SELECT category, manager_email FROM xx_cat_manager"/>
</xapi:request>
```

The recipient mapping must come from configuration, not a hardcoded list —
managers change.

## Principle 10: Register it properly

As an EBS concurrent program the report needs:

```
1. Data model uploaded to the BI Publisher repository
2. Layout (RTF) uploaded and associated
3. Concurrent Program Executable of type 'BIPUBLISHER'
4. Concurrent Program with parameters: as-of date, category, currency
5. Responsibility / request group setup for bursting
```

**Validate before bursting.** A report that emails 4,000 rows to 200 managers
because a filter defaulted to "All" is worse than no report.

## Design Order

1. Decide the aging basis (due date) and the rate basis (spot as at date).
2. Define buckets with mutually exclusive, exhaustive boundaries.
3. Design the data model with indexed predicates and bind variables.
4. Aggregate in SQL wherever the layout only needs totals.
5. Add the supplier category mapping with a visible unmapped fallback.
6. Design three drill levels passing IDs, not names.
7. Build the RTF with a severity colour scale.
8. Set up bursting from a configuration-driven recipient query.
9. Register the program and test parameters.
10. Run a partition test: bucket sums must equal the total.

## Anti-Patterns

- Aging from invoice date while calling it a payables report.
- Overlapping bucket boundaries (`BETWEEN 1 AND 30` and `30 AND 60`).
- Hardcoding `SYSDATE` so period-end aging is irreproducible.
- Silently converting at 1.0 when a rate is missing.
- `LEFT JOIN` to the category mapping with no fallback, hiding unmapped suppliers.
- Functions on filtered columns defeating indexes.
- Filtering in the template instead of in SQL.
- Passing supplier names in drill-down links.
- Bursting without validating the filter defaults.

## Summary

The report was straightforward SQL; the judgement was in the semantics. Aging
on due date rather than invoice date made the numbers meaningful for cash
planning; exclusive bucket boundaries made them reconcile; spot rates stated and
dated made them auditable, with missing rates surfaced rather than defaulted;
ID-based drill-down made navigation reliable; SQL-side aggregation kept the
report fast; and a visible unmapped category meant the report reconciled to the
ledger instead of quietly to less than it.