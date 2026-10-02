# A/B Testing — Flashcards

**Format:** Question (front) → Answer (back). Use for spaced repetition.

---

### Card 1
**Q:** What is an A/B test?
**A:** A randomized controlled experiment comparing two variants (A = control, B = treatment) to measure the causal effect of a change on a metric.

---

### Card 2
**Q:** What is the null hypothesis (H₀) in a standard A/B test?
**A:** H₀: μ_A = μ_B (no difference in the metric between control and treatment groups).

---

### Card 3
**Q:** What is the alternative hypothesis (H₁) in a two-sided A/B test?
**A:** H₁: μ_A ≠ μ_B (there is a difference, either positive or negative).

---

### Card 4
**Q:** Define Type I error (α).
**A:** Rejecting H₀ when it is true (false positive). Standard α = 0.05 means 5% chance of false positive per test.

---

### Card 5
**Q:** Define Type II error (β).
**A:** Failing to reject H₀ when it is false (false negative). Power = 1 − β.

---

### Card 6
**Q:** What is statistical power?
**A:** Probability of correctly detecting a true effect. Standard target = 80% (β = 0.20).

---

### Card 7
**Q:** What is the p-value?
**A:** P(data ≥ observed | H₀ true). Probability of seeing results at least this extreme if there's no real effect.

---

### Card 8
**Q:** What does p = 0.03 mean?
**A:** If H₀ is true, there's a 3% chance of observing this data (or more extreme). At α = 0.05, we reject H₀.

---

### Card 9
**Q:** What is the Minimum Detectable Effect (MDE)?
**A:** The smallest true effect size the experiment can detect with the given sample size, α, and power.

---

### Card 10
**Q:** Formula for sample size per variant (proportions)?
**A:** n = (Z_{1−α/2} + Z_{1−β})² × (p₁(1−p₁) + p₂(1−p₂)) / (p₁ − p₂)²

---

### Card 11
**Q:** What is randomization?
**A:** Random assignment of users to variants to ensure comparability and eliminate selection bias.

---

### Card 12
**Q:** What is Sample Ratio Mismatch (SRM)?
**A:** Observed traffic split deviates significantly from expected (e.g., not 50/50). Indicates experiment bug.

---

### Card 13
**Q:** How to check for SRM?
**A:** Chi-squared goodness-of-fit test comparing observed vs. expected counts per variant.

---

### Card 14
**Q:** What is "peeking" and why is it bad?
**A:** Checking p-values before the pre-determined sample size is reached. Inflates Type I error rate.

---

### Card 15
**Q:** What are valid early stopping methods?
**A:** Pre-specified sequential testing boundaries (O'Brien-Fleming, Pocock) or futility boundaries.

---

### Card 16
**Q:** What is the multiple comparisons problem?
**A:** Testing many hypotheses increases family-wise error rate (FWER). P(at least one false positive) = 1 − (1−α)^k.

---

### Card 17
**Q:** Bonferroni correction?
**A:** Adjust α' = α / k for k comparisons. Controls FWER but conservative.

---

### Card 18
**Q:** Benjamini-Hochberg procedure?
**A:** Controls False Discovery Rate (FDR). Less conservative than Bonferroni. Rank p-values, find max k where p_(k) ≤ (k/m)α.

---

### Card 19
**Q:** When to use z-test vs t-test for A/B tests?
**A:** z-test for proportions (conversion rates); t-test for continuous metrics (revenue, time). Both assume large n → normal approximation.

---

### Card 20
**Q:** What is a confidence interval (CI)?
**A:** Range of plausible values for the true effect. 95% CI: if we repeated the experiment infinitely, 95% of CIs would contain the true effect.

---

### Card 21
**Q:** CI-hypothesis test duality?
**A:** 95% CI excludes 0 ⇔ p < 0.05 (two-sided). They are equivalent.

---

### Card 22
**Q:** What is a one-sided vs two-sided test?
**A:** One-sided: H₁: μ_B > μ_A (only care about improvement). Two-sided: H₁: μ_B ≠ μ_A. One-sided has more power but requires strong justification.

---

### Card 23
**Q:** What is a permutation test?
**A:** Non-parametric test: shuffle labels many times, compute test statistic each time, compare observed to null distribution. No distributional assumptions.

---

### Card 24
**Q:** What is the "novelty effect"?
**A:** Temporary behavior change because users notice something new. Mitigate by running experiment longer or using holdout.

---

### Card 25
**Q:** What is "primacy effect"?
**A:** Experienced users perform worse on new variant due to familiarity with old. Mitigate by analyzing new vs. existing users separately.

---

### Card 26
**Q:** What is the difference between statistical and practical significance?
**A:** Statistical: p < α (effect unlikely due to chance). Practical: effect size large enough to matter for business. Both needed.

---

### Card 27
**Q:** What is a holdout group?
**A:** A small % of users never exposed to experiments. Used to measure long-term cumulative effects and detect interaction effects.

---

### Card 28
**Q:** What is "interaction effect" between experiments?
**A:** The effect of experiment A depends on whether user is in experiment B. Can bias results if not accounted for.

---

### Card 29
**Q:** How to handle experiment interactions?
**A:** Mutually exclusive experiment layers; factorial designs; or analyze with regression including interaction terms.

---

### Card 30
**Q:** What is a guardrail metric?
**A:** A metric you monitor to ensure the treatment doesn't harm key business areas (e.g., latency, error rate, revenue) even if primary metric improves.