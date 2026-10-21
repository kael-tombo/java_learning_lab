# How Workflow Orchestration Works

## Airflow Architecture
`python
"""
Airflow Components:
+------------------+      +------------------+
| Webserver (UI)   |      | Scheduler        |
| - DAG views      |      | - Parses DAGs    |
| - Task logs      |      | - Triggers tasks |
| - Trigger tasks  |      | - Manages state  |
+------------------+      +------------------+
         |                        |
         +----------+-------------+
                    |
            +-------v-------+
            |   Metadata    |
            |   Database    |
            |  (PostgreSQL) |
            +-------+-------+
                    |
         +----------+----+
         |               |
+--------v-------+  +----v-----------+
| Executor       |  | Worker(s)      |
| (Celery/K8s)   |  | Execute tasks  |
+----------------+  +----------------+
"""
`

## DAG Execution Flow
`java
/*
1. Scheduler parses DAG files every 30 seconds
2. Determines which DAG runs to create (schedule, catchup)
3. Creates DAG Run and Task Instances
4. Tasks queued to Executor
5. Workers pick up tasks and execute
6. Task state updated in metadata DB
7. Dependencies evaluated, next tasks triggered
8. DAG Run completes when all tasks done
*/
`

## Java Task in Airflow
`python
# DAG calling a Java/Spark job
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

dag = DAG('java_etl_pipeline', schedule_interval='0 2 * * *')

spark_job = SparkSubmitOperator(
    task_id='run_spark_etl',
    application='/opt/app/etl-job.jar',
    java_class='com.example.ETLJob',
    application_args=['{{ ds }}', '{{ var.value.environment }}'],
    executor_memory='4g',
    num_executors=4,
    dag=dag
)
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# Workflow Orchestration Internals

## Airflow Scheduler Internals
`python
# Scheduler heartbeat loop
class SchedulerJob:
    def _execute(self):
        while True:
            self._parse_dag_files()         # Reads DAG files
            self._create_dag_runs()         # Creates scheduled runs
            self._check_dependencies()      # Evaluates upstream success
            self._queue_tasks()             # Sends tasks to executor
            self._process_executor_events() # Gets task results
            time.sleep(settings.SCHEDULER_HEARTBEAT_SEC)
`

## Task Instance Lifecycle
`
none -> scheduled -> queued -> running -> success
                                          -> failed -> up_for_retry
                                          -> skipped
                                          -> upstream_failed
`

## Executor Architecture
`python
# CeleryExecutor distributes tasks via message broker
# Tasks are serialized and sent to Celery workers
# Workers deserialize, execute, return results

# KubernetesExecutor creates a pod per task
# Each task runs in its own container
# Clean isolation, perfect scaling
`

## Database Schema
`sql
-- Core Airflow tables
dag (dag_id, is_paused, is_active)
dag_run (id, dag_id, execution_date, state)
task_instance (dag_id, task_id, execution_date, state)
task_fail (id, task_instance_id, duration, error)
log (id, dttm, dag_id, task_id, event)
`
"@

System.Collections.Hashtable["MATH_FOUNDATION.md"] = @"
# Math Foundation for Orchestration

## Scheduling Calculus
`
Next Execution = schedule_interval.ceil(start_date)
Backfill = Historical runs between start_date and now
Catchup = True: Run all missed intervals

Recovery Time = RetryDelay * (1 + RetryExponent + ... + RetryExponent^(n-1))
TotalPossibleDelay = Max(Failures) * RecoveryTime
`

## DAG Complexity
`
Nodes = Number of tasks
Edges = Number of dependencies
Complexity = O(N + E) for topological sort
Critical Path = Longest path in DAG (minimum execution time)
Parallelism = TotalTasks / CriticalPathLength
`

## Resource Requirements
`
Scheduler Memory = DAGCount * AverageDAGSize + Overhead
Worker Memory = TaskConcurrency * AverageTaskMemory + Overhead
Database Connections = SchedulerThreads + WebserverThreads + Workers
Queue Depth = TaskThroughput * ProcessingTime / Workers
`

## Scheduling Metrics
`
SLA Miss Rate = LateDAGs / TotalDAGs
Task Success Rate = Succeeded / (Succeeded + Failed)
Backlog = CreatedTasks - CompletedTasks
Duration P50/P95/P99 = Percentile(DAGDurations)
`
"@

System.Collections.Hashtable["VISUAL_GUIDE.md"] = @"
# Visual Guide to Workflow Orchestration

## DAG Visualization
`
[Start] --> [Extract Orders] ------> [Validate Orders] --------> [Load Orders]
              |                          |
              v                          v
        [Extract Customers] -------> [Validate Customers] --> [Load Customers]
              |                                                    |
              v                                                    |
        [Extract Products] ------> [Validate Products] ----------->|
                                                                   |
                                                                   v
                                                            [Build Aggregations]
                                                                   |
                                                                   v
                                                            [Notify Success]
