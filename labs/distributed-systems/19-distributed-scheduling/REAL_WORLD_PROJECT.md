# Distributed Scheduling - Real World Project

## Project: Migrating a Cron Fleet to a Distributed Scheduler

### Objective
Replace a single-instance cron host running dozens of jobs with a horizontally scaled,
leaderless scheduler — with per-job misfire policy, stuck-run recovery, and an audit trail
that makes "did this job run?" answerable in seconds.

### Why This Matters
Single-instance cron has two failure modes that both look identical to the business: the host
goes down and nothing runs, or a deploy causes a double fire. Neither is visible without an
audit trail, which cron does not have.

### Architecture Overview
```
  N scheduler instances (no leader)
        │ poll every 10s
        ▼
  Postgres jobs table ── atomic claim ──▶ worker execution
        │                                    │
        │ history (job_run rows)             └─ timeout reaper reclaims stuck RUNNING
        ▼
  Audit query: "did job X run for date D, and what did it do?"
```

### Phase 1: Inventory and Risk Classify (Week 1)
1. List every cron job with schedule, timezone, expected duration, and business criticality
2. Classify by cost of a missed run vs cost of a duplicate run:
   - Missed run is expensive (billing, reconciliation) → `CATCH_UP_ALL` or `FIRE_ONCE`
   - Duplicate run is expensive (payments, emails) → `SKIP`, plus idempotency at the target
   - Neither (cache warm, cache refresh) → `SKIP`
3. Find jobs whose scripts are not idempotent — these need work before migration
4. Record the current success rate and duration distribution per job

### Phase 2: Build the Scheduler (Week 2)
1. Jobs table with: schedule, timezone, misfire policy, timeout, max catch-up, idempotency
   hint, owner
2. Atomic claim via conditional `UPDATE ... RETURNING`, no distributed lock anywhere
3. Heartbeat from the worker while running; reaper resets `RUNNING` rows whose heartbeat
   lapsed
4. Structured job history: every attempt, start, end, outcome, duration, error
5. Timeouts from measured p99 duration × 3, reviewed per job

### Phase 3: Migrate by Risk, Not Convenience (Week 3)
1. Start with low-risk jobs (`SKIP`, idempotent) to validate the plumbing
2. Then `FIRE_ONCE` jobs — the daily reports — where you can observe one full cycle
3. Then `CATCH_UP_ALL` jobs, with the bounded catch-up limit verified under a real gap
4. For non-idempotent jobs, add an idempotency mechanism at the *target* before moving
5. Run old and new in parallel for one cycle and compare execution counts

### Phase 4: Prove It (Week 4)
| Scenario | Expected | Verify |
|---|---|---|
| 5 scheduler instances, one job | exactly 1 execution | execution count = 1 |
| All schedulers down past fire time | misfire policy applies | policy honoured, no storm |
| Worker dies mid-job | reaper reclaims after timeout | one retry, then run recorded |
| Clock skew across instances | claim still single | no double execution observed |
| Deploy during fire window | exactly one run | no double fire during rollout |
| Job overruns its timeout | reaper reclaims; overlap possible | overlap detected and alerted |

Run all six in staging, then one deploy during a fire window in production — deliberately.

### Phase 5: Operate (Week 5+)
1. Dashboards: jobs by state, executions per job per period, duration p99 vs timeout,
   misfires, reclaims, claim contention
2. Alerts: job missed (compare against expected schedule), stuck run, duration above timeout,
   misfire count above zero
3. Runbook: "job did not run" — check history, misfires, and reclaim events before re-running
   manually; manual runs are recorded too
4. Quarterly: review misfire policies against actual business tolerance

### Deliverables
1. Job inventory with risk classification and product sign-off on misfire policy
2. Scheduler with atomic claims, heartbeats, reaper, and structured history
3. Staged migration plan plus the six-scenario chaos report
4. Dashboards, alerts, and the "job did not run" runbook

### Success Criteria
- Exactly one execution per fire time across all scenarios, including deliberate deploys
- No missed business-critical job during a full scheduler outage window
- Stuck runs recovered within one timeout, with the retry visible in history
- "Did job X run?" answered from history in under a minute

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Kubernetes Documentation, CronJobs —
  https://kubernetes.io/docs/concepts/workloads/controllers/
  Use for: the maintained statement of `concurrencyPolicy`, `startingDeadlineSeconds`, and
  missed-schedule behaviour — the same three decisions as this project's misfire policy,
  documented as configuration. Verify defaults for your cluster version.
- Amazon DynamoDB Developer Guide, "Core components of Amazon DynamoDB" —
  https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html
  Use for: conditional writes and transactions as the primitive behind a single-winner
  claim, for teams moving the job store off Postgres.

### Estimated Time
6 weeks part-time