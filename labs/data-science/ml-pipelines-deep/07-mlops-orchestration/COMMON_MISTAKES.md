# MLOps Orchestration - Common Mistakes

1. Retrying non-idempotent tasks, duplicating side effects on every retry.
   - Fix: key writes by run id; gate side effects behind promotion flags.
2. Uncapped backoff without jitter, synchronizing retry storms.
   - Fix: cap delays and spread retries so dependents recover.
3. Retrying validation failures that will never pass instead of failing fast.
   - Fix: classify errors; retry transient ones, stop on deterministic ones.
4. Unpinned dependencies, so reruns diverge and backfills cannot reproduce history.
   - Fix: lock files plus recorded seeds, commits, and data versions.
5. Promoting on overall lift while a slice regresses.
   - Fix: require per-slice no-regression bars as a conjunction.
6. Backfilling into live paths instead of versioned outputs.
   - Fix: replay into versioned paths; switch consumers explicitly.
7. One shared queue where backfills starve scheduled runs.
   - Fix: separate queues with capped backfill concurrency.
8. Missing lineage pointers, leaving incidents without a reproducible run record.
    - Fix: every run records data, code, parameters, and environment.
9. Scheduling retraining on wall-clock time while data lands late.
    - Fix: gate the run on partition arrival (event trigger) with cron as fallback.
10. Letting one slow partition serialize the whole training stage.
    - Fix: shard by partition with per-shard timeouts and independent retries.
11. Storing parameters in chat logs instead of the run record.
    - Fix: every run writes its full parameter string into lineage automatically.
12. Promoting from a notebook run that never passed through gates.
    - Fix: only DAG-produced artifacts with green gates are promotable.
13. Backfilling with current code instead of the fixed version under test.
    - Fix: pin the code version per backfill; record it in the run fingerprint.
14. Alerting on run failure to everyone instead of the pipeline owner.
    - Fix: route run pages to owners; broadcast only promotion blocks.
15. Keeping zombie schedules after migration to event triggers.
    - Fix: inventory triggers quarterly; delete each schedule with a recorded reason.
16. Testing gates on the training set instead of a held-out evaluation set.
    - Fix: freeze the evaluation set; gate comparisons run only against it.
   - Fix: every run records data, code, parameters, and environment.

## Review habit
- After each incident, ask which gate, pin, or queue rule would have prevented it.