`

## Airflow UI Tree View
`
root
 |-- extract_orders     [success]  2024-01-01 02:00:00
 |-- extract_customers  [success]  2024-01-01 02:00:05
 |-- extract_products   [success]  2024-01-01 02:00:03
 |-- validate_orders    [success]  2024-01-01 02:05:00
 |-- validate_customers [success]  2024-01-01 02:04:30
 |-- validate_products  [success]  2024-01-01 02:04:45
 |-- load_orders        [success]  2024-01-01 02:10:00
 |-- load_customers     [success]  2024-01-01 02:09:30
 |-- load_products      [success]  2024-01-01 02:09:45
 |-- build_aggregations [running ] 2024-01-01 02:15:00
 |-- notify_success     [queued  ] 2024-01-01 --
`

## Gantt Chart View (Execution Timeline)
`
extract_orders       |â–ˆâ–ˆâ–ˆâ–ˆ|             02:00-02:05
extract_customers    |â–ˆâ–ˆâ–ˆ|              02:00-02:04
extract_products     |â–ˆâ–ˆâ–ˆ|              02:00-02:04
validate_orders       |â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ|         02:05-02:09
validate_customers    |â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ|          02:04-02:08
validate_products     |â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ|         02:04-02:09
load_orders            |â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ|         02:10-02:14
load_customers         |â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ|         02:09-02:13
load_products          |â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ|         02:10-02:14
build_aggregations     |â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ| 02:15-02:25
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: Workflow Orchestration

## Complete Airflow DAG
`python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.sensors.external_task import ExternalTaskSensor

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['data-team@company.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=4),
    'sla': timedelta(hours=3),
}

dag = DAG(
    'data_pipeline',
    default_args=default_args,
    description='Main data pipeline',
    schedule_interval='0 2 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=True,
    max_active_runs=1,
    tags=['production', 'etl'],
)

# Sensors
wait_for_source = ExternalTaskSensor(
    task_id='wait_for_source_update',
    external_dag_id='source_ingestion',
    external_task_id='complete',
    timeout=3600,
    poke_interval=60,
    dag=dag,
)

# Extraction
extract_orders = SparkSubmitOperator(
    task_id='extract_orders',
    application='/jobs/extract_orders.py',
    conn_id='spark_default',
    application_args=['--date', '{{ ds }}'],
    executor_memory='8g',
    num_executors=4,
    dag=dag,
)

extract_customers = SparkSubmitOperator(
    task_id='extract_customers',
    application='/jobs/extract_customers.py',
    conn_id='spark_default',
    application_args=['--date', '{{ ds }}'],
    executor_memory='4g',
    num_executors=2,
    dag=dag,
)

# Validation
def validate_data(**context):
    ti = context['task_instance']
    # Check row counts, null percentages, etc.
    validation_passed = run_validation_checks()
    if not validation_passed:
        raise ValueError("Data quality check failed")
    return 'load_data' if validation_passed else 'send_alert'

validate = BranchPythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    provide_context=True,
    dag=dag,
)

# Loading
load_orders = SparkSubmitOperator(
    task_id='load_orders',
    application='/jobs/load_to_warehouse.py',
    conn_id='spark_default',
    application_args=['--table', 'fact_orders', '--date', '{{ ds }}'],
    dag=dag,
)

# Alerts
send_alert = SlackWebhookOperator(
    task_id='send_alert',
    slack_webhook_conn_id='slack_conn',
    message=':x: Pipeline failed at validation for {{ ds }}',
    dag=dag,
)

notify_success = SlackWebhookOperator(
    task_id='notify_success',
    slack_webhook_conn_id='slack_conn',
    message=':white_check_mark: Pipeline completed for {{ ds }}',
    dag=dag,
)

# Dependencies
wait_for_source >> [extract_orders, extract_customers]
[extract_orders, extract_customers] >> validate
validate >> load_orders >> notify_success
validate >> send_alert
`
"@

System.Collections.Hashtable["STEP_BY_STEP.md"] = @"
# Step-by-Step Orchestration Setup

