# Model Evaluation

**Track:** ml  |  **Lab:** lab10  |  **Level:** Intermediate

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

You can always make a model look good on the data you trained it on. The whole craft is measuring performance on data the model has never seen, in the way the business will actually experience it.

Every algorithm in this track is worthless without an honest evaluation protocol. This is the lab that stops you shipping a model that is worse than the baseline.

## 2. Learning Objectives

- Build a confusion matrix correctly and derive every metric from it
- Explain why accuracy fails under class imbalance and what to use instead
- Compute ROC-AUC and the PR curve, and know which to trust when
- Implement k-fold and grouped/time-series cross-validation correctly
- Estimate confidence intervals on your metric estimates
- Choose an evaluation protocol that matches deployment and defend it

## 3. Core Concepts

### 3.1 The confusion matrix is the source of truth

TP, FP, FN, TN determine every classification metric. Precision asks 'of those I flagged, how many were right'; recall asks 'of those that were positive, how many did I catch'. They trade off against each other through the threshold, and neither is meaningful alone.

### 3.2 Why accuracy is a trap

At a 1% fraud base rate, predicting 'never fraud' gives 99% accuracy and catches nothing. Accuracy is only informative when classes are balanced and error costs are symmetric. Report a confusion matrix before any aggregate.

### 3.3 ROC versus precision-recall

ROC-AUC uses the false positive rate, which shrinks as the base rate falls, making ROC look optimistic on rare positives. PR curves focus on precision, which degrades honestly. For rare positives and imbalanced costs, PR-AUC is the metric to quote.

### 3.4 Cross-validation must match deployment

k-fold assumes i.i.d. rows. Time series must respect time (forward chaining). Grouped data must split by group, or the same patient or user appears in train and test and you have leaked. Preprocessing must be fit inside each fold. This is where most published numbers quietly go wrong.

### 3.5 Variance of your estimate

A metric on 200 samples has a wide confidence interval. Comparing two models by a 0.5% difference without an interval is not a comparison. Use repeated CV or bootstrap intervals, and prefer the model that wins consistently rather than the one that wins on average.

### 3.6 Calibration versus discrimination

AUC measures ranking. Calibration measures whether a predicted 0.2 happens 20% of the time. Both matter: a ranking model that sends probabilities to a pricing engine needs calibration. Report both, and choose the threshold from the cost matrix rather than from the metric.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `Accuracy = (TP+TN)/N` | Accuracy | misleading under imbalance |
| `Precision = TP/(TP+FP)` | Precision | of flagged, how many were right |
| `Recall = TP/(TP+FN)` | Recall / TPR | of true positives, how many were caught |
| `F1 = 2PR/(P+R)` | F1 | harmonic mean; ignores TN |
| `Fβ = (1+β²)PR/(β²P + R)` | F-beta | weights recall when β > 1 |
| `AUC = P(score_pos > score_neg)` | ROC AUC | threshold-free ranking quality |
| `AP = Σ (R_k − R_{k−1}) P_k` | Average precision | PR summary; better than AUC when rare positives |
| `CI ≈ metric ± 1.96 · SE` | Normal CI for a proportion | rough interval on a metric estimate |

## 5. How the Pieces Fit Together

1. Define the metric from the cost matrix before you look at any numbers.

2. Split with a protocol matching deployment: stratified k-fold, grouped, or time-based.

3. Fit every preprocessing step inside the training fold.

4. Compute the confusion matrix, then all metrics from it; print all of them.

5. Plot the ROC and PR curves, and choose a threshold from the cost matrix on validation folds.

6. Report an interval, a baseline comparison, and the protocol you used — all three.

## 6. Assumptions and Invariants

- The evaluation split is representative of production traffic
- Splits respect the data-generating structure: time, groups, entities
- Preprocessing is fitted inside the training fold only
- The metric chosen matches the business cost, not the convenience
- Labels are correct; label noise caps achievable metrics
- Enough evaluation samples for the interval to be narrow enough to decide

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Accuracy 99%, recall 0 | 1% positive class and an untrained baseline | always print the confusion matrix and compare with a trivial predictor |
| Validation score better than the holdout score | preprocessing or feature selection done before splitting | move every fitted step inside the fold and assert it |
| Time-series CV score far above reality | shuffled folds let the model see the future | use forward-chaining splits and a final future-only holdout |
| Model A wins by 0.3% and you ship it | no interval on the estimate | use repeated CV or bootstrap intervals and require a consistent win |
| ROC-AUC 0.95 on a rare-positive task, terrible precision | FPR shrinks with the base rate | quote PR-AUC and precision at the operating point instead |
| Published result not reproducible | no seed recorded for splits or model init | record seeds, folds and version every artifact |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `int[] confusionMatrix(y, yHat)` | the single source of truth for every metric |
| `Arrays.sort on scored predictions` | rank-based ROC and PR computation |
| `SplittableRandom with a recorded seed` | reproducible folds |
| `record Fold(int[] train, int[] test)` | explicit, inspectable, serialisable folds |
| `Collectors.groupingBy for grouped splits` | group-aware partitioning by entity id |

## 9. Where This Sits in the Larger System

- **Every lab in this track** depends on this protocol; the metric decides which one wins.
- **Lab 02** shows why threshold choice comes from costs, not from 0.5.
- **Lab 07** shows why unsupervised structure needs external validation, not cross-validation.
- **mlops/lab10** applies this to a live A/B decision on production traffic.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Build a confusion matrix correctly and derive every metric from it
- [ ] 0 — cannot yet — Explain why accuracy fails under class imbalance and what to use instead
- [ ] 0 — cannot yet — Compute ROC-AUC and the PR curve, and know which to trust when
- [ ] 0 — cannot yet — Implement k-fold and grouped/time-series cross-validation correctly
- [ ] 0 — cannot yet — Estimate confidence intervals on your metric estimates
- [ ] 0 — cannot yet — Choose an evaluation protocol that matches deployment and defend it

## 11. Summary Checklist

- [ ] I print the confusion matrix before any aggregate metric
- [ ] I quote PR-AUC when positives are rare, and explain why
- [ ] My splits match deployment: time, group, or stratified
- [ ] Every fitted preprocessing step lives inside the training fold
- [ ] I report an interval and a baseline, not just a point estimate
- [ ] My threshold comes from a cost matrix
