# Experiment Tracking with MLflow - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `run_id = hash(config, code, data_version)` | Reproducibility key - one identifier for the whole trial |
| `delta_metric = metric(candidate) - metric(champion)` | Regression check - the promotion gate input |
| `metric(t) plotted vs iteration` | Metric time series - overfitting detection |
| `tags → filtered query` | Selection - runs are found by metadata, not memory |
| `run_count × metrics_per_run × cadence` | Log volume estimate - budget before you start logging |
| `best_run = argmax metric over filtered runs` | Comparison query - the question tracking exists to answer |

## Why the Math Matters

Experiment tracking turns 'we tried some things' into a queryable relation over (config, metric, artifact). The mathematics is light; the discipline of parameterising and versioning is everything.


---

## 1. Metric time series for overfitting detection

```text
log metric(i) every cadence i
train_loss(t) down, val_loss(t) up after t* => overfit
gap(t) = val_loss(t) - train_loss(t)
```

The gap between training and validation loss over time is the earliest reliable signal of overfitting, and it is only visible if you logged the series rather than the endpoint.

**Worked example.** Train loss 0.08, val loss 0.14 at epoch 40; by epoch 120 train 0.02, val 0.31. Gap grows from 0.06 to 0.29 — best round was 40, not the last.


---

## 2. Run volume and storage budget

```text
scalar_bytes = runs x metrics x log2(cadence)
artifact_bytes = runs x artifact_size
monthly = (scalar + artifact) x 30
```

Metrics are cheap; artifacts are not. Most tracking stores are dominated by checkpoints, so the budget conversation is about artifacts, not metrics.

**Worked example.** 10,000 runs x 20 metrics x 200 logs = 40M values (small). 10,000 runs x 2 checkpoints x 80MB = 1.6TB — the artifacts dominate completely.


---

## 3. Reproducibility key

```text
run_id = H(config, commit, data_version, seed, env)
same key => same run; different key => different run
```

A content hash over the inputs gives you an identity for the trial. Two runs with the same key are duplicates you can prune; two runs claiming the same key but differing are a provenance bug.

**Worked example.** Someone changes the seed and re-runs: the key changes, so the runs are distinct, and the difference is explainable from the tags.


---

## 4. Regression gate between candidate and champion

```text
delta = metric(candidate) - metric(champion)
promote if delta > -epsilon and delta > 0
require val on same data version
```

Comparing metrics across different data versions is meaningless. The gate must fix the evaluation data before it can compare anything.

**Worked example.** Candidate AUC 0.912 vs champion 0.905 on data v42: delta +0.007, promote. The same candidate on data v41 shows 0.898 — the version, not the model, explained the change.


---

## 5. Selection queries

```text
best = argmax_r metric(r) where tags(r) match filters
compare = {r1, r2, ...} joined on run_id
report = group_by(tags) then aggregate
```

Tagging is what makes queries possible. This is why tags are strings with stable values and params are typed: you group and filter on tags, you reproduce on params.

**Worked example.** Query: max(val_auc) where data_version = 'v42' and model = 'lgbm'. Without tags this is a manual scroll; with them it is a single indexed lookup.


---

## Cheat Sheet

- `run_id = hash(config, code, data_version)` - Reproducibility key
- `delta_metric = metric(candidate) - metric(champion)` - Regression check
- `metric(t) plotted vs iteration` - Metric time series
- `tags → filtered query` - Selection
- `run_count × metrics_per_run × cadence` - Log volume estimate
- `best_run = argmax metric over filtered runs` - Comparison query

## Numerical Traps

- Logging only the final metric, which hides the overfitting point entirely.
- Comparing metrics across different data versions and calling the delta a regression.
- Treating a tag as a param (or vice versa), which breaks grouping queries.
- Logging artifacts per epoch and discovering the storage bill later.
- Reusing run names so the later run silently overwrites the earlier one.

## Self-Check Problems

1. Given train/validation loss by epoch, identify the best round and the overfitting onset.
2. Estimate monthly tracking storage for 10,000 runs with the cadence and artifact sizes you use.
3. Define a reproducibility key and show how a seed change alters it.
4. Write the selection query for the best run per data version, and state the tags it needs.
5. Design a promotion gate that cannot be fooled by comparing across data versions.
