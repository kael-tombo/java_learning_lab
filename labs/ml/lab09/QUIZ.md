# Gradient Boosting - Quiz (15 Questions)

**Track:** ml  |  **Lab:** lab09  |  **Level:** Advanced

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

### Q1: What does gradient boosting fit at each round?

A) Sample weights
B) The negative gradient of the loss
C) The full gradient of the model parameters
D) Residuals of the final model

**Answer: B** - It fits the negative gradient with respect to the current prediction, which equals residuals for squared error.

---

### Q2: How does gradient boosting differ from AdaBoost?

A) It uses different trees
B) It fits gradients instead of reweighting samples
C) It is faster
D) It cannot classify

**Answer: B** - AdaBoost reweights; gradient boosting fits gradients, which generalises to any loss.

---

### Q3: The learning rate eta...

A) Controls tree depth
B) Scales each weak learner's contribution
C) Sets the number of bins
D) Determines the loss function

**Answer: B** - Eta is shrinkage on each round's update.

---

### Q4: Why are trees shallow in boosting?

A) Memory
B) Boosting adds interaction depth across rounds
C) Shallow trees are more accurate alone
D) Required by the library

**Answer: B** - Each shallow tree adds one level of interaction; stacking rounds builds the complexity.

---

### Q5: Early stopping is essentially...

A) Halting training when the gradient vanishes
B) Choosing the number of rounds by validation loss
C) Stopping when memory runs out
D) Truncating trees

**Answer: B** - The round count is a hyperparameter chosen on validation data.

---

### Q6: Why does boosting need a validation split?

A) To compute training loss
B) To choose the number of rounds without touching the test set
C) For SHAP values
D) To initialise F₀

**Answer: B** - The round count must be selected on data not used for fitting.

---

### Q7: What is stochastic gradient boosting?

A) Using a random learning rate
B) Subsampling rows per tree
C) Dropping features per tree
D) Adding noise to the target

**Answer: B** - Row subsampling decorrelates the trees and reduces variance.

---

### Q8: TreeSHAP is attractive because it is...

A) Approximate
B) Exact and additive
C) Model-free
D) Unsupervised

**Answer: B** - Tree ensembles admit exact Shapley values via path enumeration, and the additivity identity holds exactly.

---

### Q9: Gain-based importance is unreliable when...

A) The model is deep
B) Features are correlated, so credit is split arbitrarily
C) There are many bins
D) The target is skewed

**Answer: B** - Correlated features share credit unpredictably between them.

---

### Q10: Histogram binning helps because it...

A) Improves accuracy
B) Reduces candidate splits to a few hundred per feature
C) Removes the need for early stopping
D) Allows larger eta

**Answer: B** - It trades a small precision loss for an order of magnitude in speed.

---

### Q11: The initial prediction F₀ for squared error is...

A) Zero
B) The mean of the targets
C) The log-odds
D) The first feature

**Answer: B** - The constant minimising the loss with no features is the mean target.

---

### Q12: Overfitting in boosting shows up as...

A) Rising training loss
B) Training loss falling while validation loss rises
C) Fewer trees
D) Lower eta

**Answer: B** - The classic signature is a monotonically falling train curve with a turning validation curve.

---

### Q13: Which loss makes boosting robust to outliers?

A) Squared error
B) Absolute error or Huber
C) Log loss
D) Any, equally

**Answer: B** - Squared error is outlier-dominated; Huber or absolute error down-weights extremes.

---

### Q14: Increasing rounds with eta fixed is equivalent to...

A) Increasing eta
B) Decreasing eta (with more compute)
C) Increasing depth
D) Adding features

**Answer: B** - Smaller eta with more rounds approximates the same total shrinkage more finely.

---

### Q15: What does SHAP additivity let you do?

A) Retrain faster
B) Verify that explanations account for the whole prediction
C) Remove the baseline
D) Avoid cross-validation

**Answer: B** - If the contributions sum to prediction minus baseline, nothing is unexplained.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
