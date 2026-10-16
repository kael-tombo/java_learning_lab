# MLOps Orchestration - Debugging

## Retries hammer a dependency
- Cause: uncapped backoff with many parallel tasks retrying in sync.
- Check: attempt counts and retry timestamps per task.
- Fix: cap delays, add jitter, and limit task parallelism.

## Rerun duplicates outputs
- Cause: task appends without run-id keying.
- Check: output paths for missing run or partition keys.
- Fix: key all writes by run id and partition; overwrite instead of append.

## Backfill starves live runs
- Cause: shared queue with unbounded backfill parallelism.
- Check: queue wait for scheduled runs during replays.
- Fix: separate queues and cap backfill concurrency.

## Promotion blocked unexpectedly
- Cause: slice regression hidden in overall lift.
- Check: per-slice gate table; find the failing segment.
- Fix: fix the slice (data or features) or document an explicit exception.

## Rerun diverges from original
- Cause: unpinned dependency or unrecorded seed changed underneath.
- Check: environment pins and seed records for both runs.
- Fix: pin and record everything; verify artifact hashes per stage.

## Late data stalls the schedule
- Cause: cron fires before the partition lands; validation waits or fails.
- Check: partition arrival timestamps against run start times.
- Fix: event trigger on arrival with cron as the fallback sweep.

## Notebook promotion bypass
- Cause: artifacts promoted outside the DAG skipped gates silently.
- Check: promotion record for its lineage pointer and gate table.
- Fix: allow promotion only from gated DAG runs; reject the rest.

## Zombie schedules double-train
- Cause: old cron entries survive migration and launch duplicate runs.
- Check: run creation sources during the overlap window.
- Fix: inventory and delete dead schedules; one trigger owns each cadence.

## Gate flakiness blocks good models
- Cause: evaluation-set leakage or nondeterministic scoring moves metrics.
- Check: gate verdicts across reruns with identical lineage fingerprints.
- Fix: freeze the set, pin seeds, and require verdict stability before blocking.
