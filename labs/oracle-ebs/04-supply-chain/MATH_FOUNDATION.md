# Lab 04: Supply Chain (Cycle Counting) — Math Foundation

## 1. The ABC/Pareto Distribution

Inventory value is **not** uniformly distributed across SKUs. It follows a steep
power law:

```
Sorted by annual dollar usage, cumulative % of total:
Top     5% of SKUs  →  ~50% of value
Top    20% of SKUs  →  ~80% of value   (the "A" class)
Top    50% of SKUs  →  ~95% of value   (A + B)
Bottom 50% of SKUs  →  ~5% of value    (the "C" class)
```

### What this means for counting effort

Assume counting cost is uniform per SKU:

| Strategy | SKUs counted/yr | Value protected | Cost |
|----------|-----------------|-----------------|------|
| Count everything monthly | 100% × 12 = 1200% | 100% | 1200 units |
| ABC (A monthly, B quarterly, C annual) | 20%×12 + 30%×4 + 50%×1 | ~80%+ | 2.4 + 1.2 + 0.5 = **4.1 units** |
| Count everything annually | 100% × 1 | ~40%¹ | 1 unit |

¹ At annual frequency you only detect drift once, so protection is much lower
than the 100% nominal value coverage suggests.

**The ABC strategy protects more value at ~1/3 the cost of monthly full counts.**
That is the entire economic case for cycle counting, and it comes straight from
the Pareto distribution.

## 2. Bounded Loss — The Real Value of Cycle Counting

This is the argument that justifies cycle counting even when accuracy is already
acceptable.

```
Expected loss between counts ≈ Discrepancy rate × Value throughput × Interval
```

**Annual counting (the current state)**:
```
= 2% × $500K/month × 12 months = $120,000/yr per A-item cohort
= $2M observed discrepancy (matches the scenario)
```

**Cycle counting, A monthly, B quarterly, C annual**:
```
A: 2% × $500K × 1 month  × (20% of items)  = $2,000/item-cohort-month
B: 2% × $150K × 3 months × (30% of items)  = $2,700/item-cohort-quarter
C: 2% × $10K  × 12 months × (50% of items)  = $1,200/item-cohort-year
```

Summed across a representative cohort, the loss window shrinks by roughly
**an order of magnitude** — not because discrepancies vanish, but because each
one is detected and corrected within days rather than a year.

```
Reduction factor ≈ 12 / 1 = 12x for A items
```

**The value of cycle counting is bounded loss, not perfect accuracy.** Both
matter; only the first is quantified by frequency.

## 3. Deriving Count Frequency from Materiality

Set the interval so expected unreconciled loss stays under a materiality
threshold:

```
Interval ≤ Materiality / (Discrepancy rate × Monthly value throughput)
```

Worked example — an A item at $500K/month, 2% discrepancy rate, $50K materiality:

```
Interval ≤ 50,000 / (0.02 × 500,000)
         = 50,000 / 10,000
         = 5 months
```

Monthly counting is therefore **conservative** for this item. Stating that
explicitly — "our derivation permits quarterly; we count monthly because these
are raw materials with theft exposure" — is what makes the policy defensible
rather than arbitrary.

### Frequency table from the derivation

| Item value/mo | Disc. rate | Materiality | Derived max interval |
|---------------|-----------|-------------|---------------------|
| $500K | 2% | $50K | 5 months |
| $500K | 2% | $10K | 1 month |
| $50K | 2% | $50K | Never (below threshold) |
| $500K | 8% | $10K | 0.25 months → weekly |

Note the fourth row: **high-value, high-discrepancy items may require weekly
counting.** ABC alone would classify that item as "A, monthly" and miss it.

## 4. Why Movement Matters as a Second Dimension

Two items with identical annual dollar usage can have very different risk:

| Item | Annual usage | Transactions | Risk |
|------|-------------|-------------|------|
| X | $500K | 12/yr (bulk, quarterly moves) | Low |
| Y | $500K | 1,200/yr (small, frequent moves) | **High** |

Item Y has 100× more transactions, so 100× more opportunities for error. Pure
ABC assigns them the same frequency.

**2×2 matrix approach:**

```
            HIGH VALUE          LOW VALUE
HIGH        Count monthly       Count quarterly
MOVEMENT
LOW         Count quarterly     Count annually
```

The upper-right quadrant (high value, low movement) is where pure ABC over-
protects. The lower-left (low value, high movement) is where pure ABC
under-protects — and those are often the items with the highest **shrinkage
rate**, because they are small and easy to steal.

## 5. Tolerance Threshold Mathematics

```
Variance % = |counted − system| / system × 100
```

### The false-approval problem with wide tolerance

Suppose true discrepancy rate is 3% and tolerance is 5%:

| Variance | Discrepancy? | Auto-approved? | Result |
|----------|--------------|----------------|--------|
| 1% | noise | yes | Correct |
| 4% | real | **yes** | ❌ Missed |
| 4.5% | real | **yes** | ❌ Missed |
| 7% | real | no | Escalated |

**A 5% tolerance misses a band of real discrepancies between 0% and 5%.** This
is why tolerances must be paired with root-cause coding — the misses are
invisible otherwise.

### Per-class tolerance rationale

| Class | Tolerance | Rationale | Value at stake at tolerance |
|-------|-----------|-----------|---------------------------|
| A | 0.5% | High value | 0.5% of $500K = $2,500 |
| B | 2% | Moderate | 2% of $50K = $1,000 |
| C | 5% | Low value | 5% of $5K = $250 |

