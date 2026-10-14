# Data Wrangling - Exercises

All tasks run on the plain JDK. Verify each answer by executing your code;
expected values below come from verified reference runs.

## 1. Reproduce the imputation

Rewrite the mean-fill for `{2, 4, NaN, 8, 10}` from scratch using streams.
Expect: missing = 1, mean = 6.0, imputed `[2.0, 4.0, 6.0, 8.0, 10.0]`.

## 2. Median-fill challenge

Median-fill `{30, 5, NaN, 7, 9}`. Sorted observed = {5, 7, 9, 30}, median =
(7 + 9)/2 = 8.0, so expect imputed `[30.0, 5.0, 8.0, 7.0, 9.0]`.

## 3. Forward-fill

Forward-fill `{NaN, 4.0, NaN, NaN, 10.0}` carrying the last seen value; a
leading NaN has nothing to carry, so leave it missing. Expect
`[NaN, 4.0, 4.0, 4.0, 10.0]` and report filled = 2, still-missing = 1.

## 4. Outlier screen drill

Screen `{12, 14, 13, 15, 14, 13, 12, 15, 14, 60}` with both rules. Expect
Q1 = 13.0, Q3 = 14.75, IQR = 1.75, fences [10.375, 17.375], IQR flags
[60.0]; mean = 18.2, sample sd = 14.72563901650602, z of 60 = 2.84, so the
z > 2 screen flags [60.0] as well.

## 5. Key redesign

The dedup table gains an `amount` column where `c7|2026-01-05` rows differ
(12.50 vs 12.55). Rebuild with key `(customer, date, amount)` and show the
unique count rises from 3 to 4. Write one paragraph on which key is correct
for a revenue sum.

## 6. Coercion ledger

Extend the parser to accept `"1e3"` (parseDouble handles it: 1000.0) while
still rejecting `"12,000"`. Report the new parsed/rejected counts on the
seven original strings plus these two.

## 7. MNAR spotter

A survey column is missing for 40% of rows, and missingness rises with age,
which is recorded. Classify (MAR - depends on observed age) and state the
fix: condition on age or impute within age bands, not a global mean.

## 8. Receipts check

Write a validator asserting in = kept + removed + rejected on the dedup and
coercion examples (5 = 3 + 2 + 0; 7 = 4 + 0 + 3). Fail loudly on mismatch.
