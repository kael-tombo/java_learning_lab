# Mock Interview: Apache Airflow (11-apache-airflow)

## Scenario: Build a production Airflow platform
Your data team is growing from 5 to 50 DAGs, from 2 to 15 engineers. You need a robust Airflow deployment that scales.

### Time: 45 minutes | Difficulty: Medium-Hard

---

## Part 1: Executor & Architecture (15 min)

**Executor comparison for this scale:**

| Executor | Pros | Cons | Best For |
|----------|------|------|----------|
| SequentialExecutor | Simple, no external deps | Single worker, no parallelism | Dev/test only |
| LocalExecutor | No external infra, multi-process | Single node bottleneck | Small teams (< 10 DAGs) |
| CeleryExecutor | Proven, moderate complexity | Need Redis/RabbitMQ + workers pool | Medium teams (10-50 DAGs) |
| KubernetesExecutor | Container isolation, auto-scaling | K8s expertise needed, more infra | Large teams (50+ DAGs), multi-tenant |

**Recommendation: KubernetesExecutor**
```
Architecture:

[Webserver] -- UI, metadata readings
[Scheduler] -- DAG parsing, scheduling (1-2 pods)
[KubernetesExecutor] -- Creates worker pods on demand
[Triggerer] -- Handles deferrable operators (async tasks)
[Metadata DB] -- PostgreSQL RDS (multi-AZ)
[GitSync] -- DAG sync from Git repo
[Redis] -- Celery backend (if hybrid), queue for K8s
[StatsD/Prometheus] -- Metrics
[Cloud Storage (S3/GCS)] -- DAG files, logs, plugins
```

**Scaling considerations:**
- Scheduler: 1 scheduler handles ~100 DAGs; scale to 2 for redundancy
- Worker pods: auto-scale based on queue depth (HorizontalPodAutoscaler)
- Metadata DB: provisioned IOPS, connection pooling (PgBouncer)
- DAG file parsing: shared file system (NFS/GitSync) or S3Fuse

---

## Part 2: DAG Design Patterns (10 min)

**Reusable DAG template with modern Airflow features:**

```python
from __future__ import annotations
import pendulum
from airflow.decorators import dag, task, task_group
from airflow.operators.python import PythonOperator
from airflow.models.baseoperator import chain
from airflow.utils.trigger_rule import TriggerRule
from datetime import timedelta

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["de-alerts@company.com"],
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(hours=1),
    "execution_timeout": timedelta(hours=4),
    "sla": timedelta(hours=8),
}

def create_etl_dag(table_name: str, schedule: str, source: str, target: str):
    @dag(
        dag_id=f"etl_{table_name}",
        schedule=schedule,
        start_date=pendulum.datetime(2024, 1, 1),
        catchup=False,
        default_args=DEFAULT_ARGS,
        tags=["etl", source, target],
        max_active_runs=1,
        max_active_tasks=8,
        render_template_as_native_obj=True,
    )
    def generate_etl():
        @task(task_id="extract", retries=3)
        def extract(**context):
            logical_date = context["logical_date"]
            return run_extract(table_name, source, logical_date)

        @task_group(group_id="transform")
        def transform_group():
            @task
            def validate(data):
                return run_validation(data, table_name)

            @task
            def transform(data):
                return run_transform(data, table_name)

            @task
            def quality_check(data):
                return check_quality(data, table_name)

            validated = validate(extracted)
            transformed = transform(validated)
            qc_result = quality_check(transformed)
            return qc_result

        @task(task_id="load", trigger_rule=TriggerRule.ALL_SUCCESS)
        def load(data):
            return run_load(data, target, table_name)

        @task(task_id="cleanup", trigger_rule=TriggerRule.ALL_DONE)
        def cleanup():
            return run_cleanup(table_name)

        @task(task_id="notify_failure", trigger_rule=TriggerRule.ONE_FAILED)
        def notify_failure():
            return send_alert(f"Pipeline failed: {table_name}")

        extracted = extract()
        qc_passed = transform_group()
        loaded = load(qc_passed)
        cleanup_task = cleanup()
        notify = notify_failure()

        extracted >> transform_group() >> loaded >> cleanup_task
        notify

    return generate_etl()

# Generate DAGs
create_etl_dag("customers", "@daily", "postgres_db", "snowflake")
create_etl_dag("orders", "@hourly", "postgres_db", "snowflake")
create_etl_dag("inventory", "@daily", "api_source", "snowflake")
```

---

## Part 3: CI/CD Pipeline (10 min)

**CI/CD for DAG deployment:**

