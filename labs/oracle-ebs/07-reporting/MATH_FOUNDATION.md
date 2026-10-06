# Lab 07: Reporting (BI Publisher) — Math Foundation

## 1. Aging Basis — Why the Choice Changes the Number

Two invoices, same aging date of 15 April, both dated 1 January, net 60.

| Invoice | Due date | Invoice-date age | Due-date age |
|---------|----------|------------------|--------------|
| A | 1 Jan | 104 days → 90+ | **-46 days → Current** |
| B | 1 Jan | 104 days → 90+ | -46 days → Current |

Now a third, dated 1 February net 30:

| Invoice | Due date | Invoice-date age | Due-date age |
|---------|----------|------------------|--------------|
| C | 3 Mar | 73 days → 61-90 | **43 days → 31-60** |

```
Invoice-date basis total overdue:  $A + $B + $C all counted as 61+ days
Due-date basis:                    $A, $B current; $C only 43 days overdue
```

**The invoice-date basis overstates overdue payables by including invoices not
yet due.** For cash forecasting, that is a material misstatement in the
conservative direction — which sounds safe but is actually wrong, because it
hides genuine timing.

## 2. Bucket Partition Proof

For the buckets to be correct, two conditions must hold.

### Exhaustiveness
Every row falls in some bucket:
```
Current (days ≤ 0) ∪ 0-30 (1..30) ∪ 31-60 (31..60) ∪ 61-90 (61..90) ∪ 90+ (>90)
= all integer days          ✓
```

### Mutual exclusivity
No day appears twice:
```
0-30 ends at 30; 31-60 starts at 31     → no overlap  ✓
```

### The classic bug

```sql
-- BROKEN: day 30 counted twice
WHEN days_overdue BETWEEN  0 AND 30 THEN bucket_1
WHEN days_overdue BETWEEN 30 AND 60 THEN bucket_2

-- Result: overstatement equal to the value of all day-30 invoices
```

Detection:
```
Difference = SUM(buckets) − SUM(total)
```

Any non-zero difference is a boundary defect. For a client with $40M in AP, a
boundary bug on day 30 could misstate by **hundreds of thousands** depending on
how many invoices fall exactly on day 30.

**Distribution matters**: in monthly aging run on period-end dates, a
significant fraction of invoices land on the boundary day, because due dates
cluster on payment terms.

## 3. Bucket Distribution and Report Design

Typical AP aging distribution:

| Bucket | % of invoices | % of value |
|--------|--------------|------------|
| Current | 55% | 48% |
| 0-30 | 20% | 22% |
| 31-60 | 12% | 14% |
| 61-90 | 8% | 9% |
| 90+ | 5% | 7% |

**Design implication**: the 0-30 and Current buckets hold ~70% of value. A report
that renders all five buckets with equal visual weight wastes attention. Make
**31-60 and beyond** the visually dominant bands — that is where the report's
conclusion lives.

## 4. Currency Conversion Error Magnitude

Suppose a client has invoices in 5 currencies, one of which is a high-volatility
currency.

```
Total AP: $500M
Non-USD portion: $180M
Spot rate moves ±8% in the period
```

If conversion uses today's rate where the invoice rate was intended:

```
Misstatement on affected currency: $180M × 8% = $14.4M potential
```

And the silent-default failure mode:

```sql
-- CATASTROPHIC: missing rate silently converts at 1.0
amount * NVL(rate, 1)
```

If the rate table is missing 40 invoices totalling $12M in JPY (≈ $85K):

```
Reported as:  $12,000,000   (at 1.0)
Actual:       $    85,000
Overstatement: $11.9M — in one report
```

**This is why `NULL` propagation plus an exception report is mandatory.** The
query must be incapable of quietly misstating by six orders of magnitude.

## 5. Currency Conversion Approaches

```
Effective rate = Amount in reporting currency / Amount in transaction currency
```

Three rate bases, three answers:

| Rate | USD value of €1M invoice |
|------|--------------------------|
| Original transaction rate | $1,080,000 |
| Spot at aging date | $1,095,000 |
| Month-end closing | $1,085,000 |

**Aging as at 31 January using a 3 March rate is not reproducible.** The report
run twice with the same date must produce identical output:

```
Reproducible ⇔ rate_date resolved as MAX(rate_date <= as_of_date)
```

## 6. Drill-Down Data Volume

Three levels over 40,000 open invoices:

| Level | Rows shipped | Payload (approx) |
|-------|--------------|------------------|
| 1: Category | 4 | 1 KB |
| 2: Supplier | 1,800 | 180 KB |
| 3: Invoice | 40,000 | 4 MB |

If level 1 shipped all detail and aggregated in the template:

```
Level 1 shipped: 40,000 rows = 4 MB
Aggregated in SQL: 4 rows = 1 KB
Reduction: 4,000×
```