## Step 1: Install Airflow
`ash
export AIRFLOW_HOME=~/airflow
pip install apache-airflow
airflow db init
airflow users create --username admin --password admin \
  --firstname Admin --lastname User --role Admin --email admin@example.com
`

## Step 2: Create DAG Directory
`ash
mkdir -p /dags
mkdir -p /plugins
mkdir -p /logs
`

## Step 3: Write Your First DAG
`python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

dag = DAG('hello_world', schedule_interval='@daily', start_date=datetime(2024, 1, 1))
task = BashOperator(task_id='say_hello', bash_command='echo "Hello World"', dag=dag)
task2 = BashOperator(task_id='say_goodbye', bash_command='echo "Goodbye"', dag=dag)
task >> task2
`

## Step 4: Start Airflow
`ash
airflow webserver --port 8080 --daemon
airflow scheduler --daemon
`

## Step 5: Debug
`ash
# Test task
airflow tasks test hello_world say_hello 2024-01-01

# Trigger DAG manually
airflow dags trigger hello_world

# Check logs
airflow tasks logs hello_world say_hello 2024-01-01
`

## Step 6: Java/Spark Integration
`python
# Use SparkSubmitOperator for Java/Spark tasks
spark_task = SparkSubmitOperator(
    task_id='spark_job',
    application='/opt/app/my-spark-job.jar',
    java_class='com.example.MySparkJob',
    spark_binary='/opt/spark/bin/spark-submit',
    total_executor_cores=4,
    executor_memory='4g',
    name='airflow-spark-job',
    dag=dag,
)
`
"@

System.Collections.Hashtable["COMMON_MISTAKES.md"] = @"
# Common Orchestration Mistakes

## 1. Not Using Idempotent Tasks
`python
# WRONG - appends without checking duplicates
INSERT INTO table VALUES (...) 

# RIGHT - idempotent
DELETE FROM table WHERE date = '{{ ds }}';
INSERT INTO table VALUES (...);
`

## 2. Hardcoding Dependencies
`python
# WRONG
task1 >> task2 >> task3 >> task4

# RIGHT - dynamic dependencies
extract_tasks >> validate_tasks >> load_tasks >> notify
`

## 3. No Task Timeouts
`python
# WRONG - task can run forever
task = PythonOperator(task_id='unbounded', ...)

# RIGHT - timeout kills hung tasks
task = PythonOperator(
    task_id='bounded',
    execution_timeout=timedelta(hours=2),
    ...
)
`

## 4. Too Many Tasks in One DAG
`python
# WRONG - 200 tasks in one DAG
# It's unwieldy to monitor and slow to parse

# RIGHT - fan-out DAGs per domain
# sales_pipeline.py: 15 tasks
# marketing_pipeline.py: 12 tasks
# hr_pipeline.py: 8 tasks
`
"@

System.Collections.Hashtable["DEBUGGING.md"] = @"
# Debugging Workflow Orchestration

## Common Issues

### DAG Not Appearing in UI
`ash
# Check DAG parsing
airflow dags list-import-errors
# Check scheduler logs
airflow scheduler --debug
# Verify DAG file syntax
python -c "import ast; ast.parse(open('dags/my_dag.py').read())"
`

### Task Stuck in Queued
`ash
# Check executor status
airflow jobs check
# Check Celery workers
celery -A airflow.executors.celery_executor.app inspect active
# Check database connections
airflow db check
`

### Missing Dependencies
`python
# Debug: Print all upstream tasks
task.upstream_task_ids
task.downstream_task_ids
`

### Performance Issues
`python
# Slow DAG parsing
# Minimize top-level code in DAG files
# Use DAG.loader for modular DAGs
# Increase DAG parsing interval
airflow config get-value scheduler min_file_process_interval
`
"@

System.Collections.Hashtable["REFACTORING.md"] = @"
# Refactoring Workflow Orchestration

## Before: Monolithic DAGs
`python
# 500-line DAG with everything
dag = DAG('everything')
task1 = ... task2 = ... task3 = ...
# 50 more tasks
`

## After: Modular DAGs with SubDAGs
`python
from airflow.operators.subdag import SubDagOperator

def extract_subdag(parent_dag_name, child_dag_name, args):
    dag = DAG(f'{parent_dag_name}.{child_dag_name}', default_args=args)
    task1 = ... task2 = ...
    return dag

extract = SubDagOperator(
    task_id='extract',
    subdag=extract_subdag('main', 'extract', default_args),
    dag=dag,
)
`

