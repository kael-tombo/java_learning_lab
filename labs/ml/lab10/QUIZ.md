# Model Evaluation - Quiz (15 Questions)

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

**Instructions.** Answer all 15 questions before reading the bold answer lines. Multiple choice, one best answer. Target: 12/15 before you move on to the mini project.

### Q1: What does precision measure?

A) Of true positives, how many were caught
B) Of those flagged, how many were correct
C) Overall correctness
D) The false positive rate

**Answer: B** - Precision is TP/(TP+FP): the purity of the flagged set.

---

### Q2: A model predicts the majority class always. Accuracy is 99%. Recall is?

A) 0.99
B) 1.0
C) 0
D) 0.01

**Answer: C** - If every positive is missed, recall is 0 no matter how good the accuracy looks.

---

### Q3: Which metric summarises PR better on rare positives?

A) ROC-AUC
B) Average precision
C) Accuracy
D) Log loss

**Answer: B** - AP stays meaningful where ROC's false positive rate flatters small-denominator effects.

---

### Q4: Why does ROC look optimistic on rare positives?

A) It uses log scale
B) FPR's denominator stays large while precision's shrinks
C) It ignores TN
D) It smooths the curve

**Answer: B** - FPR divides by the huge negative class, so many false positives barely move it.

---

### Q5: What does k-fold cross-validation assume?

A) Time independence
B) Rows are i.i.d. and exchangeable
C) Normality
D) Balanced classes

**Answer: B** - Grouped or temporal data needs a different split, or you leak.

---

### Q6: Why fit the scaler inside each fold?

A) Speed
B) Otherwise test distribution information leaks into training
C) Numerical stability
D) It is required by k-fold

**Answer: B** - Full-dataset scaling makes the CV score optimistic and does not match serving.

---

### Q7: What does forward-chaining ensure?

A) Random folds
B) Every fold trains only on data before its test window
C) Equal fold sizes
D) Balanced classes

**Answer: B** - It respects time order, which is the only honest protocol for forecasting.

---

### Q8: Precision 0.8 with recall 0.3 at n = 100. Is a rival at 0.81/0.31 better?

A) Yes, clearly
B) No — the difference is inside the noise
C) Yes, because precision is higher
D) It depends on the threshold

**Answer: B** - At n = 100 the standard error on precision is about 0.04, so 0.01 is meaningless.

---

### Q9: Why compare models on identical folds?

A) It is faster
B) It removes fold-to-fold variance from the comparison
C) It guarantees equal accuracy
D) It allows paired tests

**Answer: B** - Paired comparison cancels the dominant variance term.

---

### Q10: What is balanced accuracy?

A) Accuracy divided by classes
B) Mean of sensitivity and specificity
C) The average of precision and recall
D) Accuracy on a balanced sample

**Answer: B** - It weights both classes equally, which resists imbalance.

---

### Q11: F1 ignores which quantity?

A) False positives
B) False negatives
C) True negatives
D) Thresholds

**Answer: C** - F1 uses precision and recall only, so true negatives never affect it.

---

### Q12: Calibration means...

A) High AUC
B) Predicted probabilities match observed frequencies
C) Low variance
D) High recall

**Answer: B** - Calibration is about probability accuracy; AUC is about ranking.

---

### Q13: Which threshold should you ship?

A) 0.5
B) The one minimising expected cost from your cost matrix
C) The one maximising accuracy
D) The median score

**Answer: B** - The cost matrix, evaluated on validation folds, is the decision.

---

### Q14: What does a widening gap between training and CV error suggest?

A) Underfitting
B) High variance/overfitting
C) Data leakage
D) A better model

**Answer: B** - The gap is the classic variance signal; leakage shows up as the opposite pattern.

---

### Q15: Why report a baseline?

A) To fill space
B) So readers can judge whether the model's gain exceeds trivial predictors
C) Because metrics are meaningless alone
D) It is required by law

**Answer: B** - Against a trivial baseline you know how much of the performance is real.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
