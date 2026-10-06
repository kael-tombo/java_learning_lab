# Experiment Tracking with MLflow - Vision & Where This Is Going

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

## 1. The Future State

Tracking converges with lineage and evaluation into a single record per decision: which data, which code, which config, which outcome. The end state is a queryable history that answers 'why is this number what it is' without any human memory.

The test of that future state is boring: a new engineer ships a change to experiment tracking with mlflow on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Every run is tagged with data version, owner and branch before training starts.
- Metrics are logged as time series on a chosen cadence, with units.
- Artifacts are logged once with a retention policy.
- Promotions reference the run id that produced the artifact.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Log | Track params, one final metric and the model file. |
| L2 | Query | Tag runs and find the best one with a filter, not memory. |
| L3 | Gate | Compare candidate to champion on a matched data version. |
| L4 | Govern | Retention, budgets, and a regression alert wired to CI. |

## 4. Behaviours to Build

Log params first, metrics as series, artifacts once. Never compare across data versions. Make the record sufficient to rerun.

## 5. Anti-Vision (the failure mode we are avoiding)

- A tracking server that only stores the final metric.
- Run names that collide and overwrite each other.
- Hand-maintained spreadsheets of results beside a live tracker.
- Comparisons across data versions presented as model improvements.

## 6. Technology Shifts That Change the Work

1. Automatic lineage from data versions and code commits into the run record.
1. Tracking integrated with evaluation suites so regressions block merges.
1. Metric-first culture where business outcomes join back to model versions.
1. Cheap, high-cardinality logging as storage costs fall and dashboards become richer.

## 7. Your 30/60/90 Commitment

- **30 days.** Build a tracking client and log a run with params, tags and a metric series.
- **60 days.** Add tag-driven selection and a candidate-versus-champion comparison with a version guard.
- **90 days.** Add retention and storage budgeting plus a nightly regression alert wired into CI.

## 8. How To Tell You Are Actually Getting Better

- I can find last week's best run with one query.
- Any run of mine can be rerun from its record.
- I have never compared metrics across data versions.
- My tracking storage is budgeted and retained.

## 9. Principles That Should Not Change

- **Model experiments, runs, metrics, params, tags** Model experiments, runs, metrics, params, tags and artifacts correctly
- **Log hyperparameter** Log hyperparameter and metric time series for a training run
- **Tag runs so they can be selected without memory** Tag runs so they can be selected without memory

> The point of tracking is not record-keeping; it is that the next person does not repeat your experiments.
