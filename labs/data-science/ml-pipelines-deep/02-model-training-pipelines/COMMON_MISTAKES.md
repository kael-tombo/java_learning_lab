# Model Training Pipelines — Common Mistakes

## 1. Training on unvalidated data
Skipping or softening the validate gate lets a 30%-null column like the
demo's straight into the model. Gates must halt the run, not warn.

## 2. Unseeded shuffles
An unrecorded shuffle makes every rerun a different experiment. The
demo's seed-42 repeatability ([2, 6, 3, 1, 4, 0, 7, 5] twice) is the
baseline; anything less is not an experiment.

## 3. Mutable data paths
Reading from "latest.csv" instead of a versioned snapshot means reruns
measure different data. Pin dataset versions with hashes at ingest.

## 4. Incomplete tracking records
Logging metrics without code and data hashes produces numbers nobody
can reproduce or audit. All five fields (params, metrics, code hash,
data hash, seed) are mandatory per run.

## 5. Validating samples instead of snapshots
Checks on a hand-exported sample can pass while the pinned snapshot
fails. Always validate the exact version the pipeline will train on.

## 6. Tuning against the test set
Repeatedly adjusting based on test scores leaks the test set into
training decisions. Keep a validation split for iteration and touch
test once per candidate (see lab 03).

## 7. Registering everything as production
Without candidate/production status separation, serving may resolve an
arbitrary version. Promotion is an explicit, recorded decision.

## 8. Retrying non-idempotent stages
Stages with side effects (unversioned writes, random unseeded draws)
diverge on retry. Make every stage a pure function of versioned inputs
plus the recorded seed.

## 9. Confusing fast with healthy
A pipeline that always passes may have thresholds set so loose the
gate cannot trip — the demo flag at 0.25 would never fire at 0.9.
Review gate trip history quarterly: a gate that never trips is either
unnecessary or miscalibrated, and both deserve an explicit decision.
