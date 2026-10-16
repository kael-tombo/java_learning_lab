# MLOps Orchestration - Architecture

## Components
- Scheduler: launches runs on cron or event triggers and tracks run state.
- DAG runner: executes tasks in dependency order with parallelism for branches.
- Artifact store: versions datasets, models, and metrics with lineage pointers.
- Gate evaluator: runs data-validation and metric-gated promotion checks.
- Secret and config service: injects credentials and environment pins per run.

## Data flow
- Trigger -> run record -> task execution -> artifact writes -> gate evaluation -> promotion record.
- Every write carries data version, code commit, parameters, and environment pin.
- Failed gates halt the run and leave production routing unchanged.

## State
- Run store holds status per task for resume and audit.
- Idempotent tasks make resume safe: completed steps are skipped or rewritten identically.
- Backfill runs reuse the same DAG with a window parameter and versioned outputs.

## Scaling
- Parallel branches and sharded training data scale throughput; the scheduler itself stays light.
- Retries with capped backoff bound load during dependency outages.
- Separate queues for scheduled, event, and backfill runs prevent starvation.

## Trigger routing
- Cron entries own steady retraining; event subscriptions own arrivals and alerts.
- Each trigger type lands in its own queue so bursts never block cadence.
- Trigger definitions live in version control beside the DAG they start.

## Promotion path
- Staging promotion runs full gates on a traffic mirror before production routing.
- Production promotion flips routing only; artifacts are already in place.
- Every promotion writes who, when, lineage pointer, and gate table snapshot.

## Backfill lane
- Backfill runs carry window parameters through the identical DAG code.
- Outputs land in versioned paths namespaced by run id and window.
- Consumers switch explicitly; no silent overwrite of live tables occurs.

## Failure containment
- Task timeouts kill hung steps so one partition cannot stall the run.
- Failed runs release locks and leave production routing untouched.
- Poison partitions quarantine to a side path with owner notification.
