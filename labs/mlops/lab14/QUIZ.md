# AutoML Pipelines - Quiz (15 Questions)

**Track:** mlops  |  **Lab:** lab14  |  **Level:** Advanced

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

### Q1: Why is random search often better than grid search per trial?

A) It is exhaustive
B) Most hyperparameters are unimportant, and random sampling covers important dimensions evenly
C) It guarantees the optimum
D) It is faster per trial

**Answer: B** - Grid wastes budget on unimportant combinations.

---

### Q2: What is successive halving?

A) Random restart
B) Promoting promising configurations to more resources while killing bad ones
C) Halving the batch size
D) A pruning heuristic on features

**Answer: B** - Budget allocation is where most real tuning efficiency comes from.

---

### Q3: What does expected improvement measure?

A) Runtime
B) Expected gain over the best result so far, trading mean against uncertainty
C) Gradient norm
D) Memory usage

**Answer: B** - It is an acquisition function that asks how much better this trial might be.

---

### Q4: Why search learning rates logarithmically?

A) It is faster
B) The optimum spans orders of magnitude, and linear grids waste resolution
C) It avoids overfitting
D) It is required by the framework

**Answer: B** - Linear grids put almost all trials in a region that is never competitive.

---

### Q5: What is validation overfitting?

A) Overfitting the training data
B) Selecting the best of many trials on one validation split and reporting an inflated score
C) Using too many features
D) Early stopping too late

**Answer: B** - Selecting a maximum of many noisy estimates is biased upward.

---

### Q6: How do you fix validation overfitting?

A) More trials
B) Nested cross-validation or a final untouched holdout used once
C) Lower the learning rate
D) Use a bigger model

**Answer: B** - The estimate must come from data not used for selection.

---

### Q7: Why prune the search space?

A) To look tidy
B) Each removed dimension is budget you can spend elsewhere
C) To reduce memory
D) Because grids require it

**Answer: B** - Pruning dominated configurations is free efficiency.

---

### Q8: What is Hyperband?

A) A loss function
B) Successive halving across multiple brackets to hedge the resource schedule
C) A sampler
D) A pruning algorithm

**Answer: B** - It hedges not knowing in advance which resource schedule suits the problem.

---

### Q9: Why stop on a smoothed metric?

A) It looks nicer
B) Raw metrics are noisy, so raw stopping decisions ride on spikes
C) It is faster
D) It reduces memory

**Answer: B** - Stopping on a favourable spike loses budget on configurations that were going to lose anyway.

---

### Q10: Why repeat seeds?

A) To fill the log
B) Variance across seeds can exceed the difference you are trying to detect
C) To increase sample size
D) Because the framework requires it

**Answer: B** - Without variance, an apparent 0.3% gap may be pure seed luck.

---

### Q11: When is Bayesian optimisation worth the complexity?

A) Never
B) When each trial is expensive, so a surrogate pays for itself in saved trials
C) When trials are cheap
D) For linear models only

**Answer: B** - Surrogate cost is negligible relative to expensive trials.

---

### Q12: What should a tuning report always include?

A) The best configuration
B) A baseline comparison, the search space, the budget, and a final estimate on held-out data
C) The runtime only
D) The team name

**Answer: B** - A tuning result without a baseline and an honest final estimate is not interpretable.

---

### Q13: What is selection bias in terms of trials?

A) E[selected] > E[true best on fresh data]
B) The search finding a genuinely better model
C) Overfitting features
D) Learning rate too high

**Answer: A** - The bias grows with the number of trials and with score noise.

---

### Q14: Why should AutoML automate the search but not the judgement?

A) Cost
B) Search is tedious and repetitive; evaluation protocol and leakage decisions need human ownership
C) Search is easy
D) Judgement cannot be coded

**Answer: B** - Automating the parts that need judgement is how AutoML produces fast wrong answers.

---

### Q15: What is the practical effect of a larger search budget?

A) Better model, always
B) More trials improve the search but also inflate the reported score through selection bias
C) Faster training
D) Less memory

**Answer: B** - The true optimum improves slowly while the reported number inflates quickly.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
