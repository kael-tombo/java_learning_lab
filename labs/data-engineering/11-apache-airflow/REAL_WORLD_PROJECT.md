# Apache Airflow — REAL WORLD PROJECT

## Context

A data-intensive insurer runs 1,100 DAGs on Airflow 2 with the Celery executor
across 4 schedulers. Symptoms: median scheduling delay of 9 minutes for
priority DAGs, DAG processing taking 22 minutes (so a 04:00 DAG can start
late), XCom database at 340GB, and 300 worker slots mostly held by sensors.
Leadership wants a migration decision made on evidence. You own the diagnosis
and the remediation plan.

## Scale & Constraints

| Dimension | Value |
|---|---|
| DAGs | 1,100, ~6,500 tasks/day, peak 1,200 concurrent |
| Schedulers | 4, Postgres metadata DB (1 writer + 3 readers) |
| Executors | Celery, 300 slots, 40 workers |
| Pools | 6 pools, but 2 tasks run outside any pool |
| Metadata DB | 340GB, 68% XCom, `dag_run` 1.9B rows |
| Critical path | 04:00 claims actuarial run; 1,600 dependent tasks |
| Constraint | no big-bang migration; claim regulatory deadlines |

## Architecture (target)

```
scheduler tier
  -- 6 schedulers, partitioned by dag_id hash, so one bad DAG cannot stall others
  -- dag-file processor as a separate, scaled process (this was 22 min: a separate bug)
  -- metadata DB split: Airflow 2.x supports a separate dag-processor DB
  -- XCom -> object storage backend (files on S3), pruning the 340GB

execution tier
  -- deferrable sensors released the 200 slots they were holding
  -- pools: critical(40) / standard(180) / backfill(60) / notebook(20)
  -- KubernetesExecutor for bursty, memory-shaped workloads
```

## Key Implementation — the diagnosis that determined the plan

**Finding 1: sensors were holding 62% of worker slots.** A `mode="poke"`
sensor occupies a worker for its entire wait. With 180 sensors averaging 22
minutes of waiting, that is ~66 slots idle-by-waiting.

```python
# Measure before changing anything.
from airflow.models import TaskInstance

def sensor_slot_occupancy(lookback_days: int = 7) -> pd.DataFrame:
    ti = session.query(TaskInstance).filter(
        TaskInstance.start_date >= days_ago(lookback_days),
        TaskInstance.task_type.in_(["S3KeySensor", "ExternalTaskSensor",
                                    "SqlSensor", "HttpSensor"]),
    ).all()
    rows = []
    for t in ti:
        if t.end_date is None or t.start_date is None:
            continue
        rows.append({
            "dag_id": t.dag_id, "task_id": t.task_id,
            "slot_minutes": (t.end_date - t.start_date).total_seconds() / 60,
            "poked": getattr(t, "mode", "poke") == "poke",
        })
    df = pd.DataFrame(rows)
    return (df.groupby(["dag_id", "task_id"])
              .agg(slot_minutes=("slot_minutes", "sum"), runs=("slot_minutes", "size"))
              .assign(pct_of_total=lambda d: 100 * d.slot_minutes / df.slot_minutes.sum())
              .sort_values("slot_minutes", ascending=False))
```

The top 20 sensors alone accounted for 41% of slot-minutes. Converting them to
`mode="reschedule"` (or deferrable triggers) returned those slots to real work
with no change to correctness.

**Finding 2: DAG file processing was the latency, not task execution.** Parsing
and importing 1,100 DAG files while the scheduler also serialized DAG runs put
serialization at 22 minutes. The fix is architectural: run the DAG processor as
its own process pool against a dedicated database, which took serialization
under 90 seconds.

**Finding 3: XCom was a database, not a control channel.** Tasks were returning
dataframes through XCom. Moving XCom to object storage, plus a hard rule that
task returns must be small (paths, counts, ids), took the metadata DB from
340GB to 41GB and cut vacuum time to nothing.

**Finding 4: retries were re-running successful work.** `bash -c` monoliths
meant one failing step re-ran 30 successful ones. Splitting the 400 worst
monoliths into native tasks cut total task minutes 38% and made retry cost
proportional to the failing step.

