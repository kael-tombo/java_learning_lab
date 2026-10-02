# ML Pipeline Orchestration — Exercises

**Prerequisites:** Python 3.x with `apache-airflow`, `prefect`, or `dagster`. Java 21+ for simulation.

---

## Exercise 1: DAG Construction and Topological Sort

**Objective:** Implement core DAG data structure and scheduling logic.

**Tasks:**
1. Implement `Task` class: `id`, `name`, `function`, `upstream_task_ids`, `downstream_task_ids`, `retries`, `retry_delay`.
2. Implement `DAG` class: `tasks`, `add_task()`, `set_dependency(upstream, downstream)`.
3. Implement `topological_sort()` → execution order. Detect cycles (raise error).
4. Implement `get_ready_tasks(completed_task_ids)` → tasks whose all upstreams are done.
5. Test with diamond DAG: A → B, A → C, B → D, C → D. Order: A, (B,C), D.
6. **Challenge:** Implement dynamic task mapping: `map_task(template_task, iterable)` creates N task instances.

**Expected Answer:** Topological sort handles dependencies correctly. Cycle detection prevents invalid DAGs. Dynamic mapping creates parallel task instances.

---

## Exercise 2: Task Execution Engine with Retries

**Objective:** Build a task executor with retry logic and state management.

**Tasks:**
1. Implement `TaskInstance`: `task`, `dag_run_id`, `state` (QUEUED, RUNNING, SUCCESS, FAILED, UPSTREAM_FAILED), `try_number`, `start_time`, `end_time`.
2. Implement `execute_task(task_instance)`: 
   - Run task function, catch exceptions
   - On failure: if `try_number < max_retries`, schedule retry with exponential backoff
   - Update state accordingly
3. Implement `TaskExecutor` with thread pool: submit ready tasks, track futures.
4. Simulate task that fails 2x then succeeds. Verify 3 attempts total.
5. **Challenge:** Add timeout: kill task if exceeds `execution_timeout`. Mark as FAILED.

**Expected Answer:** Executor runs tasks in dependency order. Retries work with backoff. Failed tasks after max retries mark downstream as UPSTREAM_FAILED.

---

## Exercise 3: Sensor Implementation

**Objective:** Implement polling sensors for external dependencies.

**Tasks:**
1. Implement base `Sensor` class: `poke(context)` → bool, `poke_interval`, `timeout`, `mode` (poke/reschedule).
2. Implement `FileSensor(path)`: checks file exists (local or S3 via boto3).
3. Implement `HttpSensor(url, method, expected_status)`: polls HTTP endpoint.
4. Implement `PartitionSensor(table, partition)`: checks Hive/BigQuery partition exists.
5. Test `mode="reschedule"`: sensor releases worker slot between pokes (simulate with async/await or thread yield).
6. **Challenge:** Implement `SmartSensor` (Airflow): single process pokes multiple sensors of same type.

**Expected Answer:** Sensors wait efficiently. Reschedule mode frees worker for other tasks. SmartSensor reduces resource usage for many similar sensors.

---

## Exercise 4: XCom / Cross-Task Communication

**Objective:** Implement data passing between tasks.

**Tasks:**
1. Implement `XComBackend` interface: `push(key, value, task_instance)`, `pull(key, task_instance)`.
2. Implement `BaseXCom` (in-memory dict) and `DatabaseXCom` (SQLite/PostgreSQL).
3. Add serialization: JSON, pickle, custom (for numpy arrays, dataframes).
4. Size limit: warn if > 48KB (Airflow default), error if > 1MB.
5. Implement `XComArg` pattern: `task.output` returns lazy reference, resolved at downstream task start.
6. **Challenge:** Implement `MapIndex` for dynamic task mapping: `pull(key, map_index)` retrieves specific mapped instance output.

**Expected Answer:** Tasks pass small data via XCom. Large data: push reference (S3 path) to XCom, pull actual data in downstream. MapIndex enables fan-in after map.

---

## Exercise 5: Dynamic DAG Generation

**Objective:** Generate DAGs programmatically from configuration.

**Tasks:**
1. Define pipeline config (YAML/JSON):
   ```yaml
   pipeline:
     name: "training_pipeline"
     tasks:
       - id: "load_data"
         type: "PythonOperator"
         params: {source: "s3://bucket/data"}
       - id: "train"
         type: "PythonOperator"
         params: {model: "xgboost"}
         depends_on: ["load_data"]
   ```
2. Implement `DAGFactory.build(config)` → DAG object.
3. Support templating: `{{ ds }}`, `{{ params.model }}`, `{{ task_instance.try_number }}`.
4. Generate multiple DAGs from single config (e.g., per model type).
5. **Challenge:** Implement `DagBag` equivalent: parse directory of DAG files, detect import errors, load valid DAGs.

**Expected Answer:** Config-driven DAGs enable non-engineers to define pipelines. Templating allows dynamic parameters. DagBag provides centralized DAG management.

---

## Exercise 6: Pipeline Simulation in Java