At 3 requests/minute across 30 users:

```
Unaggregated: 120 requests/min × 4 MB = 480 MB/min = 28.8 GB/hour
Aggregated:   120 requests/min × 1 KB = 120 KB/min
```

**Unaggregated is not slow — it is unusable.**

## 7. Index Effectiveness — Why TRUNC() Matters

A range predicate on an indexed column can use a range scan:

```sql
WHERE due_date < :as_of + 1          -- index range scan  ✓
```

Wrapping the column in a function forces a full scan:

```sql
WHERE TRUNC(due_date) <= :as_of      -- full scan  ✗
```

### Cost difference on 4 million rows

| Approach | Rows examined | Buffers read | Elapsed |
|----------|---------------|--------------|---------|
| Range scan (indexed) | ~250,000 | ~25,000 | ~0.3 s |
| Full scan + TRUNC | 4,000,000 | ~400,000 | ~4.5 s |

```
15× more data read, 15× slower
```

At 30 users running the report during month-end, the difference is 4.5 s versus
0.3 s — either tolerable or the report times out, depending on load.

## 8. Unmapped Supplier Impact

Supplier category via a mapping table:

```
Total suppliers:      1,850
Mapped:               1,720  (93.0%)
Unmapped:               130  (7.0%)
Unmapped value:      $18.4M  (3.7% of AP)
```

With `INNER JOIN` (wrong):

```
Reported total:  $481.6M   (was $500.0M)
Understatement: $18.4M    (3.7%)
```

**No error is raised. The report simply shows less than the ledger.** A
reconciliation check against `AP` returns a difference nobody can explain.

With `LEFT JOIN` + `COALESCE(..., 'UNMAPPED')`:

```
Reported total:  $500.0M   ✓ reconciles
Visible finding: "UNMAPPED — $18.4M — 130 suppliers require mapping"
```

**The report reconciles and surfaces a data-quality issue at the same time.**
That is the correct design.

## 9. Report Cost Model

Monthly close report, 200 recipients:

```
Report runtime:              4 s
Requests/month:              200 (one per recipient) + 300 ad hoc = 500
Rows processed/month:        500 × 250,000 (level 1 unaggregated) = 125M
Aggregated in SQL:           500 × 250,000 = 125M, but 4 rows returned

Database CPU:  500 × 4 s = 2,000 s = 33 min of CPU/month
```

Negligible **if aggregated in SQL**. If not aggregated, add template processing:

```
RTF processing: 500 × 40 s = 20,000 s = 5.6 hours/month
```

The aggregation decision is the difference between 33 minutes and 5.6 hours of
instance CPU per month.

## 10. Bursting Delivery Volume

```
4 categories + 1 total = 5 PDF sections per run
Each PDF ~40 pages (full detail)
Size: ~2 MB

Delivery: 5 × 2 MB = 10 MB per run
Monthly: 10 MB × 12 = 120 MB/year
```

Trivial — which is why bursting should be cheap. The risk is not volume but
**over-sending**:

```
Burst guard missing → category filter defaults to NULL → "All"
→ 200 recipients each receive 40,000 rows / 180-page PDF
→ 200 × 2 MB = 400 MB, and 200 annoyed managers
```

The guard is worth more than the optimisation.

## 11. Aging Trend Analysis

Because the aging date is a parameter, trend analysis becomes a query:

```sql
SELECT TO_CHAR(aging_date,'YYYY-MM') period,
       SUM(CASE WHEN days > 90 THEN amount_usd ELSE 0 END) as bucket_90_plus,
       ROUND(100 * SUM(CASE WHEN days > 90 THEN amount_usd ELSE 0 END)
             / SUM(amount_usd), 2) AS pct_90_plus
  FROM xx_ap_aging_history
 GROUP BY TO_CHAR(aging_date,'YYYY-MM')
 ORDER BY period;
```

```
Jan: 7.0%   Feb: 6.4%   Mar: 7.8%   Apr: 6.1%
```

The March spike is now visible. With `SYSDATE` hardcoded, this analysis is
impossible — the report only ever describes today.

## 12. Conditional Formatting Value

Reading raw numbers to derive urgency is cognitively expensive:

| Approach | Time to answer "what needs attention?" |
|----------|---------------------------------------|
| Numbers only | ~15 seconds (compute 90+ total, scan) |
| Colour-coded | ~2 seconds (visual) |

Across 30 users, 20 runs/month:

```
Numbers only: 30 × 20 × 15 s = 2.5 hours/month of scanning
Colour-coded: 30 × 20 ×  2 s = 0.33 hours/month
Saving: ~2.2 hours/month
```

The formatting is not decoration — it is the report's conclusion, delivered in
the first glance.