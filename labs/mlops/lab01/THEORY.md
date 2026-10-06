# ML Pipeline Orchestration

**Track:** mlops  |  **Lab:** lab01  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. The Problem This Solves

A model is not a script; it is a graph of steps that must run in order, retry safely, resume after failure, and be auditable six months later.

Airflow-style DAG orchestration is the substrate every production ML platform rests on. Learning the failure modes here prevents the expensive class of bugs where a pipeline silently trains on stale data.

## 2. Learning Objectives

- Model a pipeline as a DAG and reason about its topological order
- Distinguish task, operator, schedule, run and dataset in an orchestrator
- Implement retries, timeouts and idempotency so a failed run can resume
- Identify the four states of a data pipeline run and act on each
- Explain why a DAG with side effects needs data-versioned inputs
- Wire lineage from a run to the data snapshot, code commit and model version

## 3. Core Concepts

### 3.1 The DAG is the unit of trust

Nodes are tasks, edges are dependencies, and the graph itself is the reproducibility contract. A linear pipeline hides a dependency you will regret the first time an upstream table changes. Explicit edges make the dependency reviewable.

### 3.2 Idempotency and safe retries

Retries are mandatory in any distributed system. A task is idempotent if re-running it produces the same state — which means writes are keyed by (run_id, task_id) rather than appended, and model artifacts are written to a versioned path before any pointer moves.

### 3.3 Backfill versus catch-up

Catch-up runs the newest window. Backfill replays historical windows, which is how you repair a silently bad dataset. Orchestrators that only catch up will keep training on the same bad window forever.

### 3.4 Data versioning is not optional

A run is reproducible only if the exact input snapshot is named. Without a data version in the run record, 'why is this metric different' has no answer. Version datasets and model binaries by content hash, not by timestamp.

### 3.5 Airflow-style operators and why they are async

Operators wrap external calls — a Spark job, an HTTP training service — that do not fit in a Python process slot. They poll for completion, which means the orchestrator is a scheduler plus a state machine, not a program counter.

### 3.6 Backpressure and fan-out limits

Fan-out without a concurrency cap will exhaust a warehouse or a GPU pool. Every orchestrator needs pool quotas, and the number that matters is the concurrency of the expensive node, not the count of nodes.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `T_task ≥ max(T_parents)` | Critical path | stage duration is bounded by its slowest parent |
| `SLO_sla = 1 − P(freshness > threshold)` | Freshness objective | the only pipeline SLO that matters |
| `retries = min(3, ceiling(log(1/p)/log(1/(1-e))))` | Retry budget | keep total attempts bounded |
| `cost = sum(node_cost × attempts)` | Cost model | retries are not free |
| `lineage = (code_commit, data_version, params, artifact_hash)` | Run fingerprint | what makes a run reproducible |
| `backfill_window = max(gap_detected, gap_repaired)` | Repair window | fix the whole gap, not just today |

## 5. How the Pieces Fit Together

1. Declare the DAG: one node per unit of work, edges only where there is a real dependency.

2. Give every node a retry policy, a timeout and an idempotent write.

3. Parameterise the data window; never hardcode a date.

4. Attach lineage to each run: commit, data version, container image, params.

5. Register the produced artifact in the model registry only after evaluation passes.

6. Alert on freshness, not just failure: a green pipeline with stale data is an outage.

## 6. Assumptions and Invariants

- Tasks are idempotent or wrapped so retries are safe
- Every input is named with an immutable version
- Concurrency is capped per resource pool
- Timezone and calendar assumptions are explicit for scheduling
- Task logs are retained and searchable, not printed to a lost console
- The DAG is versioned with the code that defines it

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| A run succeeds but trains on last week's data | no freshness gate on the input snapshot | fail the run when the input version is older than the SLA |
| Retry duplicates rows in the output table | non-idempotent append | write keyed by (run_id, task_id) and upsert |
| The cluster queues for hours during backfill | no concurrency pool limit | cap concurrency and prioritise catch-up over backfill |
| Nobody can explain a metric change | no lineage on the run record | store commit, data version and params on every run |
| Airflow task retries forever | retry_delay without max_retries | bounded retries plus a dead-letter path with an alert |
| Two runs write the same artifact path | path keyed on a timestamp only | content-hash the artifact path and move the pointer atomically |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `record Task(String id, List<String> deps, Runnable body)` | a node with explicit dependencies |
| `Topological sort / Kahn's algorithm` | execution order and cycle detection in one pass |
| `java.util.concurrent.Semaphore` | per-pool concurrency caps for fan-out |
| `Exponential backoff with a bounded attempt count` | the retry policy every node needs |
| `record RunFingerprint(String commit, String dataVersion, String params)` | the lineage record stored per run |

## 9. Where This Sits in the Larger System

- **mlops/lab02** stores the metrics and parameters this lab's runs produce.
- **mlops/lab03** is where the artifact this run produces gets promoted.
- **mlops/lab07** runs this DAG from CI, so the definition and the trigger live together.
- **mlops/lab09** is the validation gate that this DAG calls before training.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Model a pipeline as a DAG and reason about its topological order
- [ ] 0 — cannot yet — Distinguish task, operator, schedule, run and dataset in an orchestrator
- [ ] 0 — cannot yet — Implement retries, timeouts and idempotency so a failed run can resume
- [ ] 0 — cannot yet — Identify the four states of a data pipeline run and act on each
- [ ] 0 — cannot yet — Explain why a DAG with side effects needs data-versioned inputs
- [ ] 0 — cannot yet — Wire lineage from a run to the data snapshot, code commit and model version

## 11. Summary Checklist

- [ ] I can draw the dependency graph of a real pipeline from memory
- [ ] Every task is idempotent and bounded in retries
- [ ] Every input carries an immutable version
- [ ] I alert on freshness, not only on failure
- [ ] Each run records commit, data version and params
- [ ] Concurrency is capped per resource pool
