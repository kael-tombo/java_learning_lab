# VISION — Workflow Orchestration: DAGs, Scheduling, and Recovery
> Where this lab takes you: from cron scripts nobody dares delete to a DAG
> platform where retries, backfills, and dependencies are first-class.

## The Arc
1. **Model** — DAGs, tasks, dependencies, scheduling, data intervals.
2. **Execution** — executors, workers, pools, concurrency limits.
3. **Reliability** — retries, sensors, timeouts, idempotency.
4. **Time** — logical vs physical dates, catch-up, backfill.
5. **Operate** — observability, SLAs, dynamic task mapping.

## Milestones (checkable)
- [ ] M1: turn 5 interdependent SQL jobs into one DAG and explain each edge.
- [ ] M2: add a sensor so a DAG never runs on stale input.
- [ ] M3: implement a backfill of 30 days without double counting.
- [ ] M4: bound concurrency so one DAG cannot starve the scheduler.
- [ ] M5: answer "why didn't this run?" for 12 hypothetical failure cases.

## Anti-Goals
- Orchestration that does actual data movement; move data in the task, orchestrate the task.
- A DAG with a `bash -c` monolith hiding 40 steps.
- Airflow tasks that are not idempotent and are retried forever.

## Interview Lens
- "How do you know a task succeeded rather than silently doing nothing?"
- "What happens when two DAGs need the same table?"
- "Backfill 90 days — how, without paging finance?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT DAG.
- Wk3 add sensors, pools, dynamic mapping. Wk4 REAL_WORLD_PROJECT with an SLA model.

## Done = You Can
- Design an orchestration layer your teams trust for freshness and correctness.