## Before: Duplicated Code
`python
# Same validation in 5 DAGs
`

## After: Shared Plugins
`python
# airflow/plugins/custom_operators.py
class QualityCheckOperator(BaseOperator):
    def execute(self, context):
        # Shared validation logic
        pass
`
"@

System.Collections.Hashtable["PERFORMANCE.md"] = @"
# Orchestration Performance

## Airflow Tuning
`ash
# Increase DAG parsing parallelism
airflow config set scheduler parsing_processes 4

# Adjust scheduler
airflow config set scheduler scheduler_heartbeat_sec 10
airflow config set scheduler max_tis_per_query 512
airflow config set scheduler min_file_process_interval 30

# Adjust executor
airflow config set celery worker_concurrency 16
airflow config set celery celery_app_name airflow.executors.celery_executor
`

## Database Optimization
`sql
-- Clean up old records
DELETE FROM task_instance WHERE start_date < NOW() - INTERVAL '30 days';
DELETE FROM log WHERE dttm < NOW() - INTERVAL '30 days';
DELETE FROM xcom WHERE timestamp < NOW() - INTERVAL '7 days';
VACUUM task_instance;
`

## Task Optimization
`python
# Use deferrable operators for long-running sensors
wait = ExternalTaskSensor(
    task_id='wait',
    mode='reschedule',  # Don't hold worker slot
    exponential_backoff=True,
    poke_interval=300,
)
`
"@

System.Collections.Hashtable["SECURITY.md"] = @"
# Orchestration Security

## Authentication
`python
# Airflow RBAC
# airflow.cfg
[webserver]
rbac = True
authenticate = True
auth_backend = airflow.contrib.auth.backends.password_auth
`

## Variable Management
`python
# NEVER hardcode secrets in DAGs
# Use Airflow Variables (encrypted)
password = Variable.get("db_password", deserialize_json=False)

# Use Airflow Connections
conn = BaseHook.get_connection("my_db")
host = conn.host
login = conn.login
password = conn.get_password()
`

## Network Security
`python
# Run workers in private network
# Use VPC peering for database access
# Enable SSL for webserver
[webserver]
enable_proxy_fix = True
cookie_secure = True
`

## Audit
`python
# All task executions logged
# DAG version tracking via git sync
# Airflow logs contain full execution history
`
"@

System.Collections.Hashtable["ARCHITECTURE.md"] = @"
# Workflow Orchestration Architecture

## Production Airflow Architecture
`
                         +-------------------------+
                         |     PostgreSQL / MySQL   |
                         |     (Metadata DB)        |
                         +-----------+-------------+
                                     |
         +---------------------------+----------------------------+
         |                           |                            |
+--------v--------+         +--------v--------+         +--------v--------+
|   Webserver     |         |    Scheduler    |         |   Flower (Celery|
|   (Port 8080)   |         |   (Daemon)      |         |   Monitoring)  |
+-----------------+         +-----------------+         +-----------------+
                                     |
                            +--------v--------+
                            |      Redis       |
                            |  (Message Queue) |
                            +--------+--------+
                                     |
                    +----------------+----------------+
                    |                                 |
            +-------v-------+                 +-------v-------+
            | Celery Worker |                 | Celery Worker |
            |   (Task Exec) |                 |   (Task Exec) |
            +-------+-------+                 +-------+-------+
                    |                                 |
            +-------v-------+                 +-------v-------+
            |   Airflow      |                 |   Airflow      |
            |   Logs (S3)    |                 |   Logs (S3)    |
            +----------------+                 +----------------+
`

## Spring Boot Integration
`java
// Spring Boot can produce tasks called by Airflow
@SpringBootApplication
@EnableScheduling
public class DataPipelineApp {
    @Bean
    public CommandLineRunner runner() {
        return args -> {
            // This app is triggered by Airflow's BashOperator
            String date = args[0];
            processData(date);
        };
    }
}
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# Workflow Orchestration Exercises

## Exercise 1: Simple DAG
Create a DAG with 3 tasks (extract, transform, load) running daily.

## Exercise 2: Branching
Add a branch operator that runs quality checks and routes to success or failure paths.

## Exercise 3: Sensors
Add an ExternalTaskSensor that waits for an upstream DAG before starting.

## Exercise 4: Java/Spark Integration
Create a DAG that runs a SparkSubmitOperator with a Java Spark application.

## Exercise 5: Backfill
Trigger a backfill for the past 30 days and monitor progress.
