# Principal Component Analysis - Quiz (15 Questions)

**Track:** ml  |  **Lab:** lab08  |  **Level:** Intermediate

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

**Instructions.** Answer all 15 questions before reading the bold answer lines. Multiple choice, one best answer. Target: 12/15 before you move on to the mini project.

### Q1: What does the first principal component maximise?

A) The mean of the features
B) The variance of the projected data
C) The number of features
D) The correlation with the target

**Answer: B** - It is the direction of maximum variance in the centred data.

---

### Q2: Why must data be centred before PCA?

A) To avoid negative eigenvalues
B) Otherwise the first component points at the mean direction
C) To speed up the eigen solver
D) It does not matter

**Answer: B** - Without centring, PC1 captures the offset rather than the structure.

---

### Q3: When should features be standardised first?

A) Never
B) When units or variances differ materially
C) Only for tree models
D) Only when p is small

**Answer: B** - Otherwise total variance rather than correlation structure is maximised.

---

### Q4: Explained variance ratio for component i is...

A) lambda_i / p
B) lambda_i / sum(lambda)
C) sqrt(lambda_i)
D) cumulative variance

**Answer: B** - It is the share of total variance (the trace of the covariance) held by that component.

---

### Q5: Is the sign of a principal component meaningful?

A) Yes, positive means better
B) No, it is arbitrary
C) Only for PC1
D) Only after whitening

**Answer: B** - Eigenvectors are defined up to sign, so fix a convention for reproducibility.

---

### Q6: Why prefer SVD over eigendecomposition?

A) It is exact
B) It never forms the covariance matrix, avoiding squared conditioning
C) It uses labels
D) It handles categoricals

**Answer: B** - Working on X directly avoids the p×p matrix and its squared condition number.

---

### Q7: Loading versus feature importance

A) They are identical
B) A loading is a direction coefficient, not a contribution measure
C) Loadings require labels
D) Importance requires scaling

**Answer: B** - Importance asks what the model uses; a loading asks where the component points.

---

### Q8: When does PCA hurt a classifier?

A) When the data is small
B) When high-variance directions are noise rather than signal
C) Always
D) Never with correlated features

**Answer: B** - PCA is unsupervised, so it can preserve exactly the wrong variance.

---

### Q9: Reconstruction error after dropping components equals...

A) The mean squared error
B) The sum of the dropped eigenvalues
C) The largest eigenvalue
D) Zero

**Answer: B** - Orthogonality makes the discarded energy exactly the sum of dropped eigenvalues.

---

### Q10: PCA is unsupervised, so...

A) It cannot be used before supervised models
B) It can preserve variance unrelated to the label
C) It always improves accuracy
D) It requires a target column

**Answer: B** - That blindness is why k is best chosen by downstream validation.

---

### Q11: What is TruncatedSVD used for?

A) Whitening
B) Sparse matrices like term counts without centring
C) Non-linear structure
D) Classification directly

**Answer: B** - Centring densifies a sparse matrix; truncated SVD avoids that entirely.

---

### Q12: Why can PCA loadings be unstable?

A) Correlated features let the weight be split arbitrarily among them
B) The solver is buggy
C) Loadings depend on labels
D) They are always stable

**Answer: A** - The component is stable even though individual coefficients are not.

---

### Q13: The 95% cumulative-variance rule is...

A) A mathematical law
B) A convention and a poor substitute for validation
C) Required by scikit-learn
D) Optimal for classification

**Answer: B** - It is a starting point; validation error should decide k.

---

### Q14: Whitening does what?

A) Centres the data only
B) Scales each component to unit variance
C) Removes the mean
D) Adds label information

**Answer: B** - It removes residual variance differences, changing which points look close in distance.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
