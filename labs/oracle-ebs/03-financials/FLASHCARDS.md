# Lab 03: Financials — Flashcards

## Diagnosis

---
**Q**: First step before changing any AP configuration?
**A**: Build a hold taxonomy — reason, invoice count, value at risk.

---
**Q**: What does 30% hold rate mean?
**A**: The control is firing that often. Either miscalibrated or the business genuinely disputes. Measurement distinguishes them.

---
**Q**: 30% holds that nobody can explain — what's the actual problem?
**A**: Not the rate. It's the absence of an explanation.

---
**Q**: Common hold types?
**A**: Price variance, quantity variance, terms mismatch, exchange rate, tax calculation, invalid supplier.

---
**Q**: Where does `AP_HOLDS_ALL` sit?
**A**: The hold record. `release_flag='N'` means currently held. Join `AP_HOLD_CODES` for readable reasons.

---

## Matching Rules

---
**Q**: Ordered vs received vs invoiced — which pair should match?
**A**: `invoiced ≈ received`. Comparing invoiced to ordered creates false holds on every short shipment.

---
**Q**: Supplier bills 97, PO says 100, 97 received. Why held?
**A**: Rule compares invoiced (97) to ordered (100). 3% variance, hold fired.

---
**Q**: Prefer rule correction or wider tolerance?
**A**: Rule correction. It makes the comparison correct instead of merely tolerable.

---
**Q**: When must the control still fire?
**A**: Over-invoicing — `invoiced > received` AND `invoiced > ordered`.

---
**Q**: Three-way match checks what?
**A**: PO, receipt, and invoice agree.

---

## Tolerances

---
**Q**: How should tolerances be derived?
**A**: From the measured variance distribution — set just above the noise band.

---
**Q**: Where in the cumulative distribution?
**A**: Where it first reaches ~97–98%.

---
**Q**: Why is 0% price tolerance wrong?
**A**: Rounding and rebate effects are real. ~99% false positives train users to ignore holds.

---
**Q**: Tolerance too wide (e.g. 40%)?
**A**: Matches real problems too. Fails the control's purpose and invites criticism.

---
**Q**: Normal model: tolerance ≈ μ + kσ. k=3 captures?
**A**: ~99.7%.

---
**Q**: Auditor-defensible wording?
**A**: "Tolerance set at the 97th percentile of observed variance, separating rounding/rebate effects from material discrepancies."

---

## Control Integrity

---
**Q**: Hold rate vs escape rate?
**A**: Hold rate = held/total. Escape rate = real discrepancies that passed/total.

---
**Q**: Why report both?
**A**: Hold rate can fall because the control was disabled. Escape rate distinguishes recalibration from removal.

---
**Q**: Good outcome?
**A**: Hold rate 30% → 8% **with** escape rate staying at 0%.

---
**Q**: Bad outcome?
**A**: Hold rate down, escape rate up. Investigate the over-invoice path.

---
**Q**: How do you prove the control survived?
**A**: Inject a deliberate 30% over-invoice; it must still hold. Test the control, not just the metric.

---

## Release and Workflow

---
**Q**: Why is mass hold release a SOX risk?
**A**: Converts a control into a rubber stamp.

---
**Q**: What makes automated release defensible?
**A**: Explicit narrow criteria + mandatory reason code + full audit trail + approved criteria.

---
**Q**: Can a release happen without a reason code?
**A**: No. Make `release_reason` `NOT NULL` at the database level so it's enforced, not just conventional.

---
**Q**: Why does workflow matter?
**A**: Hold latency is the fixable part. Routing turns invisible problems into assigned work.

---
**Q**: Why is supplier cycle time the better business metric?
**A**: It's what the supplier experiences. 5 day DPP + 12 days held = 17 effective days.

---

## Quick Reference

| Task | Object |
|------|--------|
| Hold records | `AP_HOLDS_ALL` (`release_flag='N'`) |
| Hold reason text | `AP_HOLD_CODES` |
| Invoice validation status | `AP_INVOICES_ALL.validation_status` |
| Quantity split | `AP_INVOICE_DISTRIBUTIONS_ALL` |
| Receipt quantities | `AP_RECEIPT_LINES_ALL` |
| PO quantities | `PO_LINES_ALL` |
| Release API | `AP_HOLDS_PKG.release_hold` |
| Supplier name | `AP_SUPPLIERS_ALL` |

---

## Priority Sequence

1. Taxonomy — measure.
2. Matching rule — fix semantics.
3. Tolerances — derive from data.
4. Control test — prove it still fires.
5. Batch release — with reason codes.
6. Workflow — cut resolution latency.
7. Dashboard — track hold **and** escape rate.

---

## Anti-Patterns

1. Mass-releasing holds to hit a target.
2. Widening tolerance instead of fixing the matching basis.
3. Setting tolerances without measuring the distribution.
4. Reporting hold rate without escape rate.
5. Releasing holds with no reason code because "it was obviously fine".

---

## Study Tips
1. Be able to explain the ordered/received/invoiced mismatch in one sentence.
2. Read a cumulative variance table and pick a tolerance out loud.
3. State both hold rate and escape rate whenever quoting hold numbers.
4. Recall the difference between recalibrating and disabling a control.