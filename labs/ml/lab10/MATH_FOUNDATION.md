# Model Evaluation - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `Accuracy = (TP+TN)/N` | Accuracy - misleading under imbalance |
| `Precision = TP/(TP+FP)` | Precision - of flagged, how many were right |
| `Recall = TP/(TP+FN)` | Recall / TPR - of true positives, how many were caught |
| `F1 = 2PR/(P+R)` | F1 - harmonic mean; ignores TN |
| `Fβ = (1+β²)PR/(β²P + R)` | F-beta - weights recall when β > 1 |
| `AUC = P(score_pos > score_neg)` | ROC AUC - threshold-free ranking quality |
| `AP = Σ (R_k − R_{k−1}) P_k` | Average precision - PR summary; better than AUC when rare positives |
| `CI ≈ metric ± 1.96 · SE` | Normal CI for a proportion - rough interval on a metric estimate |

## Why the Math Matters

Evaluation is where the mathematics of estimation meets the economics of error. The confusion matrix gives you the counts, the curves give you the trade-off, and the interval tells you whether your comparison is real.


---

## 1. From counts to metrics

```text
TP, FP, FN, TN from the confusion matrix
P = TP/(TP+FP),  R = TP/(TP+FN)
F1 = 2PR/(P+R),  F_beta = (1+b^2)PR/(b^2 P + R)
```

Every metric is a ratio of cells, so the confusion matrix is the only thing you need to compute. F1's harmonic mean means precision and recall must both be decent to score well.

**Worked example.** TP = 90, FP = 10, FN = 40: precision = 0.90, recall = 0.69, F1 = 0.78. Accuracy on a 1,000-row set with TN = 860 would read 0.95 while recall is below 0.7.


---

## 2. Accuracy versus imbalance

```text
accuracy of the trivial predictor = 1 - pi, where pi is the positive rate
at pi = 0.01: accuracy = 0.99, recall = 0
useful metrics must be compared against this floor
```

The trivial predictor sets the floor any real model must beat. At low prevalence, only recall-type metrics discriminate, which is why balanced accuracy and F-beta appear in class-imbalance work.

**Worked example.** 1% positives, 10,000 rows: trivial accuracy 0.99. A model with recall 0.3 and precision 0.6 has accuracy 0.966 — worse than trivial, but far more useful. Accuracy hides that entirely.


---

## 3. ROC and PR curves

```text
ROC: sweep threshold, plot TPR = TP/(TP+FN) against FPR = FP/(FP+TN)
PR:  sweep threshold, plot precision = TP/(TP+FP) against recall
AUC_ROC = P(s_pos > s_neg)
```

With rare positives, FPR has a tiny denominator, so it stays small even when many false positives are generated. Precision's denominator is the flagged set, so it degrades visibly.

**Worked example.** 1,000 rows, 10 positives. At recall 0.8, ROC shows FPR = 0.001 (one FP) — excellent. PR shows precision = 0.62, which is the number a reviewer actually experiences.


---

## 4. Average precision

```text
AP = sum_k (R_k - R_{k-1}) P_k, over thresholds sorted by descending score
AP approximates the PR area and is comparable across datasets
```

AP is a step-wise summary of the PR curve that stays meaningful on small rare-positive sets, where trapezoidal integration over precision is noisy.

**Worked example.** 10 positives in 1,000 rows: AP = 0.71 while AUC = 0.94. The gap is the story — the model ranks well but its top-of-list precision is mediocre.


---

## 5. Variance of a metric estimate

```text
SE(p_hat) = sqrt(p(1-p)/n) for a proportion
metric CI ~ estimate ± 1.96 SE
compare models with paired tests on the same folds
```

Sampling error is often larger than the difference you are chasing. Paired comparisons on identical folds remove the fold-to-fold variance, which is the dominant term.

**Worked example.** Precision 0.80 on n = 100: SE = 0.04, so the 95% interval is 0.72–0.88. A 0.3% improvement over another model is far inside that noise.


---

## 6. Cross-validation variance

```text
variance of the k-fold estimate ~ sigma^2 / (k * n/k) = sigma^2 / n
adding folds reduces variance from partition noise, not sampling noise
repeated CV reduces both but costs k * r fits
```

More folds reduce the noise from how the data was partitioned. They do not add data. Going from 5-fold to 10-fold rarely changes the estimate much; repeating with different seeds does reduce variance.

**Worked example.** 10-fold CV on 5,000 rows estimates accuracy within roughly ±1%. Ten-fold instead of five changes the mean by about 0.1–0.3%, but a repeated 5-fold with 5 seeds tightens the reported interval noticeably.


---

## Cheat Sheet

- `Accuracy = (TP+TN)/N` - Accuracy
- `Precision = TP/(TP+FP)` - Precision
- `Recall = TP/(TP+FN)` - Recall / TPR
- `F1 = 2PR/(P+R)` - F1
- `Fβ = (1+β²)PR/(β²P + R)` - F-beta
- `AUC = P(score_pos > score_neg)` - ROC AUC
- `AP = Σ (R_k − R_{k−1}) P_k` - Average precision
- `CI ≈ metric ± 1.96 · SE` - Normal CI for a proportion

## Numerical Traps

- Computing precision with a zero denominator (no predicted positives) without guarding.
- Reporting accuracy as a percentage when the task is binary and rare-positive.
- Integrating PR with the trapezoid rule on a small rare-positive set instead of using average precision.
- Comparing two models across different fold assignments rather than paired folds.
- Averaging precision across classes without stating whether it is macro or weighted.

## Self-Check Problems

1. Compute precision, recall, F1, specificity and balanced accuracy from a given confusion matrix.
2. Show that the trivial predictor's accuracy equals 1 - pi and compute it for pi = 0.001, 0.01, 0.1.
3. Compute ROC-AUC by the rank formula and by trapezoidal integration on a scored dataset; assert equality.
4. Compute average precision for a 10-positive dataset and compare with trapezoidal PR integration.
5. Compute the 95% CI for precision 0.8 at n = 50, 100, 500 and 5,000; explain when the difference becomes decisive.
