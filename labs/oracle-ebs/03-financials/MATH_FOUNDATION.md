# Lab 03: Financials — Math Foundation

## 1. Hold Rate vs Escape Rate

Two rates that must always be reported together.

```
Hold rate   = held invoices / total invoices
Escape rate = real discrepancies that passed / total invoices
```

| Remediation | Hold rate | Escape rate | Verdict |
|-------------|-----------|-------------|---------|
| Baseline | 30% | 0% | Control works, badly calibrated |
| **Good fix** | **8%** | **0%** | ✅ Control preserved |
| Bad fix | 8% | 2% | ❌ Control disabled |

**Only the escape rate indicates control weakness.** Reporting hold rate alone
makes a successful fix indistinguishable from disabling the control — and that
is what an auditor will assume.

## 2. Variance as a Distribution

Price variance for an invoice line:

```
variance% = ((invoiced_qty × invoiced_price) - receipt_price)
             / receipt_price × 100
```

Real-world variance is not a point value; it is a distribution caused by
rounding, currency conversion, volume rebates, and contract true-ups.

```
cumulative%  bucket
   62%         0%
   85%         1%
   94%         2%
   97%         3%
   98.5%       4%
   99.2%       5%      <-- noise ends here
   99.4%       6%
   ...
   99.6%      40%      <-- real problems, sparsely populated
```

## 3. Choosing a Tolerance from the Distribution

The tolerance should sit just above the noise band:

```
Tolerance = value where cumulative% first reaches ~97–98%
```

In the table above: **tolerance = 4–5%**.

**Why not zero?** Zero means *any* difference holds, including rounding noise.
The control then fires on non-problems and users learn to ignore it — an
automatic false-positive rate of ~99% destroys the signal.

**Why not 40%?** That matches the problem cases too. The control fires on real
discrepancies, which is its job, but a tolerance that wide invites criticism and
undermines the control's credibility.

The defensible statement to an auditor: *"The tolerance was set at the 97th
percentiles of observed variance, which separates rounding and rebate effects
from material discrepancies."*

## 4. Percentile Reasoning

If variance is modeled as roughly normal with mean μ and standard deviation σ:

```
Tolerance ≈ μ + kσ
```

| k | Captured | Use |
|---|----------|-----|
| 1.0 | 68% | Too tight — fires constantly |
| 2.0 | 95% | Reasonable for low-risk categories |
| **3.0** | **99.7%** | **Common choice; conservative** |
| 4.0 | 99.99% | Very permissive — needs justification |

Deriving the tolerance empirically from the actual data is stronger than
assuming normality — real AP variance is often skewed, not Gaussian.

## 5. Quantity Matching: The Semantics Problem

Three quantities exist, and only two of them are comparable:

```
Ordered  Q_ord  — what was committed
Received Q_rec  — what arrived
Invoiced Q_inv  — what was billed
```

The correct comparison for a normal receipt is `Q_inv ≈ Q_rec`.
The incorrect comparison is `Q_inv ≈ Q_ord`.

### When does each comparison matter?

| Situation | Correct basis | Rationale |
|-----------|---------------|-----------|
| Normal receipt | Received | Supplier bills what arrived |
| Short shipment | Received | Short delivery is normal |
| Price hold | Receipt price | Invoice price vs actual receipt price |
| **Over-invoice** | **Both** | Must catch Q_inv > Q_rec **and** Q_inv > Q_ord |

Over-invoicing is the case the control must never miss. Matching on received
quantity alone would still catch it, provided the received figure is accurate.

### Impact of using the wrong basis
With 8% average short-shipment rate:
- Matching on ordered → ~8% of all lines hold on quantity.
- Matching on received → near 0% hold on legitimate short shipments.
- **False-positive rate drops by roughly the entire hold count.**

## 6. Supplier Cycle Time Impact

```
DPP = 5 days        (days payable outstanding style metric)
With holds:
  avg_days_held = 12
  effective DPP = 5 + 12 = 17 days

Hold reduction → 8% hold rate → avg_days_held ≈ 2
  effective DPP = 7 days

Improvement = 17 / 7 ≈ 2.4×
```

Quantifying this in supplier-facing terms (rather than internal hold counts) is
what makes the business case land.

## 7. Hold Taxonomy Concentration

Holds follow a steep power law — a few reasons dominate:

```
Top reason A      : 45% of invoices
Top 2 reasons     : 68%
Top 3 reasons     : 78%
Remaining 20+     : 22%
```

**Implication**: fixing the top reason alone addresses nearly half the problem.
Fixing all 20 gets you 68%. Prioritisation by value at risk, not by count of
reason codes, is the correct sequencing.

## 8. Before/After Measurement

Use the same query and the same window before and after:

```sql
-- Run BOTH before and after the change. Same SQL, same period length.
SELECT ROUND(100 * COUNT(DISTINCT h.invoice_id)
             / COUNT(DISTINCT i.invoice_id), 2) AS hold_rate_pct,
       ROUND(AVG(SYSDATE - i.invoice_date), 1)  AS avg_days_held,
       COUNT(DISTINCT i.invoice_id)             AS sample_size
  FROM ap_invoices_all i
  LEFT JOIN ap_holds_all h ON h.invoice_id = i.invoice_id AND h.release_flag='N'
 WHERE i.invoice_date BETWEEN DATE '2026-01-01' AND DATE '2026-03-31';
```

**Always report sample size.** A 30% hold rate on 40 invoices is not comparable
to a 10% rate on 40,000.

## 9. Control Strength After Remediation

Verify the control still works with a deliberate test:

```
Test: inject a 30% over-invoice against a 100-unit receipt
Expected: HOLD raised (over-invoice beyond tolerance)
Actual:   ?
```

If the test invoice validates cleanly, the remediation has broken the control
regardless of what the hold rate says. **Test the control, not just the metric.**