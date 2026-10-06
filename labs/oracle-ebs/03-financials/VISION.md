# Lab 03: Financials — Vision

## Where this lab takes you
From "30% of invoices are on hold" to a hold taxonomy, a matching-rule fix, and
a system where holds are exceptions rather than noise.

## The Arc
1. **Symptom** — 30% of invoices held, no clear reason given to AP.
2. **Measure** — build a hold taxonomy before changing anything.
3. **Diagnose** — matching against ordered vs received quantity.
4. **Tolerances** — why 0% price variance turns rounding into a hold.
5. **Fix** — matching rules and tolerances set from data, not guesses.
6. **Automate** — batch hold release with workflow notification.
7. **Prevent** — monitoring so hold rate is a tracked metric.

## Milestones (checkable)
- [ ] M1: Build a hold reason distribution query and rank by volume.
- [ ] M2: Explain why quantity variance fires when suppliers invoice delivered
      quantity against an ordered-quantity match.
- [ ] M3: Calculate what price variance tolerance the data actually supports.
- [ ] M4: Change matching rules and measure the effect on hold rate.
- [ ] M5: Write a batch hold release program with a reason-code audit trail.
- [ ] M6: Add workflow notification for held invoices.
- [ ] M7: Prove the hold rate dropped without raising control weakness.
- [ ] M8: Design a dashboard alert for hold-rate regression.

## Anti-Goals
- Mass-releasing holds without understanding the distribution.
- Setting tolerances arbitrarily instead of deriving them from variance data.
- Eliminating holds entirely — holds are a control, not a bug.
- Fixing the tolerance while leaving the quantity matching rule wrong.

## The one-sentence thesis
A hold rate is a signal — 30% holds means the matching rules disagree with how
the business actually trades, and the fix is alignment, not suppression.