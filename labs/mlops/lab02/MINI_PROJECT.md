# MINI_PROJECT — Reproducible Experiment Tracker with a Promotion Gate

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

**Brief.** Build a tracking client, log a real hyperparameter sweep with metric time series, and gate promotion on a champion comparison.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

The gap between 'we ran experiments' and 'we know which one won and why' is entirely a tracking discipline problem.

## 2. Requirements

- Implement a tracking client (experiments, runs, params, metrics, tags, artifacts).
- Log a sweep of at least 20 runs as parent/child with metric time series at a chosen cadence.
- Tag every run with owner, branch and data version; write the selection query for the best per version.
- Compare the best candidate to a champion on a matched split with an epsilon gate.
- Prove the gate refuses a cross-data-version comparison.
- Add an offline queue and demonstrate that a tracking outage loses no metrics.
- Estimate monthly storage and write a retention policy.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Tracking client with retries and an offline queue | A client that survives an outage |
| 2 | 25m | Run context that logs params/tags at start and closes reliably | No leaked open runs |
| 3 | 40m | Run a 20-run sweep with parent/child runs and metric time series | A sweep report with curves |
| 4 | 25m | Tag-driven selection queries | Two queries that answer real questions |
| 5 | 30m | Champion comparison with epsilon and version guard | A gate plus a refused invalid comparison |
| 6 | 20m | Simulate a tracking outage; verify no metric loss and no duplicate runs | An outage transcript |
| 7 | 20m | Storage estimate and retention policy | A cost table and a policy |

## 4. Architecture Sketch

```text
 experiments -> runs (parent: sweep, children: configs)
                  |            |
                  |            +-- params (lr, depth, subsample)
                  |            +-- tags   (owner, branch, dataVersion)
                  |            +-- metrics: train_loss(t), val_auc(t), log_volume(t)
                  |            +-- artifacts: model.bin, config.json
                  v
         selection query -> best per dataVersion
                  |
         champion comparison (epsilon gate, version guard)
                  |
            promotion decision + offline queue replay
```

## 5. Implementation Notes

- Log params before the first step or a crashed run tells you nothing.
- Parent/child runs make a sweep queryable instead of twenty loose runs.
- The version guard is the highest-value 20 lines in the project.
- Measure real bytes per log so the storage estimate is not a guess.

## 6. Deliverables

1. Tracking client with an offline queue and an outage demonstration.
1. 20-run sweep report with metric time series.
1. Selection queries and a gated champion comparison.
1. Storage estimate and retention policy.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Client complete; runs closed reliably; no lost or duplicated metrics |
| Queryability | 25% | Tags support real selection questions |
| Discipline | 25% | Version guard, epsilon gate, reproducible records |
| Cost | 10% | Measured storage estimate and retention policy |
| Communication | 10% | Report explains what the sweep proved |

## 8. Stretch Goals

- Add a nightly regression alert that pages when the best run's metric drops.
- Version the metric definitions in code and assert every logger agrees.
- Wire the sweep into CI so a merged PR runs a small tracked sweep.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Implement a tracking client (experiments, runs, params, metrics, tags, artifacts).
- [ ] Log a sweep of at least 20 runs as parent/child with metric time series at a chosen cadence.
- [ ] Tag every run with owner, branch and data version; write the selection query for the best per version.
- [ ] Compare the best candidate to a champion on a matched split with an epsilon gate.
- [ ] Prove the gate refuses a cross-data-version comparison.
- [ ] Add an offline queue and demonstrate that a tracking outage loses no metrics.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
