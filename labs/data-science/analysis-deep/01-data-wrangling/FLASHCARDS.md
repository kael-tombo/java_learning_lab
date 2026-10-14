# Data Wrangling - Flashcards

## Q1. What distinguishes MCAR, MAR, MNAR?

A: MCAR: missingness independent of all data. MAR: depends only on observed
data. MNAR: depends on the missing value itself. The mechanism picks the fix.

## Q2. When is listwise deletion unbiased?

A: Only under MCAR. Under MAR/MNAR, deletion selects a subpopulation and
biases estimates.

## Q3. What does mean imputation preserve, and what does it damage?

A: Preserves the mean; shrinks variance (roughly by the filled fraction) and
understates uncertainty.

## Q4. Why test doubles with Double.isNaN instead of ==?

A: NaN is unequal to everything including itself, so `v == Double.NaN` is
always false.

## Q5. What is a dedup key?

A: The column set declaring row identity, e.g. (customer_id, order_date).
Rows sharing a key are the same event recorded twice.

## Q6. Why dedup before imputing?

A: Duplicates would overweight the fitted fill value (e.g. the mean).

## Q7. State the Tukey fence rule.

A: Flag values outside [Q1 - 1.5 x IQR, Q3 + 1.5 x IQR]. Example bounds:
[10.375, 17.375] for the lab data.

## Q8. What is masking in z-score screening?

A: A huge outlier inflates the sd, shrinking its own z-score and possibly
escaping the screen. The IQR rule resists this.

## Q9. Why trim strings before parsing?

A: To distinguish blanks from bad characters and sentinels, giving each
reject a precise reason.

## Q10. What are the coercion receipts?

A: parsed = 4, rejected = 3, sum = 56.5 on the lab inputs; 4 + 3 = 7
reconciles every input.

## Q11. When is forward-fill valid?

A: Only for ordered data where persistence is plausible, with a cap on gap
length; never for cross-sectional rows.

## Q12. What must a cleaning run record?

A: The rule used, rows affected, fill values, fence bounds, and
before/after summaries - the audit ledger.

## Q13. Median or mean for income fills?

A: Median - income is right-skewed, and the mean follows the tail.

## Q14. What does Anscombe 1973 warn wranglers about?

A: Identical summary statistics can hide different shapes (including
outlier-driven ones), so inspect data, not just its mean.
