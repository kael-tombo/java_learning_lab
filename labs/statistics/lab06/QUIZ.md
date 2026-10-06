# Bayesian Statistics - Quiz (15 Questions)

**Track:** statistics  |  **Lab:** lab06  |  **Level:** Advanced

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

### Q1: What does a credible interval express?

A) Repeated-sampling coverage
B) The posterior probability that the parameter lies in the range
C) The probability the hypothesis is true
D) Sampling error

**Answer: B** - It is a statement about the parameter given the model, which is why it needs the prior.

---

### Q2: How does a credible interval differ from a confidence interval?

A) It is narrower
B) It concerns the parameter under the posterior; a confidence interval concerns repeated sampling
C) It uses the normal
D) It requires a large sample

**Answer: B** - Only the credible interval answers 'what is the probability of this range'.

---

### Q3: What is conjugacy?

A) A prior that is unbiased
B) A prior-likelihood pair with a closed-form posterior
C) A prior that is non-informative
D) A sampler technique

**Answer: B** - Convenient, but the conjugate prior is a specific shape that may be too strong.

---

### Q4: When does the prior matter most?

A) With large samples
B) When the data is uninformative relative to the prior
C) Never
D) Only for discrete data

**Answer: B** - Prior influence scales as its pseudo-counts relative to n.

---

### Q5: What is a weakly informative prior?

A) Uninformative
B) One encoding genuine knowledge while ruling out absurd values without dominating data
C) A uniform prior
D) A prior fitted to the data

**Answer: B** - It regularises without materially moving an answer that the data determines.

---

### Q6: What does R-hat measure?

A) Posterior variance
B) Agreement between independent chains, indicating convergence
C) Effective sample size
D) Prior sensitivity

**Answer: B** - Values near 1 indicate chains mixing and agreeing.

---

### Q7: Why must you check convergence?

A) Convention
B) An interval from unmixed chains is confidently wrong
C) To speed up sampling
D) To compute the mean

**Answer: B** - Diagnostics are what make a posterior summary trustworthy.

---

### Q8: What does a prior predictive check test?

A) The prior's mean
B) Whether the model can generate data like the observed
C) Posterior spread
D) Sampling speed

**Answer: B** - It makes the model falsifiable before the real data is used.

---

### Q9: How should two competing models be compared?

A) Compare posterior means
B) Sample from both and compute P(A > B)
C) Compare the HDI widths
D) Compare the priors

**Answer: B** - Sampling accounts for parameter uncertainty on both sides.

---

### Q10: Why is comparing posterior means a mistake?

A) Means are biased
B) Means hide uncertainty; two posteriors can share a mean and imply different odds
C) Means require conjugate priors
D) Means are unstable

**Answer: B** - The decision-relevant quantity is a probability, not a difference of point estimates.

---

### Q11: What is posterior predictive checking for?

A) Sampling diagnostics
B) Testing model adequacy by comparing simulated to observed data
C) Prior selection
D) Interval construction

**Answer: B** - It tests whether the model, not merely the parameter values, is adequate.

---

### Q12: What does the evidence P(data) do?

A) Normalise the posterior
B) Let you compare models via Bayes factors, though it is hard to compute
C) Set the prior
D) Define the interval

**Answer: B** - It is the normalising constant, valuable for model comparison and expensive to compute.

---

### Q13: If two defensible priors give different conclusions, what do you report?

A) The one with the higher evidence
B) The sensitivity as a finding, with the conclusion qualified accordingly
C) The uniform prior
D) Average them

**Answer: B** - Prior-sensitivity findings belong in the report, not in a footnote.

---

### Q14: What is the effective sample size?

A) Number of iterations
B) Number of effectively independent draws, which determines interval accuracy
C) Chain count
D) Prior strength

**Answer: B** - Many correlated draws carry less information than ESS suggests.

---

### Q15: Why does Bayesian inference suit A/B testing?

A) It is faster
B) It answers the decision question directly as a probability about which variant is better
C) It avoids data
D) It removes the need for a control

**Answer: B** - P(variant A beats control | data) is exactly the question a product manager asks.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
