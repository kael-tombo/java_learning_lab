# MLOps Orchestration - Quiz

## Question 1
Why orchestrate ML pipelines with a scheduler instead of ad-hoc scripts?
A) For aesthetics
B) Reproducibility, retries, dependency management, and audit trails — a script run by hand has none of these
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 2
What is a task's dependency?
A) A metric
B) A task that must succeed before this one runs — pipelines are DAGs of these
C) A plot
D) A speed

**Answer**: B

## Question 3
Why make pipeline tasks idempotent?
A) For aesthetics
B) A retried or re-run task must not duplicate work or corrupt state — use deterministic keys and upserts
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 4
What is a backfill?
A) A new database
B) Re-running historical pipeline runs to regenerate data after a fix — must be audited and rate-limited
C) A metric
D) A plot

**Answer**: B

## Question 5
Why separate exploration from production DAGs?
A) For aesthetics
B) Production needs determinism, alerting, and ownership; exploration needs speed and iteration — mixing them creates fragile pipelines
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 6
What is a data quality gate in a pipeline?
A) A plot
B) A validation step that fails the pipeline if row counts, nulls, or schema checks fail — stops bad data from propagating
C) A metric
D) A speed

**Answer**: B

## Question 7
Why parameterize pipeline runs?
A) For aesthetics
B) Same code, different date/config — parameterization makes runs reproducible and auditable
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 8
What is a task's SLA?
A) A metric
B) The time by which the task should finish — missing it triggers an alert; ML jobs often have soft SLAs that formal SLAs miss
C) A plot
D) A speed

**Answer**: B

## Question 9
Why is a monolithic pipeline fragile?
A) It is faster
B) One failure aborts everything, and all tasks share one schedule — decompose into modular DAGs per concern
C) It changes dtypes
D) It is a metric

**Answer**: B

## Question 10
What is a sensor in orchestration?
A) A metric
B) A polling check that waits for an external condition (file arrival, another pipeline's success) before triggering a task
C) A plot
D) A speed

**Answer**: B

## Question 11
Why version pipeline code?
A) For aesthetics
B) A re-run of an old data point must use the same code that produced it — or the result is not reproducible
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 12
What is a dry run?
A) A slow run
B) A run without materializing outputs — validates the DAG and parameters before side effects
C) A metric
D) A plot

**Answer**: B

## Question 13
Why track run duration trends?
A) For aesthetics
B) A task that gradually slows is a silent regression — alert on trend changes, not just absolute failures
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 14
What is a backfill's risk?
A) It is slow
B) Overwriting corrected data or hammering a dependency with a burst of historical runs — rate-limit and audit
C) It changes dtypes
D) It is a metric

**Answer**: B

## Question 15
Why is orchestration not the same as a job queue?
A) They are the same
B) Orchestration manages dependencies, schedules, and retries across a DAG — a queue runs tasks independently
C) A queue is faster
D) Orchestration is always slower

**Answer**: B
