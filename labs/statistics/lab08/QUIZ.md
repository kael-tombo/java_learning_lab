# Experimental Design - Quiz (15 Questions)

**Track:** statistics  |  **Lab:** lab08  |  **Level:** Advanced

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

### Q1: What is an estimand?

A) The sample size
B) The precise quantity to be estimated, defined before data collection
C) The p-value
D) The treatment label

**Answer: B** - Defining it first prevents the analysis answering a different question.

---

### Q2: Why compute sample size before collecting data?

A) For cost planning
B) Power depends on n, effect and variance; collecting first risks an uninformative study
C) To satisfy ethics
D) To reduce variance

**Answer: B** - A study that could never detect the effect should not be run.

---

### Q3: What does blocking achieve?

A) Reducing cost
B) Removing between-unit variation from the error term by randomising within homogeneous groups
C) Increasing power for free
D) Simplifying analysis

**Answer: B** - The gain comes from a smaller error variance.

---

### Q4: When is a randomised block design appropriate?

A) Homogeneous units
B) When units differ systematically and that variation is nuisance
C) Large samples
D) Binary outcomes

**Answer: B** - Machine, operator, location and day are classic blocking variables.

---

### Q5: Why run a factorial rather than separate experiments?

A) It is cheaper
B) Each treatment is compared across both levels of the other factor, estimating main effects and interaction together
C) It reduces bias
D) It is always more powerful

**Answer: B** - Cross-level comparison is where the efficiency comes from.

---

### Q6: What does a significant interaction mean for main effects?

A) They are still valid
B) The factor's effect depends on the other factor's level, so marginal means mislead
C) The design failed
D) Sample size was too small

**Answer: B** - Report simple effects within levels instead.

---

### Q7: What does confounding prevent?

A) Precise estimation
B) Separating the effects of two factors that vary together
C) Randomisation
D) Blocking

**Answer: B** - No sample size fixes an unidentifiable design.

---

### Q8: Why inflate a pilot variance before computing n?

A) To be conservative
B) Small pilots give noisy, often biased-low variance estimates
C) To match a formula
D) It is required

**Answer: B** - Under-estimated variance is the most common reason studies are underpowered.

---

### Q9: How do you verify randomisation happened?

A) By inspection
B) By auditing realised arm sizes against the design
C) By seed recording alone
D) By a significance test on the data

**Answer: B** - Arm-size counts catch a broken assignment immediately.

---

### Q10: What is the minimum detectable effect?

A) The observed effect
B) The smallest effect the design can detect at its size and power
C) The target effect
D) The power itself

**Answer: B** - It is the design's resolution, and it should be compared to what matters.

---

### Q11: Why can blocking reduce required n by an order of magnitude?

A) It removes bias
B) Within-block correlation rho removes a fraction rho of the error variance
C) It reduces cost
D) It increases the effect size

**Answer: B** - The reduction factor is 1 - rho.

---

### Q12: What is replication for in a factorial design?

A) Precision of cell means
B) Separating the interaction from residual variation
C) Bias reduction
D) Power for main effects

**Answer: B** - Without within-cell replication the interaction is confounded with error.

---

### Q13: What does pre-specifying the analysis prevent?

A) Overfitting
B) Choosing the analysis after seeing results, which inflates error
C) Small samples
D) Confounding

**Answer: B** - Analysis flexibility is a source of false positives if left open.

---

### Q14: What is the unit of randomisation?

A) The observation
B) The entity independently assigned to treatments, which determines what the design can support
C) The cell
D) The time point

**Answer: B** - Randomising units but analysing others causes pseudoreplication.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
