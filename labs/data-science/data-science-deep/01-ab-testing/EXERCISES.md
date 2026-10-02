# A/B Testing — Exercises

**Prerequisites:** Python 3.x with `numpy`, `scipy`, `pandas`, `statsmodels` or Java with Apache Commons Math.

---

## Exercise 1: Sample Size Calculation

**Objective:** Calculate required sample size per variant for a conversion rate A/B test.

**Scenario:** Baseline conversion rate = 10%. You want to detect a 10% relative lift (i.e., 11% in treatment). α = 0.05 (two-sided), power = 80%.

**Tasks:**
1. Calculate the absolute difference (Δ) and treatment rate (p₂).
2. Compute the pooled standard error under H₀.
3. Use the formula: `n = (Z_{1−α/2} + Z_{1−β})² × (p₁(1−p₁) + p₂(1−p₂)) / Δ²`
4. Verify using `statsmodels.stats.proportion.proportion_ztest_power` or equivalent.
5. **Challenge:** How does required n change if baseline = 1% vs 50%? Plot n vs baseline rate.

**Expected Answer:** ~14,700 per variant. At 1% baseline, n ≈ 150,000; at 50%, n ≈ 38,400.

---

## Exercise 2: Simulate A/A Test (False Positive Rate)

**Objective:** Empirically verify Type I error rate.

**Tasks:**
1. Simulate 10,000 A/A tests: both variants have identical conversion rate (e.g., 10%).
2. For each test, generate binomial samples (n = 1000 per variant) and run a two-proportion z-test.
3. Count proportion of tests with p < 0.05.
4. Repeat for n = 100, 1000, 10000.
5. **Challenge:** What happens to false positive rate if you "peek" 5 times during the experiment (sequential testing without correction)?

**Expected Answer:** False positive rate ≈ 5% for fixed-horizon tests. With peeking 5×, FPR inflates to ~15-20%.

---

## Exercise 3: Power Analysis via Simulation

**Objective:** Estimate power for a given effect size and sample size.

**Tasks:**
1. Simulate 5,000 A/B tests where treatment has a true 10% relative lift (10% → 11%).
2. Sample size = 15,000 per variant (from Exercise 1).
3. Run two-proportion z-test for each; compute proportion with p < 0.05.
4. Compare empirical power to theoretical 80%.
5. **Challenge:** Plot power curve as function of true lift (0% to 30% relative lift).

**Expected Answer:** Empirical power ≈ 78-82%. Power curve should show steep rise around MDE.

---

## Exercise 4: Sample Ratio Mismatch Detection

**Objective:** Implement SRM check.

**Scenario:** Expected 50/50 split. Observed: Control = 48,500, Treatment = 51,500 (Total = 100,000).

**Tasks:**
1. Compute expected counts under 50/50 split.
2. Perform chi-squared goodness-of-fit test: `χ² = Σ (O−E)²/E`.
3. Calculate p-value with 1 degree of freedom.
4. At α = 0.01 (stricter for SRM), is there significant mismatch?
5. **Challenge:** Write a function `check_srm(observed_control, observed_treatment, alpha=0.01)` returning (is_srm, p_value).

**Expected Answer:** χ² = 90, p ≈ 0 → SRM detected. Expected 50,000 each; deviation of 1,500 is highly significant.

---

## Exercise 5: Confidence Interval for Difference in Proportions

**Objective:** Compute and interpret CI for lift.

**Scenario:** Control: 1,000 conversions / 10,000 users (10%). Treatment: 1,150 / 10,000 (11.5%).

**Tasks:**
1. Compute point estimate of difference: `p̂₂ − p̂₁`.
2. Compute standard error: `SE = √(p̂₁(1−p̂₁)/n₁ + p̂₂(1−p̂₂)/n₂)`.
3. Compute 95% CI: `diff ± 1.96 × SE`.
4. Does CI exclude 0? What does this imply about p-value?
5. **Challenge:** Compute relative lift CI: `(p̂₂ − p̂₁) / p̂₁` using delta method or bootstrap.

**Expected Answer:** Diff = 0.015, SE ≈ 0.0043, 95% CI ≈ [0.0066, 0.0234]. Excludes 0 → p < 0.05.

---

## Exercise 6: Multiple Comparisons Correction

**Objective:** Apply Bonferroni and Benjamini-Hochberg corrections.

**Scenario:** You test 5 variants against control (5 comparisons). Raw p-values: [0.012, 0.038, 0.004, 0.067, 0.021].

