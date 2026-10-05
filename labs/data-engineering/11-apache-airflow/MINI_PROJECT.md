# Apache Airflow — MINI PROJECT

## Project: Revenue Reconciliation DAG Suite

Three DAGs demonstrating production patterns: a 9-task daily revenue DAG with
sensors and retries, a dynamically-mapped backfill DAG, and a data-quality DAG
gated on dataset dependencies.

### Scope
- `revenue_daily`: extract -> validate -> transform -> marts -> publish, with
  an `ExternalTaskSensor` on the upstream extract, task groups, SLA.
- `revenue_backfill`: dynamic task mapping over a date range, `max_active=8`.
- `dq_gates`: dataset-scheduled quality checks that block publishing.
- `test_dags.py`: DAG integrity tests (cycles, missing retries, no `bash -c` monolith).

### Architecture

```
revenue_extract (upstream DAG)
   |  dataset: s3://lake/bronze/orders/_available  (upstream_updated)
revenue_daily
   |
  [ extract_taskgroup ]
     extract_raw >> validate_raw
  [ transform_taskgroup ]
     stage >> conform >> fact
  [ publish_taskgroup ]
     marts >> publish (SLA 2h, retries 2, backoff 120s)
   |
   dataset: analytics.daily_revenue/_available
dq_gates -> blocks anything depending on analytics.daily_revenue
```

### Implementation

```python
from datetime import datetime, timedelta
from airflow import DAG, task, task_group
from airflow.datasets import Dataset
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.utils.trigger_rule import TriggerRule

bronze_ready = Dataset("s3://lake/bronze/orders/_available")
revenue_published = Dataset("s3://lake/gold/daily_revenue/_available")

default_args = {
    "owner": "data-platform",
    "retries": 2,
    "retry_delay": timedelta(seconds=120),      # must exceed the p99 of the dependency
    "retry_exponential_backoff": True,
    "depends_on_past": False,
    "sla": timedelta(hours=2),
}

with DAG(
    dag_id="revenue_daily",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,          # one run at a time: overlapping runs double-write the mart
    default_args=default_args,
    tags=["finance", "tier1"],
) as dag:

    @task
    def extract(logical_date: str) -> str:
        ds = logical_date[:10]
        run(f"python -m etl.extract --date {ds} --out s3://lake/bronze/orders/{ds}/")
        return f"s3://lake/bronze/orders/{ds}/_SUCCESS"   # small return value only

    @task
    def validate(manifest_uri: str) -> None:
        m = json.load(open(manifest_uri))
        assert m["rows"] > 0, "empty extract"
        assert m["checksum_ok"], "checksum mismatch"

    @task
    def stage(**ctx) -> None:
        run_with_metrics("warehouse", ["SQL_TRANSFORM_STAGE", ctx["ds"]])

    @task
    def conform(**ctx) -> None:
        run_with_metrics("warehouse", ["SQL_TRANSFORM_CONFORM", ctx["ds"]])

    @task
    def build_fact(**ctx) -> None:
        run_with_metrics("warehouse", ["SQL_BUILD_FACT", ctx["ds"]])

    @task(outlets=[revenue_published])
    def publish(**ctx) -> None:
        run_with_metrics("warehouse", ["SQL_PUBLISH", ctx["ds"]])

    @task_group(group_id="extract_taskgroup")
    def tg_extract():
        s = extract()
        validate(s)

    with tg_extract():
        pass
    stage_task = stage()
    conform_task = conform()
    fact_task = build_fact()
    publish_task = publish()

    # Sensor: do not start transforming until the extract DAG has succeeded for
    # the same logical date. Deferrable so it does not occupy a worker slot.
    wait_for_extract = ExternalTaskSensor(
        task_id="wait_for_extract",
        external_dag_id="bronze_orders_extract",
        external_task_id="publish",
        execution_date="{{ logical_date }}",       # Airflow 2 form; logical_date for 2.x
        mode="reschedule",                          # the important bit: releases the slot
        poke_interval=300,
        timeout=60 * 60 * 3,
        soft_fail=False,
    )

    s3_ready = S3KeySensor(
        task_id="wait_for_bronze_marker",
        bucket_key="bronze/orders/{{ ds }}/_SUCCESS",
        poke_interval=600,
        mode="reschedule",
        timeout=60 * 60 * 4,
    )

    wait_for_extract >> s3_ready >> stage_task
    stage_task >> conform_task >> fact_task >> publish_task
```

