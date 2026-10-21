# Model Training Pipelines — Step by Step

## Step 1. List the stages
Write the six names in order: ingest, validate, transform, train,
evaluate, register. Run PipelineDag and confirm the observed order
string `ingest->validate->transform->train->evaluate->register` with
gate_pass=true and stages=6.

## Step 2. Break the gate on purpose
Flip the validate entry to false in the demo map and rerun mentally:
transform must not execute. This is the behavior to assert in a real
orchestrator: downstream stages require an explicit pass record.

## Step 3. Validate a column by hand
Column of 10 with 3 nulls: null rate = 3/10 = 0.3. Run DataValidation
and confirm n=10, nulls=3, null_rate=0.3, threshold=0.25,
drift_flag=true, min=1.0, max=13.0, schema_ok=true.

## Step 4. Prove seed determinism
Run DeterministicRetrain and confirm run1 equals run2 ([2, 6, 3, 1, 4,
0, 7, 5]) with same_seed_equal=true, while seed 7 differs. Change the
seed to 99, predict that run1/run2 still match each other, and verify.

## Step 5. Write a tracking record
For the config `lr=0.01|depth=6|seed=42|data=v3` (hash -1652323048),
draft the full run record: params, metrics, code hash, data hash, seed,
timestamps. Check that removing any one field breaks reproducibility.

## Step 6. Simulate a drift response
Raise the demo null rate by adding a fourth null (4/10 = 0.4). Confirm
the flag stays tripped and write the on-call action: page data owner,
halt promotion, file the incident with the dataset version.

## Step 7. Register a fake artifact
Assign version `model:v7`, attach the tracking record, mark it
candidate (not production). State the promotion rule it must pass
before serving traffic.
