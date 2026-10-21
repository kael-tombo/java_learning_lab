# Model Training Pipelines — Architecture

## Components
1. Orchestrator: executes the DAG in order, enforces gates, retries
   idempotent stages.
2. Dataset store: immutable versioned snapshots with hashes.
3. Transform registry: versioned feature code (shared with lab 01).
4. Trainer: fits models from (features, config, seed).
5. Evaluator: fixed metric suite on held-out data.
6. Model registry: versioned models plus lineage records.
7. Experiment tracker: params/metrics/hashes per run, queryable.

## Data flow
Trigger -> ingest (dataset v) -> validate (gate) -> transform
(features) -> train (params) -> evaluate (scores) -> register
(model v + lineage). The tracker observes every stage.

## Key interfaces
- `runPipeline(trigger, datasetVersion)`: returns run record.
- `validate(dataset)`: returns pass/fail plus per-check details.
- `train(features, config, seed)`: returns params + metrics.
- `register(model, lineage)`: returns immutable model version.

## Ordering guarantees
Stages run in topological order; transform never sees unvalidated
data because the runner halts at a failed gate. Retries are safe only
for stages with deterministic outputs from versioned inputs.

## Scaling notes
Ingest and transform scale with data volume (partitioned batch work);
training scales with model size times data passes; evaluation is one
bounded pass. The tracker and registries are small metadata services
that must stay available even when compute stages queue.

## Worked gate example
Dataset v41 arrives with null rate 0.3 over the 0.25 policy: validate
emits fail with per-check detail, the runner halts before transform,
the tracker records a stopped run, and the owner is paged with the
dataset version. No model, no metrics, no ambiguity — the halt is the
correct output of the stage.
