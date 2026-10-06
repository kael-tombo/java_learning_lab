# Experiment Tracking with MLflow

**Track:** mlops  |  **Lab:** lab02  |  **Level:** Intermediate

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

Six weeks into a modelling project nobody can say which version of the data, which hyperparameter or which code produced the number in the slide deck.

Experiment tracking is the cheapest tooling you will ever adopt and the one that determines whether your team can learn from its own work rather than repeating it.

## 2. Learning Objectives

- Model experiments, runs, metrics, params, tags and artifacts correctly
- Log hyperparameter and metric time series for a training run
- Tag runs so they can be selected without memory
- Make a run reproducible from its own metadata
- Compare runs and detect regressions automatically
- Explain how tracking differs from model registry and from data versioning

## 3. Core Concepts

### 3.1 The entity hierarchy

Experiment is a container, run is one trial, and inside a run you log params, metrics, tags and artifacts. Getting the hierarchy right means queries like 'best run on the last data version' are expressible, not requiring a spreadsheet convention.

### 3.2 Params versus metrics versus tags

Params are inputs and do not change during a run (learning rate, depth). Metrics are numbers that change per iteration (train loss, AUC). Tags are arbitrary strings for filtering (owner, branch, data_version). Mixing them makes queries impossible later.

### 3.3 Metrics are a time series

Logging train loss every 50 iterations, not just the final value, is what lets you see overfitting, divergence and the exact step where a run went wrong. One scalar per run throws away the most useful signal you had.

### 3.4 Runs must be reproducible on their own

A run that logs params but not the data version, the code commit or the environment is an anecdote. The tracking record is the receipt: it should contain enough to reconstruct the run without asking its author.

### 3.5 Tracking is not the registry

Tracking records trials; the registry (Lab 03) manages which artifact is promoted to which stage. They are related but answering different questions — 'what did we try' versus 'what is serving'.

### 3.6 Log volume and cost discipline

High-frequency logging of big artifacts is expensive and rarely useful. Log scalar metrics at a sensible cadence, log artifacts once, and set a retention policy on the tracking store before it becomes the biggest thing in your bucket.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `run_id = hash(config, code, data_version)` | Reproducibility key | one identifier for the whole trial |
| `delta_metric = metric(candidate) - metric(champion)` | Regression check | the promotion gate input |
| `metric(t) plotted vs iteration` | Metric time series | overfitting detection |
| `tags → filtered query` | Selection | runs are found by metadata, not memory |
| `run_count × metrics_per_run × cadence` | Log volume estimate | budget before you start logging |
| `best_run = argmax metric over filtered runs` | Comparison query | the question tracking exists to answer |

## 5. How the Pieces Fit Together

1. Create or look up the experiment by name, keyed to a business question.

2. Start a run and immediately log the full config, the commit and the data version as params and tags.

3. Train with a periodic logging hook: params once, metrics on a cadence.

4. Log the final metrics plus the artifact (model file, plots, the config JSON).

5. End the run; compare against the champion with a delta check.

6. Feed the selection query into a promotion decision recorded in the registry.

## 6. Assumptions and Invariants

- Run names are unique per experiment and meaningful to a human reading them later
- Params are logged before training so a crashed run is still diagnosable
- The data version is always present, even when the data is 'the same'
- Metric cadence is chosen deliberately rather than every iteration
- Artifact logging happens once, not per epoch
- Retention is set so the tracking store does not become the cost centre

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Cannot find last week's best run | no tags for data version or branch | tag every run with owner, branch and data version |
| A run's params are wrong | params logged after training instead of before | log params immediately at run start |
| Overfitting invisible until the run finished | only the final metric logged | log metrics on a cadence as a time series |
| Tracking store costs more than the models | logging large artifacts repeatedly | log artifacts once; set retention and a log volume budget |
| Two people ran the 'same' experiment | no shared run naming convention | require a naming convention with date and owner |
| The tracked number and the dashboard disagree | different metric definitions | define each metric once in code and version it |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `java.net.http.HttpClient` | the REST calls to the tracking server |
| `record RunInfo(String runId, String status, Instant start, Instant end)` | the run handle the training loop reports into |
| `LongAdder for per-metric sample counts` | cadence control without a thread per metric |
| `java.nio.file.Path / Files.move with ATOMIC_MOVE` | artifact writes that cannot be half-read |
| `record MetricDef(String name, String unit, int cadence)` | one definition of each metric, shared by logger and reporter |

## 9. Where This Sits in the Larger System

- **mlops/lab01** produces the run fingerprint this lab records.
- **mlops/lab03** promotes the artifact this lab tracks.
- **mlops/lab07** runs these experiments from CI, so tracking is automatic.
- **mlops/lab09** validates data before the run starts, which the tags should record.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Model experiments, runs, metrics, params, tags and artifacts correctly
- [ ] 0 — cannot yet — Log hyperparameter and metric time series for a training run
- [ ] 0 — cannot yet — Tag runs so they can be selected without memory
- [ ] 0 — cannot yet — Make a run reproducible from its own metadata
- [ ] 0 — cannot yet — Compare runs and detect regressions automatically
- [ ] 0 — cannot yet — Explain how tracking differs from model registry and from data versioning

## 11. Summary Checklist

- [ ] I can distinguish param, metric and tag and use each correctly
- [ ] Every run has data version, commit and owner tags before training
- [ ] Metrics are logged as a time series, not one final scalar
- [ ] A run is reproducible from its own record
- [ ] I compare against a champion with a delta, not a vibe
- [ ] Log volume and retention are budgeted
