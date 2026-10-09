# How It Works: Hypothesis Testing

## 1. The null supplies a reference distribution
Assume H₀ (μ = 100, σ = 8) plus a sampling model: under H₀, x̄ ~ N(100, 8²/25) = N(100, 2.56), so SE = 1.6 and (x̄ − 100)/1.6 ~ N(0,1) *if H₀ is true*. The test statistic is this standardized distance; everything else is reading its tail.

## 2. p is the probability of data *at least this far*
Observed t = 1.25 → p = 2·P(T₂₄ > 1.25) = 0.223. The computation is pure probability under H₀ — no priors, no P(H₀). The statement it licenses: "data this incompatible with μ = 100 occur about 22% of the time under μ = 100." Whether that makes μ = 100 a good belief is lab 08's question.

## 3. The CI is the same test, run for every θ₀
The 95% CI is {θ₀ : the test of H₀: θ = θ₀ does not reject at 0.05}. That's why the interval (98.70, 105.30) contains 100 whenever p > 0.05 — not a coincidence but an algebraic identity (inversion). It also explains one-sided tests producing one-sided intervals.

## 4. Power comes from the alternative's distribution
Under H₁ (true mean shifted by δ·σ), the statistic is N(λ, 1) instead of N(0,1) with noncentrality λ = δ√n (one-sample) or δ√(n/2) per group (two-sample), so power = P(Z > 1.96 − λ) + P(Z < −1.96 − λ). Check both STEP_BY_STEP numbers this way: one-sample, n = 25, δ = 0.5 → λ = 2.5, power ≈ Φ(2.5 − 1.96) = Φ(0.54) ≈ **0.71**; two-sample, n = 63/group → λ = 0.5·√31.5 = 2.81, power ≈ Φ(0.85) ≈ **0.80**. Everything in power analysis is this geometry: noncentrality versus the critical value.

## 5. Why corrections are union bounds
With m independent tests, P(any false positive) = 1 − (1 − α/m)ᵐ → 1 − e^{−α} ≈ α for Bonferroni — and the union bound Σ P(FPᵢ) ≤ m·(α/m) = α holds *without* independence (Holm and Bonferroni both rest on this). BH is different in kind: it controls E[V/max(R,1)] ≤ q, a ratio of counts — the right currency when you are hunting true signals among thousands.

## 6. Choosing between Fisher and Neyman–Pearson
If you will *act* on the result (ship the feature, reject the batch), you are in Neyman–Pearson territory: pre-specify α, β and n, report the decision and the effect size. If you are *summarizing incompatibility* in an observational study, Fisher's p + interval + effect size is the honest summary — with "statistically significant" replaced by "the data are/aren't incompatible with θ = θ₀ at this sample size."

## 7. Worked: two-proportion power end to end

Goal: detect 10% → 12% conversion (δ = 0.02), α = 0.05 two-sided, power 0.80. Standard error under H₁ uses both arms: SE = √(p̄(1−p̄)/n · 2) with p̄ = 0.11 → 0.4425/√n, plus the observed spread √(0.10·0.90/n + 0.12·0.88/n) = 0.4423/√n. The formula (z₀.₀₂₅·0.4425 + z₀.₂₀·0.4423)²/δ² = (1.960·0.4425 + 0.8416·0.4423)²/0.0004 = 3 841 per arm. Two lessons ride along: n scales as 1/δ² (a 2-point lift needs 4× the traffic of a 1-point lift), and moving α to 0.005 (the 2018 proposal, z = 2.807) inflates this same design by (2.807 + 0.842)²/(1.960 + 0.842)² = 1.70× — stricter thresholds must be paid for in traffic.

## 8. Worked: what correction does to a borderline result

Observed p = 0.04 from 12 variants. Bonferroni: compare to 0.05/12 = 0.00417 → the result does not survive; Holm: sort all 12 p's, the smallest must clear 0.00417, the next 0.05/11, … — same first hurdle. BH at q = 0.05 would keep it only if at least k of the p's satisfy p₍ₖ₎ ≤ 0.05·k/12; with a single p = 0.04 that needs 0.04 ≤ 0.00417 · k/1 — k ≥ 9.6, so 10 of 12 tests must be at or below 0.04, which they are not. All three agree here: report the unadjusted p with its interval and state that the family of 12 was searched — the *search* is the fact, not the star.

## 9. The pipeline in order, with one design's numbers

Fix the design first: baseline 10%, minimum interesting lift 2 points, α = 0.05 two-sided, power 0.80.

1. **Power calculation sets n** — from section 7: 3 841 per arm; this happens *before* any data exists.
2. **Fix the test statistic and reference distribution** — two-proportion z (or the pooled χ², identical here); switching to "whatever looks best" after seeing data re-opens the type-I error you just priced.
3. **Run to n, then compute once** — pooled p̂ = (x₁+x₂)/(2n), SE₀ = √(p̂(1−p̂)·2/n), z = (p̂₁−p̂₂)/SE₀.
4. **Convert to p, apply the family correction** — Holm/BH across the pre-declared family only; tests invented later join a *new* family and need their own confirmation.
5. **Report estimate + interval** — (p̂₁−p̂₂) ± 1.96·SE_unpooled, with the raw p and the adjusted p side by side.
6. **Decide against the pre-committed rule** — the decision cites the rule, not the number: "Holm-adjusted p = 0.018 < 0.05, effect +2.1 points [0.7, 3.5]" (±1.96 × 0.0071 at n = 3 841 = ±1.4 points).

Steps 1–2 are design; steps 3–5 are arithmetic; step 6 is contract. Most failed replications trace to step 1 (n chosen by data availability) or step 2 (statistic chosen by data appearance), never to the algebra in between.
