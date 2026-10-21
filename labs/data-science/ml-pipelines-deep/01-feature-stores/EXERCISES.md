# Feature Stores — Exercises

## 1. As-of join by hand (pen and paper, then run)
History: (u1,10,1.0), (u1,20,2.0), (u1,30,3.0). Labels: (u1,25), (u1,30).
Write the expected join values before running PointInTimeJoin.
Expected: 2.0 and 3.0. Then add label (u1,9) and predict the output
before running: must be NO_FEATURE.

## 2. Leak detector
Modify the label loop to also compute a naive "latest regardless of
time" join. Assert the naive value >= as-of value on this dataset and
print both. Confirms the leak direction on monotone histories.

## 3. Skew alarm
Change the stale shift from 0.0 to 0.9 in ServingSkewCheck. Predict
maxdiff (0.1 per element, so 0.1), run, confirm. Then set an alert
threshold of 1e-9 and print SKEW vs OK.

## 4. TTL tuning
In BackfillTtl, set TTL to 60. Predict kept/dropped before running
(ages 90 drop; 50, 10, 5 keep: kept=3, dropped=1, coverage=0.75).
Run and confirm.

## 5. Version pinning drill
Extend the Feature record with a version field. Build two histories v1
and v2 with different values at the same ts. Write `asOfValue` variant
that filters by version. Show a model pinned to v1 is unaffected when
v2 rows are added.

## 6. Missing-data contract
For entity u2 at t=12 (no history), decide: impute with declared
default vs drop the row. Write down when each is correct and what
breaks if serving imputes differently from training.

## 7. Late-event drill
Insert a late row (u1,18,9.0) after the u1@25 training row was built.
Decide: does the existing row change (no — history is append-only and
the row already consumed ts<=25 state), and what does the next
materialization carry? Recompute the u1@25 value with the late row
present (still 2.0, since ts=20 remains the max <= 25) and state the
watermark rule you would file for rows later than one day.
