# Naive Bayes Classifier - Quiz (15 Questions)

**Track:** ml  |  **Lab:** lab06  |  **Level:** Intermediate

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

### Q1: The 'naive' assumption is...

A) Classes are equally likely
B) Features are conditionally independent given the class
C) Features are normally distributed
D) Labels are binary

**Answer: B** - Conditional independence is the assumption; class balance is a prior, not the assumption.

---

### Q2: Which variant fits binary term indicators?

A) Gaussian
B) Multinomial
C) Bernoulli
D) Any of them

**Answer: C** - Bernoulli models each term's presence or absence, plus a document-length term.

---

### Q3: Laplace smoothing prevents...

A) Slow training
B) Zero probabilities for unseen values
C) Class imbalance
D) Overfitting to the majority class

**Answer: B** - Add-alpha keeps every token possible in every class.

---

### Q4: Why is probability-space scoring unsafe for text?

A) It is slower
B) Products of many small probabilities underflow to zero
C) It cannot handle multi-byte characters
D) It ignores the prior

**Answer: B** - Log space is mathematically identical and numerically safe.

---

### Q5: What happens to the argmax when P(x) is dropped?

A) Nothing
B) The argmax changes because P(x) is class dependent
C) It becomes random
D) It becomes the prior

**Answer: A** - P(x) is a constant across classes for a fixed x, so it cannot reorder them.

---

### Q6: Why are NB posteriors overconfident?

A) The prior is wrong
B) The independence assumption makes the likelihood ratio too extreme
C) Smoothing adds mass to unseen tokens
D) The variance estimate is biased

**Answer: B** - Multiplying over many features compounds independence error into a sharper ratio.

---

### Q7: Gaussian NB estimates per class...

A) A single variance
B) A mean and a variance per feature
C) A covariance matrix
D) A density estimate via KDE

**Answer: B** - Per-class per-feature mean and variance gives a diagonal-covariance discriminant.

---

### Q8: When does NB beat logistic regression?

A) Very large datasets
B) Small datasets with many features, especially text
C) Continuous data only
D) When labels are continuous

**Answer: B** - Low variance from few parameters makes it strong in low-data regimes.

---

### Q9: NB training is best described as...

A) Iterative optimisation
B) Counting sufficient statistics
C) Gradient descent
D) Cross-validation

**Answer: B** - Per-class totals and feature counts are all that is needed, so updates are incremental.

---

### Q10: Which is NOT true of multinomial NB?

A) It uses term counts
B) It applies smoothing
C) It can handle binary features
D) It ignores document length entirely

**Answer: C** - Multinomial uses counts and is insensitive to length; that is a known weakness versus Bernoulli.

---

### Q11: P(x|y) is the...

A) Posterior
B) Likelihood
C) Prior
D) Evidence

**Answer: B** - Likelihood is the conditional density of the data given the class; the posterior is the reverse.

---

### Q12: How do you get calibrated probabilities from NB?

A) Clip the posterior
B) Platt-scale the log-odds score
C) Raise to a power
D) Average with the prior

**Answer: B** - A one-dimensional logistic fit on the log-odds recovers most of the calibration error.

---

### Q13: Adding alpha to smoothing counts...

A) Speeds up training
B) Interpolates between the MLE and a uniform prior
C) Removes the prior term
D) Reduces class imbalance

**Answer: B** - alpha = 0 is the MLE; alpha tending to infinity approaches uniform over the vocabulary.

---

### Q14: Why fit the vectoriser inside the training fold?

A) Speed
B) Otherwise the vocabulary sees test-fold text and leaks it
C) Memory
D) It changes the smoothing

**Answer: B** - Vocabulary leakage is a real source of optimistic accuracy on text tasks.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
