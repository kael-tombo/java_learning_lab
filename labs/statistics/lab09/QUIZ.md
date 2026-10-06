# Non-Parametric Statistics - Quiz (15 Questions)

**Track:** statistics  |  **Lab:** lab09  |  **Level:** Advanced

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

### Q1: When is a rank test preferable?

A) Large samples
B) Ordinal data, heavy tails, or samples too small to assess normality
C) Normally distributed data
D) Equal variances

**Answer: B** - Rank tests rely only on the ordinal scale and exchangeability.

---

### Q2: What does the Mann-Whitney null assume?

A) Equal means
B) Identical distributions across groups
C) Equal medians
D) Normality

**Answer: B** - Equal means is not assumed, and equal medians requires additional shape similarity.

---

### Q3: Is Mann-Whitney a test of medians?

A) Always
B) Only under additional shape similarity assumptions
C) Never
D) Only for large samples

**Answer: B** - Otherwise it tests stochastic ordering of distributions.

---

### Q4: How do ties affect rank tests?

A) They are ignored
B) They require average ranks and a variance correction, or p-values are too small
C) They increase power
D) They reduce the statistic

**Answer: B** - The tie correction inflates the variance, raising p-values appropriately.

---

### Q5: When should you use an exact p-value?

A) Always
B) For small samples where a normal approximation is invalid
C) Never
D) Only for continuous data

**Answer: B** - The rank statistic is discrete at small n, so enumeration is both easy and correct.

---

### Q6: Which test for paired data?

A) Mann-Whitney
B) Wilcoxon signed-rank
C) Kruskal-Wallis
D) Friedman

**Answer: B** - Paired data requires the signed-rank test on within-pair differences.

---

### Q7: Which test for three or more independent groups?

A) Friedman
B) Kruskal-Wallis
C) Wilcoxon
D) Mann-Whitney

**Answer: B** - Kruskal-Wallis extends the two-group rank test to k independent groups.

---

### Q8: Which test for three or more related groups?

A) Kruskal-Wallis
B) Friedman
C) Wilcoxon
D) ANOVA

**Answer: B** - Friedman blocks by subject and ranks within blocks.

---

### Q9: Why must zero differences be omitted in the signed-rank test?

A) They reduce power
B) A zero carries no direction, so including it distorts the rank sum
C) They cause ties
D) They are required to be omitted for exactness

**Answer: B** - Only non-zero differences contribute directional information.

---

### Q10: Why are rank tests less powerful?

A) They are more conservative
B) They discard magnitude, so large skewed effects need larger samples
C) They assume less so are worse
D) They cannot detect small effects

**Answer: B** - Discarding magnitude is the price of the weaker assumption.

---

### Q11: What is the probability of superiority?

A) The p-value
B) P(X > Y) + 0.5 P(X = Y), a communicable effect size for rank tests
C) The variance
D) The sample size

**Answer: B** - It is directly interpretable as 'how often would a random pair favour this group'.

---

### Q12: Why follow a significant Kruskal-Wallis with pairwise tests?

A) To increase power
B) The omnibus says something differs but not which, and the pairs need a multiplicity correction
C) To satisfy reviewers
D) To reduce the p-value

**Answer: B** - Localisation requires its own error control.

---

### Q13: What is Dunn's test for?

A) Pairwise comparisons after Kruskal-Wallis with a correction
B) Testing normality
C) Variance estimation
D) Tie handling

**Answer: A** - It localises a significant omnibus with appropriate multiplicity control.

---

### Q14: What is a tie correction?

A) A way to remove ties from the data
B) An adjustment to the null variance accounting for tied ranks
C) A test for outliers
D) A correction applied to the p-value

**Answer: B** - It restores the reference distribution's validity under ties.

---

### Q15: When does a rank test's null hold?

A) When means are equal
B) When the distributions are identical across groups, with independent observations respecting the design
C) When variances are equal
D) When the data is normal

**Answer: B** - Exchangeability of ranks is the actual assumption.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
