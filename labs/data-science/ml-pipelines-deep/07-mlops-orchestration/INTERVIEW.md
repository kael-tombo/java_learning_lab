# MLOps Orchestration - Interview Questions

1. Why model pipelines as DAGs?
   - Dependencies order execution; branches parallelize; acyclicity guarantees a valid order.
2. What does idempotence buy a retried task?
   - Safe reruns with identical outputs keyed by run id instead of duplicates.
3. How does capped exponential backoff behave?
   - Waits double per attempt up to a cap; jitter desynchronizes retries across tasks.
4. Cron versus event triggers?
   - Fixed cadence versus reacting to new data or signals; most systems combine both.
5. What is artifact lineage?
   - Pointers to data version, code commit, parameters, and environment per run.
6. What gates a promotion?
   - Data validation before training; overall lift plus per-slice no-regression before serving.
7. How do you backfill safely?
   - Replay windows in order into versioned outputs without touching live paths.
8. Rerun diverges from the original: likely cause?
   - Unpinned dependency or unrecorded seed changing results silently.
9. Why separate queues for backfill?
   - Unbounded replays starve scheduled runs on a shared queue.
10. Which errors should never retry?
    - Deterministic validation failures; retry transient dependency errors only.
11. How do you bound retraining staleness under each trigger?
    - Cron by period plus duration; events by detection delay; run both.
12. What makes a promotion record complete?
    - Who, when, lineage pointer, and the gate table snapshot that passed.
13. How do you test backfill before a full replay?
    - One window first into versioned paths, then the range after it verifies.
14. When is a slice exception to a gate veto acceptable?
    - Documented explicitly with owner sign-off, never silent; the veto is default.
15. How do you detect zombie schedules?
    - Run creation sources show duplicate launches; inventory triggers regularly.
16. What proves rerun equality?
    - Matching fingerprints across runs with identical lineage pointers.
17. Where do side effects belong in a retried DAG?
    - Behind promotion flags only, never inside tasks that retry.

## How to answer
- Describe the mechanism, state the invariant, then give the incident it prevents.