### Dynamic task mapping for backfill

```python
with DAG(
    dag_id="revenue_backfill",
    schedule=None,                 # manual or dataset-triggered only
    params={"start": Param("2026-01-01"), "end": Param("2026-01-31")},
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
) as backfill:

    @task
    def dates_to_process(**params) -> list[str]:
        start = date.fromisoformat(params["start"])
        end = date.fromisoformat(params["end"])
        out, d = [], start
        while d <= end:
            if warehouse.has_partition("analytics.daily_revenue", d):
                d += timedelta(days=1)      # already done: skip, do not recompute
                continue
            out.append(d.isoformat())
            d += timedelta(days=1)
        return out

    @task(max_active_tis_per_dag=8, retries=0)   # per-DAG limit, not per-task-run
    def rebuild_one(day: str) -> None:
        run_id = f"shadow_{day}"
        run_with_metrics("warehouse", ["SQL_BACKFILL_SHADOW", day, run_id])
        validate_shadow(day, run_id)             # reconcile before touching prod
        promote_shadow_to_prod(day, run_id)      # atomic swap
        # If this task dies after promote but before the marker, the re-run
        # sees the marker and exits early. Idempotency lives in the marker check.

    dates = dates_to_process()
    rebuild_one.expand(day=dates)                # runtime fan-out, one task per date
```

### Dataset-based quality gating

```python
with DAG(dag_id="dq_gates", schedule=[revenue_published], catchup=False) as dq:

    @task
    def check_completeness(**ctx) -> None:
        result = run_with_metrics("warehouse", ["DQ_COMPLETENESS", ctx["ds"]])
        if result.failed_rows > result.total_rows * 0.0005:      # 0.05% budget
            raise AirflowFailException(
                f"{result.failed_rows} invalid rows exceeds the 0.05% budget; "
                f"downstream publishing is blocked. See {result.report_uri}")

    @task(trigger_rule=TriggerRule.ALL_DONE)
    def always_report(**ctx) -> None:
        publish_dq_metrics(ctx["ds"])            # runs even on failure: a failed run is a signal

    check_completeness() >> always_report()
```

### DAG integrity tests

```python
def test_no_cycles_and_all_tasks_have_retries(dagbag):
    for dag in dagbag.dags.values():
        assert dag.test_cycle() is False, f"{dag.dag_id} has a cycle"
        for t in dag.tasks:
            if t.task_type not in {"TriggerDagRunOperator", "EmptyOperator"}:
                assert t.retries >= 1, f"{dag.dag_id}.{t.task_id} has no retries"

def test_no_bash_monoliths(dagbag):
    for dag in dagbag.dags.values():
        for t in dag.tasks:
            if t.task_type == "BashOperator":
                assert len(t.bash_command.split("&&")) <= 2, f"{t.task_id} is a monolith"

def test_tasks_have_owners_and_retries(dagbag):
    for dag in dagbag.dags.values():
        assert dag.dag_id in OWNERS, f"{dag.dag_id} has no owner"
        assert dag.dag_id in ESCALATION, f"{dag.dag_id} has no escalation contact"
```

### Stretch
- Add a `TriggerDagRunOperator` fan-out from a per-tenant DAG to per-tenant DAGs.
- Convert the S3 sensor to a deferrable event-based trigger.
- Measure scheduler lag with and without `mode="reschedule"`.

## Deliverables
- [ ] Three DAGs: daily, dynamic-mapping backfill, dataset-gated quality
- [ ] Sensors with `mode="reschedule"`, explicit timeouts, and a scheduler-lag measurement
- [ ] Dynamic mapping with a per-DAG concurrency limit and a skip-already-done check
- [ ] Idempotent backfill with shadow-then-promote and a reconciliation step
- [ ] DAG integrity test suite (cycles, retries, owners, no monoliths)
- [ ] Written rationale for `max_active_runs`, pool usage, and SLA choices
