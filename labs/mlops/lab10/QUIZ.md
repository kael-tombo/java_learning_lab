# A/B Testing & Experimentation - Quiz (15 Questions)

**Track:** mlops  |  **Lab:** lab10  |  **Level:** Advanced

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

### Q1: What is the single most important requirement for a valid A/B test?

A) A large sample
B) Random, stable assignment of units to arms
C) A long duration
D) Many metrics

**Answer: B** - Everything else is analysis; broken assignment cannot be repaired statistically.

---

### Q2: What does power mean?

A) Sample size
B) The probability of detecting a real effect of a given size
C) Confidence level
D) Variance

**Answer: B** - Power is 1 - beta and must be fixed before launch.

---

### Q3: Why must sample size be computed before the test?

A) For billing reasons
B) It follows from the MDE, alpha and power you chose
C) Because the API requires it
D) To reduce storage

**Answer: B** - Computing it afterwards makes an underpowered result uninterpretable.

---

### Q4: What is sample ratio mismatch?

A) A metric bug
B) The arms receiving traffic in different proportions than designed
C) Label delay
D) Seasonality

**Answer: B** - SRM invalidates everything downstream, so it is checked before any metric.

---

### Q5: Why does peeking inflate false positives?

A) It reduces power
B) Each additional look adds another chance to cross the threshold by chance
C) It increases variance
D) Labels arrive late

**Answer: B** - Ten daily looks at alpha 0.05 behave like a much larger error rate.

---

### Q6: How do you allow early stopping correctly?

A) Increase alpha
B) Use a sequential design with alpha control, such as alpha spending
C) Stop at first significance
D) Use a larger sample

**Answer: B** - Alpha spending or always-valid confidence sequences keep the error rate at the planned level.

---

### Q7: What is a guardrail metric for?

A) Secondary reporting
B) Bounding harm: non-inferiority checks that can stop the test
C) Increasing power
D) Sampling more

**Answer: B** - Guardrails let you stop for harm even while the primary metric looks good.

---

### Q8: What is the difference between statistical and practical significance?

A) They are the same
B) Statistical means unlikely to be noise; practical means worth the rollout cost
C) Practical uses bigger samples
D) Statistical needs more time

**Answer: B** - A tiny reliable effect can still be a bad investment.

---

### Q9: What can a shadow test not measure?

A) Latency
B) Business outcomes from user-facing exposure
C) Score distribution
D) Disagreement with the champion

**Answer: B** - Shadow scoring never changes decisions, so it cannot attribute a business effect.

---

### Q10: Why hash on user id rather than session?

A) Performance
B) So a user stays in one arm and does not contaminate both
C) Easier debugging
D) To reduce storage

**Answer: B** - Cross-arm users dilute the effect and confuse the analysis.

---

### Q11: What is a novelty effect?

A) A bug
B) An early spike in the treatment that decays as users adapt
C) Sampling bias
D) Label noise

**Answer: B** - A short horizon will call a decaying spike a win.

---

### Q12: How do you handle a result that depends on excluding outliers?

A) Exclude them
B) Pre-register the exclusion rule; post-hoc filtering invalidates the result
C) Report both and pick the better
D) Increase the sample

**Answer: B** - Post-hoc filtering lets you find any conclusion you want.

---

### Q13: What should the horizon be?

A) Two weeks by convention
B) The time your sample size requires, computed from MDE and power
C) Until significant
D) One full business quarter

**Answer: B** - A fixed horizon is also what keeps the error rate honest.

---

### Q14: What is the risk of running many arms at once?

A) Cost
B) Multiple comparisons inflate the false positive rate across arms
C) Label delay
D) Storage

**Answer: B** - With 5 arms and 20 looks, uncorrected error rates become very large.

---

### Q15: What should the decision document contain?

A) A p-value
B) The effect with an interval, translated into business units, plus guardrail status
C) Arm names
D) Traffic numbers

**Answer: B** - A decision needs the magnitude, the uncertainty and the value, not just significance.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
