# Descriptive Statistics - Quiz (15 Questions)

**Track:** statistics  |  **Lab:** lab01  |  **Level:** Foundational

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

### Q1: Which summary is most robust to outliers?

A) Mean
B) Median
C) Variance
D) Standard deviation

**Answer: B** - The median depends on position, not magnitude, so extreme values barely move it.

---

### Q2: Why does sample variance divide by n minus one?

A) Convenience
B) One degree of freedom is used estimating the mean, so n−1 makes it unbiased
C) To make it smaller
D) Because of rounding

**Answer: B** - E[s²] equals σ² only with the n−1 divisor.

---

### Q3: Why is sum-of-squares variance numerically unstable?

A) It is slower
B) Subtracting two nearly equal large numbers loses significant digits
C) It cannot handle negatives
D) It ignores the mean

**Answer: B** - With a large mean and small spread, the difference is tiny relative to both terms.

---

### Q4: What does an IQR of 30 tell you?

A) The mean is 30
B) The middle 50% of values span 30 units
C) The range is 30
D) The variance is 30

**Answer: B** - IQR is Q3 minus Q1, the width of the middle half.

---

### Q5: What should you do with a point outside the 1.5 IQR fence?

A) Delete it
B) Flag and inspect it for a data-quality cause
C) Replace it with the median
D) Ignore it

**Answer: B** - Outliers are often the interesting rows, and deletion is a decision to record.

---

### Q6: Which summary should you report for p99 latency?

A) Mean ± sd
B) Mean and median
C) p50, p90, p99 and tail analysis
D) Mode

**Answer: C** - Latency is right-skewed, so percentiles describe what traffic experiences.

---

### Q7: Can mean and standard deviation describe a bimodal distribution?

A) Yes
B) No
C) Only if modes are close
D) Only with small n

**Answer: B** - Two numbers cannot encode two modes; the summary hides the structure.

---

### Q8: What is Simpson's paradox?

A) A numerical error
B) An aggregate trend that reverses inside every segment
C) A sampling artifact
D) A correlation fallacy

**Answer: B** - It appears whenever segment sizes are unbalanced.

---

### Q9: A skewness of 2.4 indicates...

A) Symmetric data
B) Strong right skew, so the mean sits above the typical value
C) Left skew
D) Bimodality

**Answer: B** - Positive skew means a right tail pulling the mean up.

---

### Q10: Why does mode work for categorical data but mean does not?

A) Mode is cheaper
B) Categories have no meaningful numeric ordering to average
C) Means require sorting
D) Modes are more accurate

**Answer: B** - Averaging categories is meaningless without an ordering.

---

### Q11: What does kurtosis describe?

A) The centre
B) Tail weight relative to a normal distribution
C) The range
D) The sample size

**Answer: B** - Excess kurtosis above zero means heavier tails than normal.

---

### Q12: If two datasets share mean and standard deviation, can they differ?

A) No
B) Yes; the two numbers discard shape
C) Only if n is large
D) Only if the median matches

**Answer: B** - This is why distribution comparison is a separate tool.

---

### Q13: Which estimator gives an unbiased population variance?

A) Dividing by n
B) Dividing by n−1
C) Taking the square root
D) Using the range

**Answer: B** - The n−1 divisor is exactly the Bessel correction.

---

### Q14: Why compute quantiles by interpolation?

A) Speed
B) Order statistics alone are coarse and bin-width sensitive
C) Accuracy of the mean
D) To reduce memory

**Answer: B** - Interpolation gives a smoother, more stable estimate between order statistics.

---

### Q15: What is the safest single number to report for skewed business data?

A) Mean
B) Median
C) Range
D) Variance

**Answer: B** - The median represents a typical observation when the mean does not.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
