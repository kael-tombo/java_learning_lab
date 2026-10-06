# Lab 04: Supply Chain (Cycle Counting) — Flashcards

## Why Cycle Counting

---
**Q**: Why is an annual count not a control?
**A**: It measures accuracy once per year. Loss accumulates unseen and the causing transactions are too old to investigate.

---
**Q**: Real value of cycle counting?
**A**: Bounding the loss window. Findings arrive small and recent, while the transactions are still traceable.

---
**Q**: Expected loss between counts?
**A**: `disc_rate × value throughput × count interval`. Frequency directly bounds it.

---
**Q**: Bounded loss — annual vs monthly, $500K/mo at 2%?
**A**: Annual = $120K/yr per cohort. Monthly = $10K. ~12× reduction.

---
**Q**: Does cycle counting give 100% accuracy?
**A**: No, and it isn't aiming for that. It aims to detect and code every discrepancy quickly.

---

## Classification

---
**Q**: Metric for ABC?
**A**: Annual dollar usage. Not unit count, item value, or volume.

---
**Q**: Standard cutoffs?
**A**: A = top 80% of value, B = 80–95%, C = final 5%.

---
**Q**: Limitation of pure ABC?
**A**: Ignores movement. Mid-value, high-transaction items get under-protected.

---
**Q**: Two-dimensional alternative?
**A**: Value × movement 2×2 matrix. High value/high movement = count monthly; low value/high movement = count quarterly.

---
**Q**: Worst under-protected group?
**A**: Low value, high movement — small, easy to remove, high shrinkage rate.

---

## Frequency

---
**Q**: Derive max count interval.
**A**: `Materiality / (disc_rate × monthly value)`.

---
**Q**: $500K/mo, 2%, $50K materiality → interval?
**A**: 5 months. Monthly counting is conservative here — say so explicitly.

---
**Q**: Can pure ABC "A = monthly" miss an item?
**A**: Yes. $500K/mo at 8% discrepancy with $10K materiality needs weekly counting.

---
**Q**: Coverage metric?
**A**: SKUs counted in period / total active SKUs. ABC schedule gives ~160%/yr — that's by design, not over-counting.

---

## Scheduling

---
**Q**: Rotate what?
**A**: Location, counter, AND time of day. Shrinkage follows patterns a fixed schedule would miss.

---
**Q**: Why rotate the counter?
**A**: Coverage and independence — a fixed counter becomes invested in their own numbers.

---
**Q**: Partition counts by?
**A**: Subinventory, on a rotation anchor.

---

## Tolerance

---
**Q**: Tolerances by class?
**A**: A 0.5%, B 2%, C 5%.

---
**Q**: Why a value cap as well as a percentage?
**A**: 5% of $2M is $100K — a management decision. Percentage alone hides magnitude.

---
**Q**: Escalate condition?
**A**: `variance_pct > tolerance OR variance_value > max_adj_value`.

---
**Q**: Risk of wide tolerance?
**A**: Real discrepancies inside the band are auto-approved and invisible. With 3% true rate and 5% tolerance, the whole 0–5% band is missed.

---
**Q**: Why tolerance at all — why not escalate everything?
**A**: Without it, 150 escalations/year destroys approver attention. Tolerance protects focus on cases that matter.

---

## Capture

---
**Q**: Barcode → what API?
**A**: Resolve via `MTL_SECONDARY_LABELS`, record via the cycle count supplies table.

---
**Q**: Scanner saving vs manual?
**A**: ~5.6× on labour (45s/item → 8s/item). But the bigger win is eliminating ~2% transcription error.

---
**Q**: Justify scanners on what first?
**A**: Accuracy (removing false discrepancies), not labour. Labour is the secondary case.

---
**Q**: Unknown barcode behaviour?
**A**: Raise an error. Never silently skip — a skipped scan is an uncounted item.

---

## Root Cause Coding

---
**Q**: Mandatory?
**A**: Yes. Enforce with `NOT NULL` + a check constraint, not convention.

---
**Q**: Cause codes?
**A**: `TRANS_ERR`, `UNREC_SHIP`, `DAMAGE`, `CYCLE_SHRINK`, `MISCNT`, `LOC_ERR`, `OTHER`.

---
**Q**: Why is it the most important step?
**A**: It's the only step that prevents recurrence. Everything else is measurement.

---
**Q**: `CYCLE_SHRINK` dominant means?
**A**: A security problem. Route to security with access controls. Counting cannot fix theft.

---
**Q**: Typical cause Pareto?
**A**: `UNREC_SHIP` ~60%, `CYCLE_SHRINK` ~25%, `TRANS_ERR` ~10%, rest ~5%.

---

## Accuracy

---
**Q**: Accuracy formula?
**A**: Zero-variance items / total counted × 100.

---
**Q**: Targets by class?
**A**: A 98%, B 95%, C 90%.

---
**Q**: Expect improvement in month 1?
**A**: No. Accuracy lags because the programme is still measuring. It rises once cause codes drive fixes.

---
**Q**: Success metric?
**A**: Accuracy trend and recovered loss. **Not** the number of counts performed.

---

## Quick Reference

| Task | Object |
|------|--------|
| Cost history | `MTL_TRANSACTION_ACCOUNT` |
| On-hand | `MTL_ON_HAND_TXN_QTY` |
| Transactions | `MTL_TRANSACTION_HISTORY` |
| Count API | `INV_CYCLE_COUNT_API.create_cycle_count_request` |
| Count records | `MTL_CYCLE_COUNT_SUPPLIES` |
| Barcode | `MTL_SECONDARY_LABELS` |
| Approval API | `AP_HOLDS_PKG.release_hold` |
| Concurrent requests | `FND_CONCURRENT_REQUESTS` |

---

## Business Case Numbers

| Metric | Value |
|--------|-------|
| Annual expected loss (2% of $500M usage) | **$10M** |
| A-item detection improvement (annual → monthly) | ~12× |
| Scanner labour reduction | ~5.6× |
| Manual transcription error rate | 1–3% per line |
| Weighted annual coverage | ~160% of SKUs |

Present **recovered loss**, not cost saving. Nobody funds counting because it
saves counting labour.

---

## Anti-Patterns

1. Annual counts presented as a control.
2. Uniform frequency for all items.
3. Pure ABC without movement.
4. Percentage-only tolerance.
5. Counting with no mandatory cause code.
6. Treating shrinkage as a counting problem.
7. Reporting counts performed as success.

---

## Study Tips
1. Explain bounded loss in one sentence with a number.
2. Derive a count interval out loud, showing units.
3. Recall why percentage-only tolerance is dangerous.
4. State the threshold value at which you stop counting and start securing.