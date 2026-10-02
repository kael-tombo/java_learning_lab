# A/B Testing — Quiz (10 Questions)

**Instructions:** Answer each question. Correct answers and explanations follow.

---

### Q1: What is the primary purpose of randomization in A/B testing?
A) To ensure the treatment group is larger than the control group
B) To eliminate selection bias and ensure groups are comparable
C) To reduce the required sample size
D) To guarantee statistically significant results

**Answer: B** — Randomization ensures that both known and unknown confounding variables are distributed equally across treatment and control groups, making them comparable on average.

---

### Q2: In an A/B test, the p-value is 0.03. Using α = 0.05, what is the correct interpretation?
A) There is a 3% chance the null hypothesis is true
B) There is a 3% chance of observing this data (or more extreme) if the null hypothesis is true
C) The treatment effect is 3%
D) The test has 97% power

**Answer: B** — The p-value is the probability of observing data at least as extreme as what was observed, assuming the null hypothesis is true. It is NOT the probability that the null hypothesis is true.

---

### Q3: What is the difference between Type I and Type II errors?
A) Type I: False positive (reject H₀ when true); Type II: False negative (fail to reject H₀ when false)
B) Type I: False negative; Type II: False positive
C) Type I: Wrong sample size; Type II: Wrong metric
D) Type I: Bias in assignment; Type II: Bias in measurement

**Answer: A** — Type I error (α) = rejecting a true null hypothesis. Type II error (β) = failing to reject a false null hypothesis. Power = 1 − β.

---

### Q4: You run an A/B test with 10,000 users per variant. The conversion rate is 5% (control) vs 5.2% (treatment). The p-value = 0.06. What should you conclude?
A) The treatment is definitely effective
B) The treatment is definitely ineffective
C) There is insufficient evidence to reject the null hypothesis at α = 0.05
D) Increase the sample size and re-run the test immediately

**Answer: C** — With p = 0.06 > 0.05, we fail to reject the null hypothesis. This does NOT prove the treatment is ineffective; it means we lack sufficient evidence to claim an effect at the 5% significance level.

---

### Q5: What is the minimum detectable effect (MDE) in A/B testing?
A) The smallest effect size the test can detect with a given power and sample size
B) The actual effect size observed in the experiment
C) The difference between Type I and Type II error rates
D) The p-value threshold for significance

**Answer: A** — MDE is the smallest true effect size that the experiment has sufficient power (typically 80%) to detect at the chosen significance level. It depends on sample size, baseline conversion rate, α, and desired power.

---

### Q6: Which of the following is a valid reason to stop an A/B test early?
A) The p-value drops below 0.05
B) The treatment group shows a large positive lift
C) A pre-specified stopping rule (e.g., sequential testing boundary) is crossed
D) The experiment has run for two weeks

**Answer: C** — Stopping early based on observing a significant p-value (peeking) inflates Type I error. Only pre-specified sequential testing rules (e.g., O'Brien-Fleming, Pocock boundaries) or futility boundaries justify early stopping.

---

### Q7: What is the "multiple comparisons problem" in A/B testing?
A) Running too many tests simultaneously increases the family-wise error rate
B) Comparing more than two variants requires different statistics
C) Comparing results across different time periods
D) Using multiple metrics to evaluate the same experiment

**Answer: A** — Testing multiple hypotheses (e.g., many variants, many metrics) increases the probability of at least one false positive. Corrections include Bonferroni, Holm-Bonferroni, or Benjamini-Hochberg (FDR control).

---

### Q8: In a conversion rate A/B test, why might you use a binomial proportion z-test instead of a t-test?
A) The t-test assumes continuous data; conversion rates are binomial proportions
B) The z-test is always more powerful
C) The t-test requires larger sample sizes
D) The z-test handles unequal variances better

**Answer: A** — Conversion rates follow a binomial distribution (success/failure). The z-test for proportions uses the normal approximation to the binomial. The t-test assumes continuous, normally distributed data.

---

### Q9: What is "sample ratio mismatch" (SRM)?
A) The treatment effect differs across user segments
B) The observed traffic split deviates significantly from the expected split
C) The sample size is too small to detect the effect
D) The metric variance differs between groups

**Answer: B** — SRM occurs when the actual allocation ratio (e.g., 50/50) differs from the expected ratio due to bugs, filtering, or randomization failures. It invalidates the experiment. Always check SRM with a chi-squared goodness-of-fit test.

---

### Q10: What is the relationship between confidence intervals and hypothesis testing?
A) A 95% CI that excludes 0 corresponds to p < 0.05 for a two-sided test
B) A 95% CI that includes 0 corresponds to p < 0.05
C) CIs and p-values are unrelated
D) CIs are only for Bayesian analysis

**Answer: A** — For a two-sided test at α = 0.05, the null hypothesis (effect = 0) is rejected if and only if the 95% confidence interval for the effect does not contain 0. They are mathematically equivalent.