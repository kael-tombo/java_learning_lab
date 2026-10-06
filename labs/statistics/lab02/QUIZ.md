# Probability Distributions - Quiz (15 Questions)

**Track:** statistics  |  **Lab:** lab02  |  **Level:** Foundational

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

### Q1: Which distribution models waiting time between Poisson events?

A) Normal
B) Exponential
C) Binomial
D) Poisson

**Answer: B** - The exponential is continuous and memoryless; the Poisson counts events in an interval.

---

### Q2: What is the defining property of a Poisson count?

A) Constant mean
B) Variance equal to mean, from a constant rate with independent events
C) Symmetry
D) Bounded support

**Answer: B** - Variance equals mean, so a ratio above one indicates the assumption failed.

---

### Q3: What does overdispersion tell you?

A) Sampling error
B) The event rate varies over time, so events cluster
C) The sample is too small
D) The mean is biased

**Answer: B** - A non-constant rate breaks the model, usually toward a negative binomial.

---

### Q4: When is the normal approximation to the binomial valid?

A) Always
B) When np and n(1−p) are both about 5 or more
C) When n exceeds 1000
D) When p is near 0.5

**Answer: B** - Small expected counts in a tail invalidate the approximation exactly where it matters.

---

### Q5: What does the central limit theorem require?

A) Normality of the data
B) Independence and finite variance, not normality
C) A large sample
D) Symmetry

**Answer: B** - Normality of the inputs is explicitly not required.

---

### Q6: Why use the complementary error function for the normal CDF?

A) Speed
B) 1 minus the CDF loses relative accuracy in the tail
C) Memory
D) Precision near zero

**Answer: B** - The subtraction cancels; erfc keeps the tail accurate.

---

### Q7: Why does Poisson PMF evaluation overflow?

A) Large sample
B) k! exceeds double range around k = 170
C) Slow generator
D) Rounding

**Answer: B** - Log-space evaluation with a log-gamma function avoids forming k!.

---

### Q8: What is the memoryless property?

A) P(X = x) declines exponentially
B) Survival probability does not depend on time already elapsed
C) Mean equals variance
D) Independent events

**Answer: B** - It is the assumption behind exponential backoff.

---

### Q9: Box-Muller transforms...

A) One uniform into one normal
B) Two independent uniforms into two normals
C) Normals into uniforms
D) Counts into rates

**Answer: B** - It exploits the polar form of the bivariate normal.

---

### Q10: Why compare CDFs rather than densities?

A) CDFs are cheaper
B) A density value is not a probability
C) Densities do not exist for discrete data
D) CDFs are smoother

**Answer: B** - Conclusions about likelihood need cumulative probability.

---

### Q11: What does a Monte Carlo estimate require to be trustworthy?

A) Many samples
B) A seed and an interval across independent runs
C) Normal data
D) A closed form

**Answer: B** - An unreproducible estimate with no interval cannot be checked.

---

### Q12: When should you use a Poisson rather than a binomial?

A) When trials are dependent or numerous with a small rate
B) Never
C) When you need a mean and variance
D) For continuous measurements

**Answer: A** - The Poisson is the limit of the binomial as n grows and p shrinks with np fixed.

---

### Q13: What is a continuity correction for?

A) Correcting rounding
B) Adjusting a discrete boundary when approximating with a continuous distribution
C) Reducing variance
D) Fixing skewness

**Answer: B** - P(X ≤ k) is approximated by Phi((k + 0.5 − np)/sqrt(np(1−p))).

---

### Q14: How do you estimate a Poisson rate?

A) The median of the counts
B) The sample mean of the counts, by maximum likelihood or moments
C) The variance
D) The maximum count

**Answer: B** - Both estimators give the sample mean, which is the Poisson's sufficient statistic.

---

### Q15: Why does an unseeded sampler undermine a Monte Carlo result?

A) It is slower
B) The estimate cannot be reproduced or checked
C) It biases the result
D) It uses more memory

**Answer: B** - Reproducibility is what turns a number into a result you can defend.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
