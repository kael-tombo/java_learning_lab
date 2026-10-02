# ML Pipeline Orchestration — Flashcards

**Format:** Question (front) → Answer (back). Use for spaced repetition.

---

### Card 1
**Q:** What is ML pipeline orchestration?
**A:** Automating, scheduling, and coordinating ML workflow tasks (data prep, training, validation, deployment) as a DAG.

---

### Card 2
**Q:** What is a DAG?
**A:** Directed Acyclic Graph. Nodes = tasks. Edges = dependencies. No cycles. Execution follows topological order.

---

### Card 3
**Q:** What is a task vs pipeline?
**A:** Task = atomic unit of work. Pipeline = DAG of tasks with defined execution order.

---

### Card 4
**Q:** What is idempotency?
**A:** Re-running task with same inputs → same outputs. f(f(x)) = f(x). Essential for safe retries.

---

### Card 5
**Q:** What is retry with exponential backoff?
**A:** Retry failed tasks with increasing delays (1s, 2s, 4s...). Handles transient failures. Max retries + max delay cap.

---

### Card 6
**Q:** What are static vs dynamic DAGs?
**A:** Static: structure known at parse time. Dynamic: structure determined at runtime (e.g., map over list).

---

### Card 7
**Q:** What is a sensor?
**A:** Task that waits for external condition (file exists, API ready, partition available). Modes: poke (block) vs reschedule (yield).

---

### Card 8
**Q:** What is XCom?
**A:** Cross-Communication. Small data passing between tasks (paths, params, metrics). Not for large data.

---

### Card 9
**Q:** Push vs pull orchestration?
**A:** Push: central scheduler assigns tasks (Airflow). Pull: workers poll queue (Prefect, Dagster, Celery).

---

### Card 10
**Q:** What is data lineage?
**A:** Tracking data from source → transformations → output. Enables debugging, compliance, impact analysis.

---

### Card 11
**Q:** What is orchestration vs choreography?
**A:** Orchestration: central coordinator knows full DAG. Choreography: event-driven, no central brain.

---

### Card 12
**Q:** What is a DAG run / pipeline run?
**A:** One execution instance of a DAG with specific parameters/context (run_id, execution_date).

---

### Card 13
**Q:** What is backfill / catchup?
**A:** Running pipeline for historical dates. Airflow: catchup=True runs missed intervals.

---

### Card 14
**Q:** What is a task instance?
**A:** One execution of a task within a DAG run. Has state: queued, running, success, failed, upstream_failed.

---

### Card 15
**Q:** What is a trigger rule?
**A:** Condition for task to run: all_success (default), all_failed, one_success, one_failed, none_failed, dummy.

---

### Card 16
**Q:** What is a SubDAG / TaskGroup?
**A:** Group related tasks visually and logically. TaskGroup (Airflow 2.0+) preferred over SubDAG (deprecated).

---

### Card 17
**Q:** What is dynamic task mapping?
**A:** Create task instances at runtime based on upstream output (e.g., map over list of files). Airflow 2.3+, Prefect, Dagster.

---

### Card 18
**Q:** What is a "branch" operator?
**A:** Conditional execution: choose one downstream path based on logic (BranchPythonOperator).

---

### Card 19
**Q:** What is SLA (Service Level Agreement) in orchestration?
**A:** Expected max runtime for task/DAG. Alert if exceeded. Helps detect stuck pipelines.

---

### Card 20
**Q:** What is a dead letter queue (DLQ) for failed tasks?
**A:** Capture failed task payloads for later replay/debugging. Not standard in all orchestrators.

---

### Card 21
**Q:** What is the difference between cron and event-based scheduling?
**A:** Cron: time-based (every hour). Event-based: triggered by external event (file arrival, model drift alert).

---

### Card 22
**Q:** What is a "pipeline as code"?
**A:** Define pipelines in code (Python, YAML) not UI. Version controllable, testable, CI/CD friendly.

---

### Card 23
**Q:** What are the main orchestration tools?
**A:** Airflow (mature, push), Prefect (Pythonic, pull), Dagster (asset-centric, pull), Argo (K8s-native), Kubeflow Pipelines (K8s), Flyte (K8s, typed).

---

### Card 24
**Q:** What is asset-centric orchestration (Dagster)?
**A:** Focus on data assets (tables, models) not tasks. Define what assets exist, how to materialize them. Lineage built-in.

---

### Card 25
**Q:** What is a "software-defined asset"?
**A:** Dagster concept: asset defined by code that computes it. Metadata, partitions, freshness policies attached.

---

### Card 26
**Q:** What is partition in orchestration?
**A:** Logical slice of data (by date, region, etc.). Enables incremental processing, backfill, parallelism.

---

### Card 27
**Q:** What is an IOManager?
**A:** Dagster/Prefect abstraction: how to store/load artifacts (S3, DB, local). Swappable without changing business logic.

---

### Card 28
**Q:** What is the difference between task-level and pipeline-level retries?
**A:** Task-level: retry individual failed task. Pipeline-level: re-run entire DAG from start or failed task.

---

### Card 29
**Q:** What is "exactly-once" semantics?
**A:** Task executes exactly once despite retries/failures. Hard to achieve. Idempotency + transactional outputs approximate it.

---

### Card 30
**Q:** What is a "pipeline template"?
**A:** Reusable DAG structure with parameters. Instantiate for different models/datasets/environments.

---

### Card 31
**Q:** How to handle secrets in pipelines?
**A:** Never hardcode. Use secret manager (AWS Secrets Manager, HashiCorp Vault, K8s Secrets). Inject at runtime.

---

### Card 32
**Q:** What is a "task wrapper" or "operator"?
**A:** Reusable task template (e.g., PythonOperator, DockerOperator, SparkSubmitOperator). Encapsulates common patterns.

---

### Card 33
**Q:** What is the "latest only" pattern?
**A:** Only run latest scheduled DAG run, skip intermediate ones. Useful for daily pipelines where only latest matters.

---

### Card 34
**Q:** What is a "trigger DAG" / "cross-DAG dependency"?
**A:** One DAG triggering another. TriggerDagRunOperator. Or dataset-driven scheduling (Airflow 2.4+).

---

### Card 35
**Q:** What is "dataset-driven scheduling"?
**A:** Schedule DAG when upstream dataset updates (Airflow 2.4+). Decouples producer/consumer DAGs.

---

### Card 36
**Q:** What is the "task flowchart" pattern?
**A:** Visualize DAG as flowchart. Airflow UI graph view. Helps debugging and communication.

---

### Card 37
**Q:** What is "pipeline testing"?
**A:** Unit test tasks, integration test DAGs (test DAG structure, task dependencies, parameter passing).

---

### Card 38
**Q:** What is "observability" for pipelines?
**A:** Metrics (duration, success rate), logs, alerts, lineage, data quality checks. Datadog, Prometheus, OpenTelemetry.

---

### Card 39
**Q:** What is a "pipeline deployment" strategy?
**A:** CI/CD for pipelines: test DAG code → deploy to dev → promote to prod. Version DAGs. Rollback capability.

---

### Card 40
**Q:** When to use Airflow vs Prefect vs Dagster?
**A:** Airflow: mature, huge ecosystem, push-based. Prefect: Pythonic, pull, great DX. Dagster: asset-centric, testing, local dev. Argo/Kubeflow: K8s-native.