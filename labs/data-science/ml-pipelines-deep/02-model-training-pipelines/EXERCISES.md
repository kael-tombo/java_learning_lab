# Model Training Pipelines — Exercises

## 1. Gate drill
In PipelineDag, set the validate entry to false. Predict the printed
order (stops before transform) and gate_pass (false). Edit, run, and
confirm. Then restore to true.

## 2. Threshold arithmetic
In DataValidation, change the threshold to 0.35. Predict drift_flag
(0.3 > 0.35 is false, so flag clears) and run to confirm. Write one
sentence on why thresholds are policy while the compute-compare-gate
mechanism is standard.

## 3. Extra null
Add a fourth null to the demo column (11 entries with 4 nulls gives
rate 0.3636...). Compute by hand first, then run and confirm the flag
and the new min/max.

## 4. Seed swap
In DeterministicRetrain, change both run1/run2 seeds to 99. Predict
that same_seed_equal stays true while the order itself changes. Run and
confirm, and record the new order.

## 5. Tracking record completeness
Take the config `lr=0.01|depth=6|seed=42|data=v3` and write the full
run record with params, metrics, code hash, data hash, seed, and
timestamps. Delete one field and explain exactly which reproducibility
question becomes unanswerable.

## 6. Stage contract design
Pick the transform stage and write its contract: inputs (dataset
version, transform version), outputs (feature matrix version), success
predicate (row count matches, null rates within bounds). State what a
retry does and why it is safe.

## 7. Threshold review drill
The demo gate trips at 0.25 with an observed 0.3 rate. Write the
quarterly review note: trips in the last 90 days, false-stop rate,
and whether 0.25 still matches the data owner's tolerance. A gate
without a review date is a guess that hardened into policy.