## Remediation Phases

| Phase | Duration | Change | Measured effect |
|---|---|---|---|
| 1 | Weeks 1-2 | Sensors -> `reschedule`/deferrable | slot availability +66, p99 task start 9min -> 40s |
| 2 | Weeks 3-5 | Dedicated DAG-processor pool + DB | serialization 22min -> 90s |
| 3 | Weeks 6-7 | XCom -> object storage, return-value lint | metadata DB 340GB -> 41GB |
| 4 | Weeks 8-12 | Split bash monoliths, fix retry policy | task minutes -38% |
| 5 | Weeks 13-18 | 6 schedulers, pool redesign, KubernetesExecutor | scheduler isolation; no cross-tenant starvation |

## The Pool Design That Fixed Starvation

The old pools were advisory. Tasks ran outside them, and one team could occupy
everything during its month-end.

```python
from airflow.models.pool import Pool

POOLS = {
    # Reserved. Claims actuarial must never be starved by a team backfill.
    "critical":   {"slots": 40, "description": "Regulatory deadline DAGs only"},
    "standard":   {"slots": 180, "description": "Default production DAGs"},
    "backfill":   {"slots": 60,  "description": "Historical recompute; off-peak only"},
    "notebook":   {"slots": 20,  "description": "Ad-hoc analysis"},
}

def enforce_pools(dagbag) -> list[str]:
    """CI check: every task must belong to a pool. A task with no pool is a
    task that can starve a regulatory DAG."""
    missing = []
    for dag in dagbag.dags.values():
        for t in dag.tasks:
            if t.pool is None:
                missing.append(f"{dag.dag_id}.{t.task_id}")
    return missing
```

## Failure Modes and the Runbook

1. **Scheduler lag on critical DAGs.** Symptom: 04:00 DAG starts at 04:22.
   Cause: contention in DAG processing or a stuck DAG. Fix: partition schedulers
   by `dag_id` hash so one pathological DAG cannot block others; alert on
   `scheduler.scheduler_zombie` and DAG-processing duration.
2. **Metadata DB write contention.** Symptom: scheduler heartbeat warnings,
   slow UI. Cause: too many task updates, usually a fan-out. Fix: shard
   schedulers, move XCom out, and cap `max_active_tis_per_dag`.
3. **Pool exhaustion.** Symptom: tasks queued for hours. Fix: `critical` pool is
   admission-controlled by an allowlist checked in CI; `backfill` runs only
   outside 06:00-20:00 UTC.
4. **XCom payload limit reached.** Symptom: `AirflowDatabaseException` on a large
   return value. Fix: return a URI; a DAG lint rejects returns over 1MB.
5. **A DAG stuck in `running` after an executor loss.** Symptom: slot never
   released. Fix: `zombie` detection, `graceful_deadlock`/`_execution_timeout`,
   and a `celery` visibility timeout aligned with the task timeout.
6. **Backfill recomputes a date that already succeeded.** Symptom: mart numbers
   move after a "no-op" backfill. Fix: partition-existence check before
   enqueuing, plus shadow-then-promote for anything that must be recomputed.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Airflow's core abstraction is a DAG of tasks, scheduled by data intervals; the
  scheduler manages dependencies, retries, sensors, pools, and backfill, and
  tasks should be idempotent with data stored outside XCom.
  - Reference: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html
  - Reference: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/xcoms.html
  - Reference: https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/pools.html
- Airflow's best-practice guidance explicitly covers idempotent tasks, testing
  DAGs, and avoiding passing large data between tasks.
  - Reference: https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html

## Deliverables
- [ ] Diagnosis with the four measurements (sensor slots, serialization, XCom, retries)
- [ ] Phased remediation plan with a measured before/after table
- [ ] Pool design with a CI enforcement check
- [ ] Dedicated DAG-processor configuration and a serialization-latency SLO
- [ ] XCom object-storage migration plus a return-value lint
- [ ] Runbook for the six failure modes
- [ ] Migration decision memo recommending Airflow-keep vs move, on this evidence
