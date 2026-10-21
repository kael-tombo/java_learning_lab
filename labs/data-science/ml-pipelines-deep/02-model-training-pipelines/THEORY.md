# Model Training Pipelines — Theoretical Foundation

## Core Concept

A training pipeline turns raw data into a registered model through a
fixed DAG — ingest → validate → transform → train → evaluate → register —
where every stage's inputs, code version, and outputs are recorded. The
pipeline exists for one reason: **the same inputs must always produce the
same model**, so results are auditable, regressions are bisectable, and
retraining is a rerun rather than a research project.

## Stage Contracts

1. **Ingest**: snapshot input data with an immutable identifier (content
   hash or versioned snapshot id). Mutable "latest" pointers make reruns
   unrepeatable — the snapshot is the unit of reproducibility.
2. **Validate**: schema, null-rate, and distribution checks *gate* the run.
   A failed check stops the pipeline before training burns compute on bad
   data. Checks and thresholds are versioned with the pipeline, not tribal
   knowledge.
3. **Transform**: feature logic applied identically to train and future
   serve data. The transform artifact (parameters like scalers' means, plus
   code version) is saved — a model without its transform is undeployable.
4. **Train**: pinned code, pinned hyperparameters, pinned seed. Seeds
   don't make training *good*; they make it *repeatable*.
5. **Evaluate**: fixed held-out split (or versioned fold assignments) and
   recorded metrics. Changing the test set between runs invalidates every
   comparison.
6. **Register**: the model artifact plus its full lineage (data snapshot
   id, code version, params, metrics) enters the registry. Promotion
   (staging → production) reads lineage, not filenames.

## Determinism Discipline

Nondeterminism creeps in through: unseeded RNGs, thread-racy reductions
(floating-point summation order), unordered map iteration feeding
features, timestamp-based splits, and unpinned dependencies. The pipeline
counters with seeds, pinned versions, sorted/canonical orderings, and
content hashes. Total bitwise reproducibility across machines is often
unreachable (BLAS threading, GPU kernels); aim for *decision*
reproducibility — same data + same code ⇒ same metrics within tolerance,
same promotion decision always.

## Retraining Triggers (not Schedules)

Retrain on: schedule plus data drift beyond threshold, performance decay
on live labels, new labeled data crossing a volume bar, or upstream schema
change. "Retrain nightly because we can" wastes compute and churns
production models for noise; every trigger is a monitored condition with
an owner.

## Key Invariants

1. Same inputs + same code ⇒ same model (within stated tolerance).
2. No stage runs on failed validation.
3. Every artifact carries lineage (data id, code version, params).
4. Test data is fixed across compared runs.
5. Promotion reads the registry, never a filename.
