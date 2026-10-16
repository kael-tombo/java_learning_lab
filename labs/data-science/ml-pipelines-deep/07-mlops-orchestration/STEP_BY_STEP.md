# MLOps Orchestration - Step by Step

1. Draw the DAG: ingest, validate, train, evaluate, promote, with edges.
   - Every edge is a dependency the runner enforces; branches run in parallel.
2. Attach triggers: cron for cadence plus events for new data or alerts.
   - Cadence bounds staleness; events react to arrivals between ticks.
3. Make each task idempotent, keyed by run id and partition.
   - Reruns overwrite identical outputs instead of duplicating them.
4. Add retries with capped exponential backoff for transient steps only.
   - Validation failures fail fast; only flaky dependencies retry.
5. Pin dependencies and record seeds, commits, and data versions per run.
   - Unpinned environments make reruns diverge silently.
6. Add data-validation gates before training and metric gates before promotion.
   - Failed gates stop the run and keep current production routing untouched.
7. Test backfill on one window before replaying a full range.
   - Replays write to versioned outputs, never into live paths.
8. Promote only on green gates; record the lineage pointer that went live.
   - The promotion record names who, when, and which pointer shipped.
9. Separate queues for scheduled, event, and backfill lanes with capped replay concurrency.
    - Fairness between live work and history repair is structural, not hoped for.
10. Add staging promotion with full gates on mirrored traffic before production routing.
    - Production flips only after staging gates and owner sign-off both pass.
11. Inventory triggers quarterly and delete zombie schedules with recorded reasons.
    - Each cadence has exactly one owner and one firing mechanism.
12. Freeze the evaluation set with a stored hash; gates compare only against it.
    - Set changes are reviewed events with re-baselined bars, never silent edits.
13. Require second approval for production promotion and record the approver.
    - Emergency promotions re-gate within one cycle or roll back automatically.
14. Drill gate-blocked promotion and backfill replay on staging every quarter.
    - Failed gates must stop runs; replays must stay in versioned paths.

## Launch checklist
- DAG drawn, triggers owned, tasks idempotent, backoff capped, pins recorded.
- Gates green on the frozen set, queues separated, backfill tested on one window.
- Promotion record complete: who, when, lineage pointer, gate snapshot.
- A missing item blocks launch; waivers expire in one cycle with an owner.

## Done when
- A rerun reproduces its artifacts, a failed gate blocks promotion, and backfill is routine.