**Tasks:**
1. Apply Bonferroni: α' = 0.05/5 = 0.01. Which are significant?
2. Apply Benjamini-Hochberg (FDR = 0.05): sort p-values, find max k where p_(k) ≤ (k/5)×0.05.
3. Compare results. Which method is more conservative?
4. **Challenge:** Implement both corrections as reusable functions.

**Expected Answer:** Bonferroni: only p=0.004 significant. BH: p=0.004, 0.012, 0.021 significant (k=3, threshold=0.03).

---

## Exercise 7: Sequential Testing Simulation (Peeking Problem)

**Objective:** Demonstrate Type I error inflation from peeking.

**Tasks:**
1. Simulate A/A test (both 10% conversion) with n=10,000 per variant.
2. Peek at 5 equally spaced intervals (2000, 4000, 6000, 8000, 10000).
3. Stop and reject H₀ if any peek yields p < 0.05.
4. Run 10,000 simulations; compute false positive rate.
5. Compare to fixed-horizon (only final peek).
6. **Challenge:** Implement O'Brien-Fleming boundaries: α_k = 2 − 2Φ(z_{α/2}/√(k/K)) for K=5 looks.

**Expected Answer:** Naive peeking FPR ≈ 14-18%. Fixed-horizon ≈ 5%. O'Brien-Fleming controls FPR at ~5%.

---

## Exercise 8: Bayesian A/B Test (Optional Advanced)

**Objective:** Compute posterior probability that treatment is better.

**Tasks:**
1. Assume Beta(1,1) prior for both variants.
2. Control: 1000 conversions, 9000 failures. Treatment: 1150 conversions, 8850 failures.
3. Posterior: Control ~ Beta(1001, 9001), Treatment ~ Beta(1151, 8851).
4. Sample 100,000 draws from each posterior; compute P(θ_T > θ_C).
5. Compare to frequentist p-value.
6. **Challenge:** Compute expected loss (expected opportunity cost) for choosing each variant.

**Expected Answer:** P(θ_T > θ_C) ≈ 0.999. Very strong evidence for treatment. Expected loss quantifies risk of wrong decision.

---

## Exercise 9: Practical Significance vs Statistical Significance

**Objective:** Distinguish between statistical and practical significance.

**Scenario:** Large experiment: n = 1,000,000 per variant. Control: 10.00% conversion. Treatment: 10.05% conversion. p < 0.001.

**Tasks:**
1. Compute 95% CI for absolute and relative difference.
2. Is the result statistically significant?
3. Is it practically significant? (Business context: 0.05% lift = $50K/year vs $1M implementation cost)
4. **Challenge:** Define a "region of practical equivalence" (ROPE) and compute P(effect ∈ ROPE) using Bayesian approach.

**Expected Answer:** Statistically significant (p < 0.001, CI excludes 0). But 0.5% relative lift may not justify cost. Practical significance depends on business context.

---

## Exercise 10: End-to-End A/B Test Analysis Pipeline

**Objective:** Build a complete analysis script.

**Requirements:** Create a Python/Java class `ABTestAnalyzer` with methods:
- `calculate_sample_size(baseline_rate, mde_relative, alpha, power)`
- `analyze_results(control_conversions, control_users, treatment_conversions, treatment_users)`
- `check_srm(control_users, treatment_users, expected_ratio=0.5, alpha=0.01)`
- `compute_ci(control_conversions, control_users, treatment_conversions, treatment_users, confidence=0.95)`
- `generate_report(...)` → formatted markdown with decision recommendation

**Test Cases:**
1. Sample size: baseline=0.1, mde=0.1, alpha=0.05, power=0.8
2. Analysis: control=1000/10000, treatment=1150/10000
3. SRM: control=48500, treatment=51500
4. Edge case: control=0/1000, treatment=5/1000 (zero conversions)

**Deliverable:** Working code + test outputs + brief reflection on assumptions and limitations.

---

## Bonus: Real-World Data Exercise

**Dataset:** Use the [UCI Online Shoppers Intention dataset](https://archive.ics.uci.edu/ml/datasets/Online+Shoppers+Purchasing+Intention) or similar.

**Tasks:**
1. Treat "Weekend" vs "Weekday" as A/B test (not truly randomized — discuss limitations).
2. Compare "Revenue" conversion rates.
3. Run full analysis: sample size check, hypothesis test, CI, SRM check, power analysis.
4. Write a 1-page experiment report with recommendation.
5. **Reflection:** What threats to validity exist? (Non-random assignment, seasonality, etc.)