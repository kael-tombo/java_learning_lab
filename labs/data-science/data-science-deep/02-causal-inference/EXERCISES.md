# Causal Inference — Exercises

**Prerequisites:** Python 3.x with `numpy`, `pandas`, `statsmodels`, `scikit-learn`, `causalml` (optional), or Java with Apache Commons Math.

---

## Exercise 1: Simulate Confounding and Naive Estimation Bias

**Objective:** Demonstrate how confounding biases naive ATE estimation.

**Tasks:**
1. Generate data with confounder X ~ N(0,1):
   - T = 1 if X + ε_T > 0 else 0 (ε_T ~ N(0,1))
   - Y = 2 + 3×T + 2×X + ε_Y (ε_Y ~ N(0,1))
   - True ATE = 3
2. Compute naive ATE: E[Y|T=1] − E[Y|T=0]
3. Compute regression-adjusted ATE: coefficient of T in Y ~ T + X
4. Compare both to true ATE = 3
5. **Challenge:** Vary strength of confounding (coefficient of X in T equation). Plot bias vs confounding strength.

**Expected Answer:** Naive ATE ≈ 5.0 (biased upward by ~2). Regression-adjusted ATE ≈ 3.0 (unbiased).

---

## Exercise 2: Propensity Score Estimation and Diagnostics

**Objective:** Estimate propensity scores and assess overlap.

**Tasks:**
1. Use same data as Exercise 1 (or generate new with multiple confounders X₁, X₂, X₃).
2. Fit logistic regression: T ~ X₁ + X₂ + X₃. Get predicted probabilities ê(X).
3. Plot propensity score distributions for treated vs control (histograms/density).
4. Check positivity: min/max ê(X) in each group. Any near 0 or 1?
5. Compute standardized mean differences (SMD) before and after weighting:
   - SMD = (mean_T − mean_C) / √((var_T + var_C)/2)
6. **Challenge:** Implement caliper matching (1:1 nearest neighbor with caliper = 0.2 × SD of logit(e(X))).

**Expected Answer:** SMD < 0.1 after weighting/matching indicates good balance. Caliper matching discards units with poor matches.

---

## Exercise 3: Inverse Probability Weighting (IPW)

**Objective:** Implement IPW estimator for ATE.

**Tasks:**
1. Using propensity scores from Exercise 2, compute weights:
   - wᵢ = 1/ê(Xᵢ) if Tᵢ=1, wᵢ = 1/(1−ê(Xᵢ)) if Tᵢ=0
2. Compute IPW ATE: Σ wᵢTᵢYᵢ / Σ wᵢTᵢ − Σ wᵢ(1−Tᵢ)Yᵢ / Σ wᵢ(1−Tᵢ)
3. Compute robust (sandwich) standard errors for IPW.
4. Compare IPW estimate to true ATE and regression-adjusted estimate.
5. **Challenge:** Implement stabilized weights: wᵢ = P(T=1)/ê(Xᵢ) for treated, P(T=0)/(1−ê(Xᵢ)) for control. Compare variance.

**Expected Answer:** IPW ATE ≈ 3.0. Stabilized weights reduce variance but same asymptotic bias.

---

## Exercise 4: Propensity Score Matching

**Objective:** Implement 1:1 nearest neighbor matching with replacement.

**Tasks:**
1. Match each treated unit to control with closest propensity score (caliper = 0.2 × SD of logit(e(X))).
2. Compute matched ATT: mean(Y_T − Y_matched_C)
3. Assess balance: SMD for each covariate before/after matching. Plot Love plot.
4. Estimate standard error using Abadie-Imbens formula (accounts for matching).
5. **Challenge:** Implement full matching (subclassification) and compare ATT estimates.

**Expected Answer:** Matched ATT ≈ 3.0. SMDs < 0.1 after matching. Standard error larger than IPW due to discarding units.

---

## Exercise 5: Doubly Robust Estimation (AIPW)

**Objective:** Implement Augmented IPW estimator.

**Tasks:**
1. Fit outcome models: μ̂₁(X) = E[Y|T=1,X], μ̂₀(X) = E[Y|T=0,X] (e.g., linear regression per group).
2. Compute AIPW:
   τ̂ = ¹/N Σ [μ̂₁(Xᵢ) − μ̂₀(Xᵢ) + Tᵢ(Yᵢ−μ̂₁(Xᵢ))/ê(Xᵢ) − (1−Tᵢ)(Yᵢ−μ̂₀(Xᵢ))/(1−ê(Xᵢ))]
3. Verify double robustness:
   - Misspecify outcome model (omit X₃), keep propensity model correct → should be unbiased
   - Misspecify propensity model (omit X₃), keep outcome model correct → should be unbiased
   - Misspecify both → biased
4. **Challenge:** Implement cross-fitting (sample splitting) to avoid overfitting bias with ML models.

**Expected Answer:** AIPW ≈ 3.0 in all correctly specified cases. Remains unbiased when one model is misspecified.

---

## Exercise 6: DAG Analysis and Backdoor Criterion

**Objective:** Practice identifying adjustment sets from DAGs.

**DAG 1 (Confounding):**
```
X → T
X → Y
```
**Question:** What adjustment set identifies ATE?

**DAG 2 (Mediator):**
```
T → M → Y
```
**Question:** Should you adjust for M to estimate total effect of T on Y?

