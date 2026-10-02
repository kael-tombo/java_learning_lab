# ML Pipeline Orchestration — Quiz (10 Questions)

**Instructions:** Answer each question. Correct answers and explanations follow.

---

### Q1: What is a DAG in the context of ML pipeline orchestration?
A) A type of neural network architecture
B) Directed Acyclic Graph representing task dependencies
C) A data structure for storing model weights
D) A database schema for experiment tracking

**Answer: B** — A DAG (Directed Acyclic Graph) represents tasks as nodes and dependencies as directed edges. No cycles allowed. Orchestrators (Airflow, Prefect, Dagster) execute tasks in topological order.

---

### Q2: What is the difference between a task and a pipeline in orchestration?
A) No difference — synonyms
B) A task is a single unit of work; a pipeline is a DAG of tasks
C) A pipeline runs on one machine; tasks run on multiple
D) Tasks are for training; pipelines are for serving

**Answer: B** — Task = atomic unit (e.g., "load data", "train model"). Pipeline = collection of tasks with dependencies defining execution order. Pipeline = DAG of tasks.

---

### Q3: What is idempotency in pipeline tasks?
A) Running a task multiple times produces the same result
B) Tasks that can run in parallel
C) Tasks that never fail
D) Tasks that cache their outputs

**Answer: A** — Idempotent task: f(f(x)) = f(x). Re-running with same inputs produces same outputs. Critical for retry safety and reproducibility. Non-idempotent tasks (e.g., "send email") need special handling.

---

### Q4: What is the purpose of retry logic with exponential backoff?
A) To make failed tasks eventually succeed without overwhelming the system
B) To speed up pipeline execution
C) To reduce the number of tasks
D) To parallelize task execution

**Answer: A** — Transient failures (network blip, temporary resource unavailability) often resolve on retry. Exponential backoff (1s, 2s, 4s, 8s...) prevents thundering herd. Max retries and max delay cap prevent infinite loops.

---

### Q5: What is the difference between static and dynamic DAGs?
A) Static DAGs are defined in code; dynamic DAGs are generated at runtime
B) Static DAGs run faster
C) Dynamic DAGs don't support retries
D) Static DAGs can't have branches

**Answer: A** — Static: DAG structure known at parse time (Airflow classic). Dynamic: DAG structure determined at runtime based on parameters/data (Airflow dynamic task mapping, Prefect, Dagster). Dynamic enables map-reduce patterns.

---

### Q6: What is a "sensor" in Airflow-style orchestration?
A) A task that waits for an external condition (file, partition, API response)
B) A task that monitors CPU usage
C) A task that validates data quality
D) A task that triggers other DAGs

**Answer: A** — Sensor = task that polls until condition is met (e.g., `FileSensor` waits for file in S3, `HttpSensor` waits for API success). Modes: `poke` (blocking) vs `reschedule` (releases worker slot between pokes).

---

### Q7: What is XCom (Cross-Communication) in Airflow?
A) A message queue between workers
B) Mechanism for tasks to pass small data (metadata, paths) to downstream tasks
C) A database for model artifacts
D) A monitoring dashboard

**Answer: B** — XCom allows tasks to push/pull small data (JSON-serializable). Use for passing file paths, model versions, metrics. NOT for large data (use external storage + pass reference).

---

### Q8: What is the difference between "push" and "pull" based orchestration?
A) Push: orchestrator tells workers what to do. Pull: workers poll for work.
B) Push is faster; pull is slower
C) Push is for batch; pull is for streaming
D) They are the same

**Answer: A** — Push (Airflow scheduler → workers): central scheduler assigns tasks. Pull (Prefect, Dagster, Celery): workers poll queue. Pull scales better, handles heterogeneous workers, more resilient to scheduler failure.

---

### Q9: What is "data lineage" in pipeline orchestration?
A) The version of the pipeline code
B) Tracking data from source through transformations to output
C) The lineage of the orchestrator software
D) The dependency graph of tasks

**Answer: B** — Data lineage = tracking data origin, transformations, and destinations. Answers: "Where did this column come from?" "What pipelines use this table?" Critical for debugging, compliance, impact analysis.

---

### Q10: What is the difference between orchestration and workflow engines?
A) Orchestration = central coordinator; Workflow = decentralized/choreography
B) Orchestration is for ML; Workflow is for general purpose
C) No difference
D) Workflow engines don't support retries

**Answer: A** — Orchestration: central brain knows full DAG, decides what runs when (Airflow, Prefect, Dagster, Argo). Choreography: services emit/consume events, no central coordinator (Kafka, event-driven). Orchestration better for complex ML pipelines with strict ordering.