The absolute value at stake justifies the differing tolerances. **A percentage
alone is misleading** — 5% of a $2M item is $100K, which is a management
decision, not a floor-level approval.

### Both percentage AND value cap are needed

```
ESCALATE if variance_pct > tolerance
        OR variance_value > max_adj_value
```

A percentage-only rule approves a $100K adjustment because it is "only 4%".

## 6. Approval Queue Load

Approval workload determines whether a tolerance programme is sustainable.

```
Escalation rate ≈ Discrepancy rate × (1 - tolerance_coverage)
```

With 3% discrepancy rate and tolerance covering 95% of discrepancies in the
value band:

```
Escalations = 3% × 5% = 0.15% of counts
```

For 5,000 counts/year (ABC-weighted):

```
0.15% × 5,000 = 7.5 escalations/year
```

Completely manageable. Now **without** tolerance (escalate everything):

```
3% × 5,000 = 150 escalations/year
```

That is the queue that makes AP teams stop approving carefully and start
approving reflexively. Tolerance exists to protect the attention of approvers on
the cases that matter.

## 7. Scanner Economics

### Manual counting
```
Cost = Items × Seconds/item × Hourly rate
     = 500 × 45s × ($0.35/3600) per second
     = 500 × 0.00875 = $4.38/hr... recompute:
     = (500 × 45/3600) hours × $22/hr
     = 6.25 hours × $22 = $137.50 per session
```

### Barcode scanning
```
Count time: 500 × 8s = 4,000s = 1.11 hours
Cost = 1.11 × $22 = $24.44 + scanner amortisation
```

```
Reduction = 137.50 / 24.44 ≈ 5.6x
```

For 260 sessions/year:

```
Saving = (137.50 − 24.44) × 260 = $29,400/year
```

Against, say, $15,000 for 4 scanners → payback in ~6 months. Reasonable.

### The stronger argument: error reduction

Manual counting has a transcription error rate of roughly **1–3%** per line:

```
500 items × 2% misc = 10 miscounts per session
260 sessions × 10 = 2,600 miscounted discrepancies/year
```

Those are **false discrepancies** that consume investigation time and erode
trust in the programme. Scanning largely eliminates them.

```
Justification = investigation cost of false discrepancies
             + labour saving
             = accuracy benefit (larger) + labour benefit (secondary)
```

## 8. Root Cause Pareto — Finding the Real Problem

Discrepancies cluster by cause, just as inventory value clusters by item:

```
Cause               Value    Cum %   Fix
UNREC_SHIP         $1.2M    60%     Barcode at despatch point
CYCLE_SHRINK       $0.5M    85%     Security controls — NOT counting
TRANS_ERR          $0.2M    95%     Retraining + approval tightening
DAMAGE             $0.1M   100%     Scrap procedure
```

**Reading**: 60% of value is fixed by barcoding the despatch step — a 1-week
change. 25% is shrinkage, which counting will never fix.

```
Counting effort spent on the top two causes = 85%
Effectiveness of "count more" alone          = captures only TRANS_ERR + DAMAGE ≈ 15%
```

This is the argument for root-cause coding: it redirects effort from
measurement to prevention.

## 9. Accuracy Target Math

```
Accuracy % = Zero-variance items / Total counted × 100
```

Industry expectations:

| Class | Target | Rationale |
|-------|--------|-----------|
| A | 98% | High value; errors are expensive |
| B | 95% | Moderate |
| C | 90% | Low value; not worth the effort |

### Improvement trajectory

```
Baseline (annual count only):  84%
Month 3  (programme starting): 86%
Month 6  (causes being fixed):  91%
Month 12 (steady state):       96% overall, 98% on A
```

Note the **lag**: accuracy improves slowly at first because the programme is
still measuring. It improves faster once cause codes start driving process
fixes. Anyone expecting month-1 improvement from counting alone will conclude
the programme failed.

## 10. Coverage Math — Are You Actually Counting Enough?

```
Coverage % = SKUs counted in period / Total active SKUs × 100
```

With the ABC schedule:

| Class | Share | Frequency | Annual count rate |
|-------|-------|-----------|-------------------|
| A | 20% | Monthly | 240% (counted 2.4×/yr each) |
| B | 30% | Quarterly | 120% |
| C | 50% | Annual | 100% |
| **Weighted** | | | **160% of SKUs/yr** |

Every SKU counted ≥1×/year, A items counted 2.4×/year. If a site reports 160%
coverage, the schedule is working as designed — **that is not over-counting**,
it is the intended rotation.

## 11. Value at Risk — the Number for the Business Case

```
Annual expected loss = Σ over items of (disc_rate_i × annual_usage_i)
                     = Σ (annual_usage_i) × 0.02
                     ≈ 0.02 × Total annual dollar usage
```

For $500M of annual usage:

```
Annual expected loss = $10M (2%)
```

Cycle counting at 4.1 cost-units/yr versus 1 cost-unit for annual counting —
but recovering 85% of that $10M is the comparison:

```
Recovered ≈ $8.5M/yr
Programme cost ≈ 3.1 extra cost-units × counting labour

Even if a cost-unit is $50K: cost = $155K, benefit = $8.5M
ROI ≈ 55:1
```

**Always present the recovered-loss figure, not the cost saving.** Nobody
funds a counting programme because it saves counting labour.