**DAG 3 (Collider):**
```
T → C ← Y
```
**Question:** What happens if you adjust for C?

**DAG 4 (M-Bias):**
```
U₁ → X₁ ← U₂
U₁ → T, U₂ → Y
T → Y
```
**Question:** Is X₁ a confounder? Should you adjust for it?

**DAG 5 (Complex):**
```
X₁ → T, X₁ → Y
X₂ → T, X₂ → Y
T → M → Y
X₁ → M
```
**Question:** Minimal adjustment set for total effect of T on Y?

**Expected Answers:**
1. {X} blocks backdoor path T ← X → Y
2. NO — adjusting for M blocks indirect effect. Don't adjust for mediators for total effect.
3. Adjusting for C OPENS path T → C ← Y, creating spurious bias.
4. X₁ is a COLLIDER (U₁ → X₁ ← U₂). Adjusting for it INDUCES bias (M-bias).
5. {X₁, X₂} blocks all backdoor paths. M is a mediator — don't adjust for total effect.

---

## Exercise 7: Instrumental Variables (IV) Simulation

**Objective:** Simulate IV setting and estimate LATE.

**Tasks:**
1. Generate data:
   - Z ~ Bernoulli(0.5) (instrument)
   - T = 1 if 0.5 + 0.5×Z + ε_T > 0 else 0 (Z increases treatment probability)
   - Y = 2 + 4×T + ε_Y (true effect = 4 for compliers)
   - Add "always-takers" (T=1 regardless of Z) and "never-takers" (T=0 regardless)
2. Compute naive OLS: Y ~ T
3. Compute 2SLS: First stage T ~ Z, second stage Y ~ T̂
4. Compare to true complier effect (LATE = 4).
5. **Challenge:** Compute compliance rate and verify LATE = ITT / compliance_rate (Wald estimator).

**Expected Answer:** OLS biased (confounded). 2SLS ≈ 4.0 (LATE). Wald estimator: ITT = E[Y|Z=1]−E[Y|Z=0], compliance = E[T|Z=1]−E[T|Z=0], LATE = ITT/compliance.

---

## Exercise 8: Difference-in-Differences (DiD)

**Objective:** Implement DiD with parallel trends assumption.

**Tasks:**
1. Generate panel data (N=1000 units, 2 periods: pre=0, post=1):
   - Treatment group: 500 units treated in post period
   - Control group: 500 units never treated
   - Yᵢₜ = αᵢ + λₜ + β×Tᵢₜ + εᵢₜ
   - True β = 2.5
2. Estimate DiD: (Y_T,post − Y_T,pre) − (Y_C,post − Y_C,pre)
3. Implement as regression: Y ~ Post + Treat + Post×Treat + unit_FE
4. Test parallel trends: add pre-treatment period (t=-1) and check if pre-trends differ.
5. **Challenge:** Implement event study design with multiple pre/post periods.

**Expected Answer:** DiD estimate ≈ 2.5. Parallel trends test: interaction of Treat × PrePeriod should be insignificant.

---

## Exercise 9: Regression Discontinuity (RD)

**Objective:** Implement sharp RD design.

**Tasks:**
1. Generate data with running variable X ~ Uniform(-10, 10):
   - T = 1 if X ≥ 0 else 0
   - Y = 1 + 2×T + 0.5×X + 0.1×X² + ε
   - True effect at cutoff = 2
2. Estimate using local linear regression (bandwidth = 2):
   - Fit Y ~ T + X + T×X separately on each side of cutoff
   - RD estimate = intercept difference at X=0
3. Try different bandwidths (1, 2, 3, 5). Plot estimate vs bandwidth.
4. **Challenge:** Implement McCrary density test for manipulation of running variable.

**Expected Answer:** RD estimate ≈ 2.0 with bandwidth ~2. Smaller bandwidth → higher variance, less bias. Larger bandwidth → more bias from curvature.

---

## Exercise 10: Sensitivity Analysis (Rosenbaum Bounds / E-value)

**Objective:** Assess robustness to unmeasured confounding.

**Tasks:**
1. Using data from Exercise 1, compute observed ATE estimate and its standard error.
2. Compute E-value for point estimate:
   - E-value = RR + √(RR×(RR−1)) where RR = exp(|β|) for log-odds/rate ratio
   - For linear model with continuous Y: approximate using Cohen's d
3. Compute E-value for CI limit (closest to null).
4. Interpret: "An unmeasured confounder would need to have RR ≥ E-value with both T and Y to explain away the effect."
5. **Challenge:** Implement Rosenbaum sensitivity bounds for matched pairs (Γ-sensitivity).

**Expected Answer:** For ATE ≈ 3 with SD ≈ 2, effect size d = 1.5. E-value ≈ 3.5 for point estimate. Confounding would need to be very strong to explain away.

---

## Bonus: Real-World Causal Analysis

**Dataset:** Use the [Lalonde job training dataset](https://web.archive.org/web/20141009181509/https://users.nber.org/~rdehejia/data/nswdata2.html) or [CPS/PSID comparison data].

**Tasks:**
1. Estimate effect of job training (NSW program) on 1978 earnings.
2. Compare experimental estimate (randomized) vs observational (NSW treated + PSID controls).
3. Apply: regression adjustment, IPW, matching, AIPW.
4. Show how observational estimates are biased without proper adjustment.
5. Write a 2-page report: methods, results, assumptions, sensitivity analysis, conclusions.