**Objective:** Simulate orchestrator concepts in Java (as per lab's Java implementation).

**Tasks:**
1. Create `PipelineOrchestrator` class with:
   - `registerTask(String id, Task task)`
   - `addDependency(String upstream, String downstream)`
   - `execute()` — runs to completion
2. Task interface: `execute(Context ctx)` returns `TaskResult` (success, output, error).
3. Context provides: `getInput(String upstreamTaskId)`, `putOutput(String key, Object value)`.
4. Implement retry policy: `RetryPolicy(maxAttempts, backoffMs, exponentialFactor)`.
5. Implement sensors as tasks that poll: `FileSensorTask`, `HttpSensorTask`.
6. Demo: Build pipeline: LoadData → ValidateData → TrainModel → EvaluateModel → RegisterModel.
7. **Challenge:** Add visualization: export DAG to DOT/GraphViz format for rendering.

**Expected Answer:** Java simulation demonstrates orchestrator concepts without external dependencies. Clear separation of DAG definition, scheduling, execution.

---

## Exercise 7: Airflow DAG Development

**Objective:** Write production-ready Airflow DAGs.

**Tasks:**
1. Create DAG: `ml_training_pipeline.py` with tasks:
   - `extract_data` (PythonOperator)
   - `validate_data` (PythonOperator, uses Great Expectations)
   - `feature_engineering` (PythonOperator)
   - `train_model` (PythonOperator, MLflow logging)
   - `evaluate_model` (PythonOperator)
   - `register_model` (PythonOperator, MLflow Model Registry)
   - `notify_slack` (SlackWebhookOperator) — on success/failure
2. Add: `default_args` (retries, retry_delay, owner, sla), `schedule_interval`, `catchup=False`.
3. Use `TaskGroup` for logical grouping.
4. Add `BranchPythonOperator`: if model metric > threshold → register, else → notify_failure.
5. Use `TriggerDagRunOperator` to trigger deployment DAG after registration.
6. **Challenge:** Add data-aware scheduling: use `Dataset` (Airflow 2.4+) to trigger on feature store update.

**Expected Answer:** Production DAG with error handling, notifications, branching, cross-DAG triggers. Follows Airflow best practices.

---

## Exercise 8: Prefect Flow Development

**Objective:** Write equivalent pipeline in Prefect (pull-based, Pythonic).

**Tasks:**
1. Create flow with `@flow` decorator.
2. Tasks with `@task(retries=3, retry_delay_seconds=exponential_backoff)`.
3. Use `prefect.deployments` to create deployment (storage: S3, infrastructure: Docker/K8s).
4. Implement `prefect.artifacts` for model metrics, plots.
5. Use `prefect.blocks` for secrets (AWS credentials, MLflow URI).
6. Compare: code structure, state handling, observability vs Airflow.
7. **Challenge:** Implement `prefect.runtime.flow_run.parameters` for dynamic config.

**Expected Answer:** Prefect flow is pure Python. No DAG parsing. State handled automatically. Deployments separate flow code from infrastructure.

---

## Exercise 9: Dagster Asset-Centric Pipeline

**Objective:** Model pipeline as assets in Dagster.

**Tasks:**
1. Define assets: `@asset` for `raw_data`, `clean_data`, `features`, `model`, `evaluation_report`.
2. Use `@asset_deps` or upstream asset references for dependencies.
3. Implement `IOManager` for S3 (Parquet) and MLflow (model).
4. Add `FreshnessPolicy`: raw_data updated daily, model weekly.
5. Define `Job` selecting assets for materialization.
6. Run `dagster dev` — explore lineage graph, asset details, materialization history.
7. **Challenge:** Add `Sensor` that triggers job when `raw_data` S3 prefix updates.

**Expected Answer:** Assets = data products. Lineage automatic. Freshness policies detect stale data. Local dev loop fast.

---

## Exercise 10: End-to-End Orchestration Project

**Objective:** Design and implement a complete ML pipeline orchestration system.

**Scenario:** Daily retraining pipeline for fraud detection model.

**Requirements:**
1. **Architecture doc:** DAG diagram, task descriptions, dependencies, SLAs, failure handling.
2. **Implementation:** Choose ONE orchestrator (Airflow/Prefect/Dagster).
3. **Tasks:**
   - Ingest: Pull transactions from Kafka → write to Bronze table (partitioned by date)
   - Validate: Great Expectations suite on Bronze → quarantine bad records
   - Feature: Compute features → write to Feature Store (online/offline)
   - Train: Train XGBoost → log to MLflow → evaluate on holdout
   - Validate: Model performance > threshold? (BranchOperator)
   - Register: Promote to MLflow Model Registry (Staging)
   - Deploy: Trigger deployment pipeline (separate DAG)
   - Notify: Slack/Teams with metrics, lineage link
4. **Observability:** Dashboard with DAG runs, task durations, success rates, data freshness.
5. **CI/CD:** GitHub Actions: lint DAG code → test tasks → deploy to Airflow/Prefect/Dagster.
6. **Deliverable:** Running pipeline + 3-page design doc + README with run instructions.

**Reflection:** Compare orchestrators. What was easy/hard? How would you handle: late-arriving data, model rollback, multi-environment (dev/staging/prod)?