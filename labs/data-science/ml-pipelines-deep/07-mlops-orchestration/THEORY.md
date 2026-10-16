# MLOps Orchestration - Theory

Orchestration runs the chain of steps that turns new data into a validated, promoted model.

## DAG shape
- Work is a directed acyclic graph: nodes are tasks (ingest, validate, train, evaluate, promote), edges are dependencies.
- The scheduler runs a task once its parents succeed; independent branches run in parallel.
- Acyclicity guarantees termination ordering; cycles must be broken with explicit iteration constructs.

## Retries and idempotence
- Transient failures retry with backoff: delay grows per attempt up to a cap, often with jitter to avoid synchronized retries.
- Tasks must be idempotent: rerunning with the same inputs and run id writes the same outputs, so retries and backfills are safe.
- Non-idempotent side effects (sending traffic, charging) are gated behind explicit promotion steps.

## Scheduling and backfill
- Cron triggers run on a fixed cadence and suit regular retraining.
- Event triggers run when something happens: new partition lands, data-quality check completes, drift alert fires.
- Backfill replays a date range through the DAG after a bug fix or schema change, writing versioned outputs.

## Lineage and reproducibility
- Artifact lineage records pointers to the data version, code commit, parameters, and environment for every run.
- Reproducibility requires pinned dependencies and recorded seeds; unpinned environments make reruns diverge silently.
- Promotion is metric-gated: overall lift plus per-slice no-regression checks must pass before serving traffic.

## CI for ML
- Data-validation gates check schema, ranges, and null rates before expensive training starts.
- Model gates compare candidate metrics against production on a fixed evaluation set.
- Failed gates stop the pipeline and keep the current production model untouched.
