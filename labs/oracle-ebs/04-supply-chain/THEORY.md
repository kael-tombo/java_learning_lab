# Lab 04: Supply Chain (Cycle Counting) — Theory

## The Scenario

A chemical manufacturer runs one physical inventory per year, requiring a full
plant shutdown. It reveals a **$2M discrepancy**. Analysis shows **80% of the
discrepancies come from 20% of SKUs** — high-value, fast-moving raw materials.
The warehouse has no mobile scanning capability.

## Principle 1: The annual count is not a control, it is a surprise

An annual count measures accuracy once, twelve months after the last one.

```
Jan 1   count says 1000 units        ← accurate
Jan 2   issue 10 without a scan     ← 990
...
Dec 31  count says 940 units        ← "20 lost this year"
```

The annual count cannot tell you **when** the loss occurred, **what caused it**,
or **which process** let it happen. By the time you know, the total is large
enough to be material and the transactions are too old to investigate.

Cycle counting inverts this: count continuously, so discrepancies are found
**small and recent** — while the transactions that caused them are still traceable.

```
Weekly counts  → max 1 week of drift   → max loss ≈ $16K
Monthly (A)    → max 1 month           → max loss ≈ $167K
Annual         → max 12 months         → max loss = $2M
```

**The value of cycle counting is not accuracy. It is bounded loss.**

## Principle 2: Not all inventory deserves equal attention

Inventory accuracy does not vary uniformly with value. It varies with
**value density and movement**:

| Factor | Effect on discrepancy risk |
|--------|---------------------------|
| High dollar value | Each error is expensive |
| High movement | More transactions = more chances to err |
| Bulk/low value | Errors are individually cheap |

This means counting effort should follow value, not item count. That is the
Pareto/ABC insight, and it is the entire economic justification for cycle
counting.

```
If you count everything monthly   → high cost, low marginal accuracy gain
If you count A items monthly,     → high cost avoided, 80% of value protected
  B quarterly, C annually
```

## Principle 3: ABC classification — and defending the cutoffs

Standard cutoffs:

| Class | Cumulative % of annual dollar usage | Count frequency |
|-------|-----------------------------------|-----------------|
| A | top ~80% | Monthly |
| B | next ~15% (~80–95%) | Quarterly |
| C | final ~5% | Annually |

**The cutoffs are a starting point, not a law.** Two refinements matter:

1. **Use annual dollar usage**, not unit count or item value. The metric must
   reflect what actually drives cost.
2. **Add movement as a second dimension.** A high-value item that never moves is
   easy to count accurately; a high-value item that moves daily is the real
   risk. Some sites use a 2×2 matrix (value × movement) rather than pure ABC.

An A item that is static does not need monthly counts. An item that is
mid-value but moves constantly does. **Pure ABC misses this.**

## Principle 4: Frequency should be derived, not defaulted

A defensible frequency formula weights value and movement:

```
Count frequency ∝ (dollar value × movement rate)
```

Or more simply, set the frequency so that the **expected loss between counts**
stays below a materiality threshold:

```
Max acceptable unreconciled loss = Materiality threshold
Loss between counts ≈ Discrepancy rate × Value per period × Count interval

Solve for Count interval:
Count interval ≤ Materiality / (Discrepancy rate × Value per period)
```

For an A item worth $500K/month with a 2% discrepancy rate and $50K materiality:

```
Interval ≤ 50,000 / (0.02 × 500,000) = 5 months
```

So monthly is conservative here — which is fine, but the *derivation* is what
makes it defensible in an audit. Hardcoding "A = monthly" without the arithmetic
is a convention, not a control.

## Principle 5: Tolerance limits are an approval control, not a counting rule

After a count, two numbers exist: system quantity and counted quantity. What
happens next depends on the difference.

```
Difference % = |counted − system| / system × 100
```

Tolerance by class:

| Class | Tolerance | Rationale |
|-------|-----------|-----------|
| A | 0.5% | High value; small differences matter |
| B | 2% | Moderate |
| C | 5% | Low value; do not waste approver time |

