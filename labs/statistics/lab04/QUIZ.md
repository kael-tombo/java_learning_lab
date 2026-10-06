# ANOVA - Quiz (15 Questions)

**Track:** statistics  |  **Lab:** lab04  |  **Level:** Intermediate

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

### Q1: What does an F-statistic near 1 indicate?

A) Groups are identical
B) Between-group variance equals within-group variance, as a true null predicts
C) The test failed
D) The effect is large

**Answer: B** - F is a variance ratio, so 1 is the null's expectation.

---

### Q2: What does eta-squared measure?

A) Statistical significance
B) The proportion of total variance explained by the factor
C) The sample size
D) The power

**Answer: B** - It is the effect size that keeps a large-n significant result from being over-read.

---

### Q3: Why run post-hoc tests after a significant ANOVA?

A) To increase power
B) The omnibus test says something differs, not which; comparisons need family-wise error control
C) To reduce error
D) To increase sample size

**Answer: B** - Uncontrolled pairwise tests inflate the family-wise error rate.

---

### Q4: How does Bonferroni differ from Tukey?

A) Bonferroni is less conservative
B) Bonferroni divides alpha by the number of comparisons; Tukey uses the studentised range
C) They are identical
D) Tukey requires normality

**Answer: B** - Bonferroni is valid by the union bound; Tukey exploits the joint distribution.

---

### Q5: What violates ANOVA assumptions most often?

A) Too much data
B) Unequal variances and non-normal residuals
C) The number of groups
D) Replication

**Answer: B** - Both are common at small n and both have well-known corrections.

---

### Q6: What is Welch's ANOVA for?

A) Non-normality
B) Unequal variances, with fractional error degrees of freedom
C) Repeated measures
D) Planned contrasts

**Answer: B** - It down-weights noisy groups and widens the interval conservatively.

---

### Q7: When does the interaction term matter most?

A) When main effects are large
B) When the effect of one factor depends on the level of the other
C) When n is large
D) When residuals are normal

**Answer: B** - Significant interaction means main effects cannot be read on their own.

---

### Q8: Why can a significant ANOVA have a negligible effect size?

A) It cannot
B) With large n any small difference becomes statistically significant
C) Because eta-squared is unreliable
D) Because p is miscomputed

**Answer: B** - The test statistic scales with sqrt(n) while the effect does not.

---

### Q9: What is the denominator mean square's degrees of freedom?

A) k − 1
B) N − k
C) N − 1
D) k

**Answer: B** - The residual df is N minus the number of groups.

---

### Q10: Fixed versus random effects changes...

A) The data
B) Which levels the error term is estimated from, and how the result generalises
C) The sample size
D) The null hypothesis

**Answer: B** - Random effects generalise to a population of levels rather than the levels tested.

---

### Q11: Why does a two-way design need replication?

A) For accuracy
B) To separate the interaction from the error term
C) To reduce cost
D) To satisfy assumptions

**Answer: B** - Without within-cell replication the error and interaction are confounded.

---

### Q12: What is Scheffe's method for?

A) Few pre-planned contrasts
B) All possible contrasts including complex comparisons, with FWER control
C) Repeated measures
D) Non-normality

**Answer: B** - It generalises to arbitrary contrasts but is the most conservative.

---

### Q13: A significant F but no post-hoc difference found means...

A) Nothing happened
B) Check power and the pairwise method; the omnibus may be driven by one pair
C) The test failed
D) The data is normal

**Answer: B** - With many groups the omnibus can detect a small overall difference that individual pairs cannot localise.

---

### Q14: How do you report an ANOVA result?

A) F and p only
B) F, df, p, effect size with an interval, and the post-hoc detail
C) Eta-squared only
D) The group means only

**Answer: B** - A bare F-test p-value is uninterpretable without magnitude and localisation.

---

### Q15: What is the rank-based alternative to one-way ANOVA?

A) Friedman test
B) Kruskal-Wallis test
C) Wilcoxon signed-rank
D) Sign test

**Answer: B** - Kruskal-Wallis compares k independent groups without the normality assumption.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
