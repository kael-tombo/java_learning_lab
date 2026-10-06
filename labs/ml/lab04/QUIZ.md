# Support Vector Machines - Quiz (15 Questions)

**Track:** ml  |  **Lab:** lab04  |  **Level:** Advanced

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

### Q1: The SVM decision boundary depends only on...

A) All training points equally
B) The support vectors
C) The class priors
D) The feature scaling

**Answer: B** - w = Σαᵢyᵢxᵢ, and points with αᵢ = 0 contribute nothing.

---

### Q2: Maximising the margin is equivalent to...

A) Minimising the number of misclassifications
B) Minimising 0.5||w||²
C) Maximising C
D) Maximising the number of support vectors

**Answer: B** - Margin width is 2/||w||, so a small ||w|| is a wide margin.

---

### Q3: In the soft-margin formulation, C controls...

A) The kernel bandwidth
B) The penalty on margin violations
C) The class prior
D) The feature dimension

**Answer: B** - Larger C buys fewer violations at the cost of a narrower margin.

---

### Q4: What is gamma in an RBF kernel?

A) The regularisation strength
B) A length scale in the squared distance
C) The class weight
D) The convergence tolerance

**Answer: B** - exp(−γ||x−z||²) — large gamma means local influence only.

---

### Q5: Why must features be standardised for RBF?

A) It improves accuracy
B) Otherwise one feature's units dominate the distance
C) It is required by the dual
D) It reduces the number of features

**Answer: B** - Squared distance mixes units unless they are comparable.

---

### Q6: The kernel trick's benefit is...

A) Faster training
B) Using a feature map without computing it
C) Guaranteed better accuracy
D) Removing the need for labels

**Answer: B** - Only pairwise inner products are ever needed, so the map can be infinite-dimensional.

---

### Q7: Which point is a support vector?

A) Any misclassified point
B) Any point with αᵢ > 0
C) Any point with the smallest norm
D) The class centroid

**Answer: B** - Positive dual coefficients define the boundary; the rest are irrelevant.

---

### Q8: A very high support-vector fraction suggests...

A) A well-regularised model
B) Memorisation and likely overfitting
C) A large margin
D) Perfect calibration

**Answer: B** - When nearly every point is on the margin, the fit is following noise.

---

### Q9: SVM decision values are...

A) Probabilities
B) Signed margins needing calibration
C) Class priors
D) Distances in input space

**Answer: B** - They are signed hyperplane values; Platt scaling is the standard wrapper.

---

### Q10: The binding practical limit on kernel SVM size is...

A) Training time
B) Memory for the O(n²) kernel matrix
C) Feature count
D) Class count

**Answer: B** - 8n² bytes of doubles is what runs out first.

---

### Q11: Complementary slackness implies that a point with 0 < α < C is...

A) Inside the margin
B) Exactly on the margin
C) Correctly classified outside the margin
D) Removed from the dataset

**Answer: B** - Interior alphas must satisfy yᵢf(xᵢ) = 1 exactly.

---

### Q12: A polynomial kernel (xᵀz + r)^d corresponds to...

A) A linear model with d features
B) A d-degree polynomial expansion
C) An RBF approximation
D) A random projection

**Answer: B** - The expansion is exactly the monomials of degree up to d with binomial weights.

---

### Q13: Why does SMO update two alphas at a time?

A) To parallelise
B) Because the two-variable subproblem has a closed-form solution
C) To reduce memory
D) To enforce the sign of w

**Answer: B** - With one variable the constraint couples it to all the others; with two it is quadratic.

---

### Q14: Which is true of the hard-margin problem on separable data?

A) It has a unique solution with a unique margin
B) It has no solution if points overlap
C) C must be infinite
D) The kernel must be linear

**Answer: A** - Separability guarantees feasibility and convexity gives a unique optimum.

---

### Q15: Choosing gamma by leaving it at its default is...

A) Always fine for small data
B) Risky, because the default is arbitrary relative to your feature scale
C) Optimal
D) Equivalent to linear regression

**Answer: B** - Set gamma from the feature variance or sweep it; the default knows nothing about your units.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
