# Model Training Pipelines — Interview

## Q: Walk me through the stages and why each exists.
A: Ingest pins a dataset version; validate blocks bad data; transform
builds features deterministically; train fits parameters; evaluate
scores held-out data; register stores the model with lineage. The demo
runs all six in order with gate_pass=true.

## Q: How do you catch data problems before training?
A: Schema checks (columns, types, ranges) plus statistical checks
(null rates vs thresholds). Demo: 10-value column, 3 nulls, rate 0.3
over a 0.25 threshold trips drift_flag while the [1.0, 13.0] range
passes schema. The gate halts the run.

## Q: How do you make retraining reproducible?
A: Pin seeds, code versions, and data versions; record all of them.
Demo: seed 42 reproduces [2, 6, 3, 1, 4, 0, 7, 5]; config string
hashes to -1652323048 as the integrity pointer.

## Q: What belongs in an experiment record?
A: Params, metrics, code hash, data hash, seed, timestamps, and the
output artifact version. Any missing field makes the run
unauditable by definition.

## Q: What is the registry's promotion rule?
A: Candidates register with evaluation scores; promotion to production
requires passing recorded thresholds plus human or policy approval.
Promotion is a pointer update, never a blob edit.

## Q: Retrain metrics moved with no code change —bug or signal?
A: Usually signal: data drift. Compare tracked data hashes and
validation histories across runs before touching hyperparameters.

## Q: Why keep failed runs?
A: They record what was tried with which data and code, preventing
repeated dead ends and documenting the search for review.
