# Common Mistakes: Hypothesis Testing

### 1. Reading p as P(H₀ | data)
P(D | H₀) ≠ P(H₀ | D). p = 0.03 means: *if* the null were true, data this extreme occur 3% of the time. It says nothing about the probability the null is true — that requires priors (lab 08). Reporting "97% confident the effect exists" inverts the conditional.

### 2. The two-sided / one-sided switch after seeing data
Choosing a one-tailed test because the two-sided p = 0.06 doubles your effective α. Neyman–Pearson requires the alternative — hence the critical region — to be fixed *before* the data. Post-hoc tail-switching is the most common silent α inflation.

### 3. Multiple comparisons without correction
20 independent tests at α = 0.05: P(at least one false positive) = 1 − 0.95²⁰ = **0.6415**. Genome-wide association studies run 10⁶ tests: even at α = 0.001, expect 1000 false hits. Fix: Bonferroni (α/m), Holm's step-down (uniformly more powerful), or Benjamini–Hochberg FDR when discoveries are the goal.

### 4. Confusing "fail to reject" with acceptance
p = 0.4 says the data are *compatible* with H₀, not that H₀ is true — with n = 8, almost any null survives. Equivalence claims need an equivalence test (TOST) with a pre-specified margin, or an interval narrow enough to exclude meaningful effects (see lab 06).

### 5. Ignoring effect size because p < 0.05
With n = 100 000, a difference of 0.006σ is significant (z = 0.006σ√100000 ≈ 1.90); 0.001σ would need n ≈ 3.8×10⁶. p measures *incompatibility* driven by n; practical importance is the effect size and its interval. Significance ≠ relevance: Fisher's own warning that p is "at best a starting point."

### 6. Using the wrong reference distribution
t-test on strongly skewed small samples (use permutation or Wilcoxon), χ² approximation on cells with expected counts < 5 (the classical Cochran rule; merge cells or use exact Fisher), and z instead of t at small n (critical value 1.96 vs t₀.₀₂₅,₄ = 2.776 — a 42% larger margin).

### 7. Two-sample t with unequal variances
"Student's" t pools variances: s_p² = ((n₁−1)s₁² + (n₂−1)s₂²)/(n₁+n₂−2). When the *small* group carries the larger variance — n₁ = 10, σ₁² = 4σ₂², n₂ = 100 — the pooled SE underestimates the true SE of the difference by √(0.41σ²/0.1375σ²) ≈ 1.73×, so |T| is inflated 1.73×: a nominal 5% test rejects about 26% of the time under H₀ (normal approximation). Welch's Satterthwaite correction computes the right df and SE — hence its status as the default in modern software.

### 8. Repeated peeking at a fixed-n test
Interim looks inflate α: checking a fixed-n 5% test every day until p < 0.05 makes the true false-positive rate far above 5% (the test's independence assumptions are broken by stopping). Use group-sequential boundaries (O'Brien–Fleming) or the SPRT (Wald–Wolfowitz 1945), whose error rates hold under optional stopping.

## Self-check: could you defend these answers?

1. *"p = 0.049 and p = 0.051 — one is a discovery, the other isn't."* — The two are evidentially indistinguishable; the only honest report is the effect estimate and its interval. If you must act on a threshold, name the procedure that set it (pre-registered α, or the 0.005 proposal of Benjamin et al. 2018 — note z = 2.807 instead of 1.96, so the same n buys far less power).
2. *"We ran 12 variants and the best had p = 0.04."* — FWER = 1 − 0.95¹² = 0.4596: that result is more likely a false positive than not. Bonferroni requires p ≤ 0.05/12 = 0.00417 — report the *adjusted* p and the interval on the winner, or run a fresh confirmatory experiment on the chosen variant only.
3. *"The study found no effect, so the feature does nothing."* — Only if power was high: at 80% power a null result still occurs 20% of the time when the effect is real. What you can say: "effects of δ ≥ (z₀.₀₂₅ + z₀.₂₀)·SE are ruled out with 80% power" — the interval says which effect sizes are actually excluded.
4. *"Fisher's exact test is always safer than χ², so use it."* — Fisher is conservative (its actual size is below α, e.g. two-sided on [[8,2],[3,7]] gives p = 0.070 vs χ²'s 0.025 — a decision-flipping gap). Cochran's rule (all expected ≥ 5) decides: with expected counts 5.5/4.5 the χ² approximation is marginal, and reporting *both* with a note is more honest than picking whichever is significant.
5. *"Our A/B test peeked daily for a month; α is still 0.05."* — The nominal α assumes one look at the pre-set n. Continuous monitoring of a noise series crosses ±1.96 almost surely eventually (random-walk argument) — the realized false-positive rate is unbounded, not 5%. Only pre-planned looks (O'Brien–Fleming, α-spending, SPRT) keep the budget.
