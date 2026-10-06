# classical-ml-deep — Quiz

15 multiple-choice questions covering all ten modules. Answer key and score guide at the
bottom.

## Questions

**Q1.** You fit OLS and two of your features are nearly perfectly collinear
(condition number 1e12). What is true?
- A) The predictions become inaccurate
- B) The predictions stay accurate but coefficient magnitudes and signs become unstable
- C) R-squared always drops
- D) You must switch to logistic regression

**Q2.** Which loss should you optimize for logistic regression, and why?
- A) 0/1 error, because it matches the metric
- B) Mean squared error, because it is smooth
- C) Log-loss (cross-entropy), because it is a convex surrogate of 0/1 error and differentiable
- D) Hinge loss, because SVMs use it

**Q3.** In `gain(S, A) = H(S) - sum_v |S_v|/|S| * H(S_v)`, what problem does plain
information gain have that gain ratio fixes?
- A) It is computationally expensive
- B) It biases toward features with many distinct values
- C) It cannot handle continuous features
- D) It requires labeled data

**Q4.** Why does a random forest need both bootstrap sampling and random subspace
selection at each split?
- A) One of them reduces memory, the other reduces training time
- B) They are alternative ways to do the same thing
- C) Two independent randomness sources decorrelate the trees, which is what makes
      variance reduction work
- D) Random subspace is needed for missing values

**Q5.** CatBoost's ordered target statistics primarily addresses which problem?
- A) High-cardinality categorical memory
- B) Target leakage when computing category encodings from the full training set
- C) Slow inference
- D) Class imbalance

**Q6.** You must not compute PCA on the full dataset before splitting. Why?
- A) PCA is stochastic
- B) It leaks test-set variance into the learned projection
- C) PCA cannot handle test data
- D) It changes the label distribution

**Q7.** In boosting with second-order expansion, the optimal leaf value is `-G/(H+lambda)`.
What do `G` and `H` represent?
- A) G is the count of samples in the leaf; H is the entropy
- B) G is the sum of gradients in the leaf; H is the sum of Hessian (curvature) terms
- C) G is the gradient of the regularizer; H is the learning rate
- D) G and H are both hyperparameter names

**Q8.** You choose `k` for k-means. Which combination of diagnostics is most defensible?
- A) Elbow alone
- B) Silhouette alone
- C) Elbow, silhouette, and gap statistic reported together, with the choice argued
- D) The largest `k` that runs quickly

**Q9.** What does DBSCAN label a point that is not core and not within `eps` of any core
point?
- A) A border point
- B) Noise (outlier)
- C) Assigned to the nearest cluster
- D) A new cluster seed

**Q10.** You build a fraud detector where 0.5% of transactions are fraud and a naive
classifier reports 99.5% accuracy. What should you report instead?
- A) Balanced accuracy
- B) Precision-recall AUC and the confusion matrix at the shipping threshold
- C) F1 at the default threshold
- D) Log loss

**Q11.** Two models have identical training MAE. One has wildly different coefficients
than the other. This is a symptom of:
- A) Too little data
- B) Multicollinearity — flat in prediction space, unstable in coefficient space
- C) A learning-rate bug
- D) Wrong label encoding

**Q12.** Which statement about the RBF kernel parameter `gamma` is correct?
- A) It is scale-invariant and needs no tuning
- B) It must be tuned; the library default `1/(p*var)` is frequently wrong
- C) Larger gamma always means better generalization
- D) It only affects the kernel matrix diagonal

**Q13.** Your Isolation Forest scores an anomaly 0.42, below many normal points. What is
the correct interpretation?
- A) The anomaly is not anomalous
- B) Isolation Forest scores are relative within the fitted forest; the decision is a
      threshold, and the rank alone is not the verdict
- C) Isolation Forest cannot detect this class
- D) The data must be standardized again

**Q14.** Applying PCA to a dataset where the highest-variance direction is nuisance noise
typically causes:
- A) Faster convergence of the classifier
- B) Loss of the label-relevant signal, because PCA maximizes variance rather than class
      separation
- C) An increase in explained variance
- D) Duplicate columns

**Q15.** Which of these is the strongest justification for starting a tabular ML project
with a logistic regression baseline?
- A) It is always the most accurate
- B) It is fast, interpretable, well-calibrated, and reveals how much signal is linearly
      available before adding capacity
- C) It does not require feature engineering
- D) It guarantees no overfitting

## Answer Key

| Q | Answer | Why |
|---|--------|-----|
| 1 | B | Collinearity inflates coefficient variance; predictions from the same span barely move. |
| 2 | C | 0/1 error is non-differentiable; log-loss is convex and penalizes confident errors logarithmically. |
| 3 | B | Gain ratio divides by `H(A)`, removing the high-cardinality bias. |
| 4 | C | Decorrelation is the mechanism; correlated trees' averaged errors do not cancel. |
| 5 | B | Ordered statistics compute encodings from prior rows, avoiding target leakage in CV. |
| 6 | B | Any statistic fit on all data leaks test information into training. |
| 7 | B | `G` sums gradients, `H` sums second derivatives; `lambda` controls leaf complexity. |
| 8 | C | Each diagnostic answers a different question; disagreement should be reported. |
| 9 | B | Noise points are dropped, not clustered. |
| 10 | B | Accuracy is dominated by the majority class; PR-AUC and the operating-point confusion matrix are informative. |
| 11 | B | The prediction-identifiable-but-coefficient-unstable signature is collinearity. |
| 12 | B | `gamma` sets the kernel width and must be tuned against CV. |
| 13 | B | Anomaly scores are ranks within the fitted model; only a calibrated threshold yields a decision. |
| 14 | B | PCA is unsupervised; it optimizes variance, not discriminability. |
| 15 | B | A baseline quantifies available signal and anchors every later gain against a trivial model. |

## Score Guide

| Score | Verdict |
|-------|---------|
| 15/15 | Ready to lead a classical ML project. Start module 06 and 10 for depth. |
| 12-14 | Solid. Revisit the questions you missed and read the linked module doc. |
| 9-11 | Understands the mechanics, not yet the failure modes. Redo Q3, Q5, Q9, Q13. |
| 6-8 | Re-read THEORY.md, then redo EXERCISES for modules 01, 04, 07. |
| 0-5 | Restart with modules 01, 02, and 08 before the boosting material. |

## Scoring Notes

- **Partial credit**: none. These are single-answer questions.
- **Retry policy**: retake after re-reading. Track which module each miss belongs to.
- **Mastery threshold**: 13/15 and zero misses on Q1, Q5, Q9, Q10.