**Without tolerance, every count difference becomes an approval queue.** With
it, small differences auto-approve and large ones escalate for investigation —
which is correct, because a large difference on an A item is a **signal**, not
a rounding error.

Approval rules must also account for the **value at stake**, not just the
percentage. A 4% difference on a $2M item is a $80K adjustment.

## Principle 6: Rotation prevents a coverage illusion

Counting the same subinventory every month by the same person creates two
problems:

1. **Blind spots** — problem items elsewhere are never counted.
2. **Independence loss** — the counter becomes invested in their own accuracy.

Good practice:

- Partition counts **by subinventory**, rotating the assignment.
- Rotate the **counter**, not just the location.
- Vary the **time of day** of counts — shrinkage often follows predictable
  patterns that a fixed schedule would miss.

```
Week 1: Raw Materials      (Counter A)
Week 2: WIP               (Counter B)
Week 3: Finished Goods    (Counter C)
Week 4: Returnable packaging (Counter A)
```

## Principle 7: The count must not be the whole fix

Cycle counting measures accuracy. It does not cause it.

The measurement loop only works if a discrepancy produces a **cause**:

```
Count → discrepancy → tolerance check → approval
                                      ↓
                              ROOT CAUSE CODE (mandatory)
                                      ↓
                              Process fix (the actual prevention)
```

**Root-cause coding is the step most programmes omit, and it is the step that
actually prevents recurrence.** Without it you count forever and learn nothing.
Common causes worth coding:

| Code | Cause | Typical fix |
|------|-------|-------------|
| `TRANS_ERR` | Transaction entered wrong | Retrain; tighten approval |
| `UNREC_SHIP` | Shipment not recorded | Barcode at despatch |
| `DAMAGE` | Damage not written off | Scrap procedure review |
| `CYCLE_SHRINK` | Unrecorded removal | Access control, camera coverage |
| `MISCNT` | Miscount | Retrain counter |
| `LOC_ERR` | Wrong location | Location validation |

If 60% of discrepancies code as `CYCLE_SHRINK`, you have found a security
problem, not a counting problem. Counting more will not fix it.

## Principle 8: Scanner capability changes the cost model

Manual counts are labour-bound:

```
Manual count cost = Items × Seconds per item × Labour rate
                   = 500 items × 45 sec × $0.35 = ~$2,190 per session
```

Barcode scanning removes the transcription step:

```
Scanned count cost = Items × 8 sec + scanner amortisation
                   = 500 × 8 sec × $0.35 ≈ $390 per session
```

Roughly **5× cheaper**, and — more importantly — it removes the transcription
error that causes `MISCNT` discrepancies in the first place. The investment is
justified by accuracy, not only labour.

## Principle 9: Accuracy should be a measured, trending metric

```
Inventory accuracy % = (SKUs with zero variance / SKUs counted) × 100
```

Track it by ABC class, monthly, with a target per class (A: 98%, B: 95%,
C: 90%). A programme that cannot show the trend improving has no business case,
no matter how much counting was performed.

## Diagnostic Order

1. When did the discrepancy occur? (Cycle counting bounds this.)
2. Which items? (ABC, plus movement as a second dimension.)
3. What value is at stake? (Drives frequency and tolerance.)
4. What caused it? (Root-cause coding — not optional.)
5. Who counts? (Rotate for coverage and independence.)
6. What happens after the count? (Tolerance, approval, cause code.)

## Anti-Patterns

- Continuing annual counts and calling them a control.
- Counting every item with the same frequency.
- Using pure ABC and ignoring movement.
- Auto-approving all differences, or escalating all of them.
- Counting without mandatory root-cause coding.
- Fixing the count process when the cause was shrinkage.
- Buying scanners justified only on labour savings.

## Summary

The $2M annual discrepancy was not a counting failure — it was a detection
failure. Cycle counting bounds the loss window so discrepancies are found small
and recent; ABC plus movement directs effort where value and risk are; tolerance
by class keeps the approval queue honest; and mandatory root-cause coding turns
measurement into prevention. Scanning pays for itself on accuracy first and
labour second.