# Hypothesis Testing - Quiz (15 Questions)

**Track:** statistics  |  **Lab:** lab03  |  **Level:** Intermediate

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

### Q1: What does a p-value of 0.03 mean?

A) 3% chance the null is true
B) P(data this extreme | the null is true)
C) 3% chance of being wrong
D) The effect is 3%

**Answer: B** - It is conditional on the null, which is the part almost always misreported.

---

### Q2: Type I error is...

A) Failing to reject a false null
B) Rejecting a true null
C) Using the wrong test
D) Sampling error

**Answer: B** - Type I error is controlled by alpha; Type II is beta.

---

### Q3: Power is...

A) 1 - alpha
B) 1 - beta, the probability of detecting a real effect
C) The sample size
D) The effect size

**Answer: B** - Power is the probability of rejecting a false null.

---

### Q4: Why prefer Welch's t?

A) It is simpler
B) It does not assume equal variances
C) It needs less data
D) It gives a smaller p

**Answer: B** - The pooled test badly distorts p-values when variances differ and n is small.

---

### Q5: When is a paired test correct?

A) When groups are large
B) When observations are paired, such as before and after
C) When variance is low
D) Always

**Answer: B** - The test runs on within-pair differences, which removes between-unit variation.

---

### Q6: What does a non-significant result tell you?

A) The treatments are equal
B) Insufficient evidence at the achieved power
C) The test was wrong
D) The effect is zero

**Answer: B** - Absence of evidence is not evidence of absence; report power and the interval.

---

### Q7: Why does p < 0.05 on a tiny effect not mean it matters?

A) It does mean it
B) With large n any small difference becomes significant, so magnitude must be judged separately
C) p-values are biased
D) It means the test failed

**Answer: B** - Significance answers whether it is noise, never whether it is worth acting on.

---

### Q8: What does testing daily and stopping at p < 0.05 do?

A) Nothing
B) Inflates the false positive rate far above 5%
C) Reduces the p-value
D) Improves power

**Answer: B** - Repeated uncorrected looks behave like multiple testing.

---

### Q9: How do you fix the multiple-look problem?

A) Use a smaller alpha
B) Fix the horizon in advance or use a sequential design with alpha control
C) Test less often
D) Use a larger sample

**Answer: B** - Alpha spending or always-valid confidence sequences preserve the error rate.

---

### Q10: What is chi-square used for?

A) Comparing means
B) Testing categorical counts for goodness of fit or independence
C) Testing proportions directly
D) Any test

**Answer: B** - Chi-square operates on counts; it is not a test of means.

---

### Q11: Why does expected count below 5 matter in chi-square?

A) It slows the test
B) The chi-square approximation to the null distribution assumes expected counts of about 5 or more
C) It changes df
D) It biases the effect size

**Answer: B** - Small expected counts make the reference distribution unreliable in the tails.

---

### Q12: Choosing a one-sided alternative after seeing data...

A) Is fine
B) Inflates the error rate; the direction must be pre-specified
C) Reduces power
D) Is required for small n

**Answer: B** - Choosing the direction post hoc is a second look in disguise.

---

### Q13: What does the confidence interval give you that p does not?

A) A smaller number
B) The plausible range of effect magnitudes, which drives the decision
C) Higher power
D) Fewer assumptions

**Answer: B** - Only the interval tells you how big the effect might be.

---

### Q14: What does H₀ being 'no difference' mean?

A) It is true
B) It is a claim to be evaluated with its probability of being detected, not an assumption of truth
C) The alternative is false
D) Nothing

**Answer: B** - The null is a hypothesis whose rejection rate you control with alpha.

---

### Q15: Why fix sample size before collecting data?

A) For ethics
B) Power is a function of n; collecting first risks a test that cannot detect the effect you care about
C) To reduce cost
D) To simplify analysis

**Answer: B** - Choosing n after seeing effect sizes is the most common source of invalid inference.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
