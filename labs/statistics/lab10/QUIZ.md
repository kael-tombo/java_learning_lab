# Statistical Power & Effect Size - Quiz (15 Questions)

**Track:** statistics  |  **Lab:** lab10  |  **Level:** Advanced

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

### Q1: What does power depend on?

A) The observed result
B) The specified effect size, variance, sample size and alpha
C) The p-value
D) Only the sample size

**Answer: B** - Because it depends on the assumed effect, power is computable before data collection.

---

### Q2: Why is a non-significant result from a small study uninformative?

A) The test was wrong
B) The study's minimum detectable effect may be far larger than any meaningful effect
C) Power is undefined
D) Alpha was too high

**Answer: B** - With n = 20 per arm you can only detect effects of about d = 0.9.

---

### Q3: What is Cohen's d?

A) A correlation
B) The mean difference in pooled standard deviation units
C) A variance ratio
D) A power value

**Answer: B** - Standardising the difference makes it comparable across scales.

---

### Q4: Why use Hedges' g?

A) It is smaller
B) It corrects the upward bias of d at small sample sizes
C) It handles outliers
D) It assumes normality

**Answer: B** - The correction is material below roughly n = 20 per group.

---

### Q5: Why inflate a pilot variance?

A) To be conservative
B) Small pilots give biased-low variance estimates
C) Because the formula requires it
D) To reduce n

**Answer: B** - Under-estimated variance is the most common cause of under-powered studies.

---

### Q6: Why is post-hoc power uninformative?

A) It is hard to compute
B) Computed at the observed effect it is a monotone function of the p-value
C) It assumes normality
D) It ignores alpha

**Answer: B** - Retrospective power is meaningful only at the a priori effect.

---

### Q7: How does MDE scale with n?

A) Linearly
B) As 1/sqrt(n), so quadrupling the sample halves it
C) As 1/n
D) It does not depend on n

**Answer: B** - That is why small studies are so uninformative.

---

### Q8: Why does one-sided power exceed two-sided?

A) It uses a different test
B) A directional alternative rejects at a less extreme threshold
C) It needs less data
D) Alpha is larger

**Answer: B** - The gain is real and must be justified by a pre-specified direction.

---

### Q9: What is Cohen's 0.5 'medium' threshold?

A) A universal constant
B) A convention that must be translated into business units before use
C) A power value
D) A sample size

**Answer: B** - A 0.5 effect in revenue may dwarf a 1.2 effect in latency.

---

### Q10: What does power curve planning buy?

A) Larger samples
B) An explicit view of what the design can and cannot detect
C) Lower alpha
D) Fewer comparisons

**Answer: B** - It converts a sample constraint into a statement about resolution.

---

### Q11: What happens to power when alpha is Bonferroni-adjusted?

A) It increases
B) It decreases, so required n grows
C) It is unchanged
D) It becomes one-sided

**Answer: B** - Each of m comparisons must run at alpha/m, which lowers sensitivity per test.

---

### Q12: What is Glass's delta?

A) A standardised difference using the control group standard deviation
B) A nonparametric effect size
C) A variance estimate
D) A correction for skew

**Answer: A** - It is the alternative to pooling when variances are unequal.

---

### Q13: Why is the effect size for planning not the observed one?

A) It is harder to compute
B) Using the observed effect plans on the outcome and inflates power claims
C) It is biased
D) It is undefined

**Answer: B** - Planning must be independent of the data you have not yet seen.

---

### Q14: What should accompany a non-significant result?

A) A larger sample suggestion
B) Power and the minimum detectable effect
C) A different test
D) A one-sided test

**Answer: B** - It converts an ambiguous null into a statement about what the study could detect.

---

### Q15: How does a business threshold become an effect size?

A) It cannot
B) Translate it into the metric's standard deviation units and use it as the planning effect
C) It becomes alpha
D) It sets the sample size

**Answer: B** - The threshold is the design's resolution requirement, expressed in domain units.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