```yaml
# .github/workflows/deploy-dags.yml
name: Deploy Airflow DAGs
on:
  push:
    branches: [main]
    paths:
      - 'dags/**'
      - 'plugins/**'
      - 'requirements.txt'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate Python syntax
        run: |
          pip install apache-airflow==2.8.0
          airflow dags list-import-errors
      - name: Run unit tests
        run: pytest dags/tests/
      - name: Lint with ruff
        run: ruff check dags/

  deploy-staging:
    needs: validate
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v3
      - name: Sync DAGs to staging
        run: |
          aws s3 sync dags/ s3://airflow-staging/dags/
          # Trigger DAG validation in staging
          curl -X POST $STAGING_AIRFLOW_API/dags/validate_dags/dagRuns \
            -H 'Authorization: Bearer ${{ secrets.AIRFLOW_TOKEN }}'

  deploy-prod:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3
      - name: Sync DAGs to production
        run: aws s3 sync dags/ s3://airflow-prod/dags/
```

**GitSync setup:**
```helm
# Helm values for Airflow on K8s
config:
  airflow.cfg:
    core:
      dags_are_paused_at_creation: True
      load_examples: False
dags:
  gitSync:
    enabled: true
    repo: (link removed)
    branch: main
    subPath: "dags"
    root: "/usr/local/airflow/dags"
    wait: 60  # Sync interval in seconds
```

---

## Part 4: Monitoring & Scaling (10 min)

**Key metrics and alerts:**
```python
# metrics.py - Emitted via StatsD
from airflow.stats import Stats

# DAG-level metrics
Stats.gauge(f"dag.{dag_id}.duration", duration_seconds)
Stats.gauge(f"dag.{dag_id}.sla_miss", sla_miss_seconds)
Stats.gauge(f"dag.{dag_id}.success_rate", success_rate)

# Task-level metrics
Stats.gauge(f"task.{task_id}.duration", task_duration)
Stats.gauge(f"task.{task_id}.retry_count", retries)

# Scheduler health
Stats.gauge("scheduler.heartbeat", 1)
Stats.gauge("scheduler.dag_parsing_lag", parsing_lag_ms)
Stats.gauge("scheduler.task_queued_count", queued_tasks)
```

**Grafana dashboard panels:**
1. DAG success rate (7-day rolling %)
2. SLA compliance (% of DAGs completing within SLA)
3. Task duration heatmap (hour/day)
4. Scheduler parsing time (ms per DAG)
5. Executor utilization (slots used vs available)
6. Queue depth (number of queued tasks)
7. Top 10 slowest tasks
8. Error rate by DAG, task, operator type

**Alert thresholds:**
```yaml
alerts:
  dag_failure:
    condition: "dag.failure > 0"
    severity: P1
    action: PagerDuty

  sla_miss:
    condition: "dag.sla_miss > 0"
    severity: P2
    action: Slack #de-alerts

  scheduler_lag:
    condition: "scheduler.dag_parsing_lag > 60"
    severity: P3
    action: Slack #de-infra

  queue_depth:
    condition: "scheduler.task_queued_count > 100"
    severity: P2
    action: PagerDuty
```

**Scaling the scheduler:**
- Monitor: `airflow scheduler --num_runs` parsing time
- 1 scheduler can handle ~100 DAGs with single-thread parsing
- For 200+ DAGs: increase `max_threads` or add secondary scheduler (HA)
- DAG serialization: `AIRFLOW__CORE__STORE_DAG_CODE=True` (reduces parsing)
- File parsing: use `min_file_process_interval` to control frequency

---

## Follow-up Questions

**Dynamic task mapping:**
```python
@task
def process_file(file_path: str) -> dict:
    return {"file": file_path, "status": "processed"}

@task
def aggregate_results(results: list[dict]) -> dict:
    return {"total": len(results), "statuses": [r["status"] for r in results]}

# Dynamic map: one task per file
file_list = ["s3://data/file1.csv", "s3://data/file2.csv"]
tasks = process_file.expand(file_path=file_list)
agg = aggregate_results(tasks)
```

**Deferrable operators:**
```python
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task import ExternalTaskSensor

# Instead of polling sensor (wastes worker slot):
wait_sensor = ExternalTaskSensor(
    task_id="wait_for_upstream",
    external_dag_id="upstream_dag",
    external_task_id="done",
    mode="reschedule",  # Free worker slot while waiting
    poke_interval=60,
    timeout=3600,
    deferrable=True,  # Use triggerer instead of worker
)
```

**Zero-downtime backfill DAG:**
```python
@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=True)
def backfill_orders():
    @task
    def backfill_day(ds: str, **context):
        staging_table = f"orders_{ds.replace('-', '_')}_backfill"
        run_query(f"CREATE TABLE {staging_table} AS SELECT * FROM source WHERE date = '{ds}'")
        run_query(f"""
            ALTER TABLE orders SWAP PARTITION ('{ds}')
            WITH TABLE {staging_table}
        """)
    # Dynamic task for each day
    dates = ["2024-01-01", "2024-01-02", "2024-01-03"]
    backfill_day.expand(ds=dates)
```

