# Data Wrangling - Worked Example

## Dataset

Column `col = {2.0, 4.0, NaN, 8.0, 10.0}`, five cells, one missing.

## Step 1 - Count missingness

Scan the column: `Double.isNaN` is true once.
Result: n = 5, missing = 1, observed = 4 (missing rate 20%).

## Step 2 - Fit the fill value on observed cells only

Sum of observed = 2 + 4 + 8 + 10 = 24. Count = 4. Mean = 24 / 4 = 6.0.
Sorted observed = {2, 4, 8, 10}, median = (4 + 8) / 2 = 6.0.
Here mean and median agree, so either fill is defensible.

## Step 3 - Fill and verify

Imputed column = {2.0, 4.0, 6.0, 8.0, 10.0}.
Recompute: no NaN remains, new mean = 30 / 5 = 6.0, unchanged.

## Step 4 - Dedup check on the companion table

Five order rows with keys `c7|2026-01-05` (twice), `c7|2026-01-06`,
`c9|2026-01-05` (twice). Unique keys = 3, duplicates removed = 2.

## Step 5 - Outlier screen on {12, 14, 13, 15, 14, 13, 12, 15, 14, 60}

Sorted: {12, 12, 13, 13, 14, 14, 14, 15, 15, 60}.
Q1 = 13.0, Q3 = 14.75, IQR = 1.75.
Fences: [13 - 1.5 x 1.75, 14.75 + 1.5 x 1.75] = [10.375, 17.375].
Only 60.0 falls outside, so the IQR flags are {60.0}.
Mean = 18.2, sample sd = 14.72563901650602; |60 - 18.2| / 14.73 = 2.84 > 2,
so the z > 2 screen agrees here.

## Step 6 - Coercion tally

Inputs {"12", " 45 ", "3x", "", "7.5", "N/A", "-8"} give parsed = 4
(12 + 45 + 7.5 - 8 = 56.5) and rejected = 3 with reasons logged.

## Step 7 - Validate the run

Reconcile: dedup 5 in = 3 kept + 2 removed; coercion 7 in = 4 parsed +
3 rejected. Recompute the imputed column mean (30 / 5 = 6.0, unchanged from
the observed 6.0) and confirm zero unexplained NaN. Any mismatch blocks
downstream use.

## What changes with different data

If the outlier were 16 instead of 60, fences [10.375, 17.375] would flag
nothing and both screens would stay silent - correct behavior, since 16 sits
with the bulk. If two cells were missing, the same fill rule applies but the
variance-shrinkage warning in MATH_FOUNDATION.md gets louder.
