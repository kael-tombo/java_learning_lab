# Why It Matters: Hypothesis Testing

## Every gate you have ever passed through used one
Clinical trials (phase III decisions at α = 0.05 with pre-specified interim looks), drug safety signals, quality-control lot acceptance, A/B tests behind every product feature, fraud-model launches, scientific replication — all are formal tests with error budgets. If the budget is not declared in advance, it is being overspent silently.

## The cost of getting it wrong is asymmetric and knowable
- **Type I** (false approval): shipping a useless or harmful feature, publishing a false effect. Its long-run rate is exactly α *if the procedure is honest*.
- **Type II** (missed effect): an underpowered trial (n too small for δ) that ends "no difference" while a real effect exists. Power analysis (n = 63/arm for δ = 0.5σ at 80%) converts "we couldn't tell" into "we were only able to detect effects this big."

## Multiplicity is everywhere and invisible
Any dashboard with 20 cards is doing 20 tests: 64% chance of a "significant" card under pure noise. Genomics at 10⁶ tests, security endpoints, model metrics — the correction (Holm, BH) must be applied to the *family actually inspected*, including the ad-hoc looks nobody logged. This single mistake accounts for a large share of failed replications.

## What testing does *not* give you
- Not P(H₀ | data) — for that you need priors and a posterior (lab 08).
- Not effect size or practical importance — a p-value shrinks with n; "significant at n = 10⁵" can be a 0.1% difference.
- Not model validity — a test answers a question *inside* an assumed model; if the model is wrong (lab 03 diagnostics), the null distribution is wrong.

## The disciplined version, in one line
Pre-specify the hypothesis, α, tail, endpoint and sample size; correct across the family; report the effect size with its interval; and treat p as compatibility-with-the-null, not as a verdict. That contract is what makes the mathematics trustworthy in trials, releases and audits alike.

## Decision table: which error rate, which correction, which design

| Situation | Controlling what | Design choice |
|---|---|---|
| One pre-registered endpoint, fixed n | FWER = α | Standard z/t test; report effect + interval |
| k secondary/guardrail metrics alongside | FWER across k | Holm step-down (uniformly ≥ Bonferroni power) |
| 10⁶ genome-wide scans, many true signals expected | FDR = q | Benjamini–Hochberg at q = 0.05 |
| Continuous monitoring (fraud, A/B dashboards) | Error under optional stopping | SPRT, CUSUM/EWMA, or O'Brien–Fleming α-spending |
| Small n, skewed/exchangeable data | Size accuracy | Permutation (B ≥ 9999, MC SE ≈ 0.0022) |
| Expected counts < 5 in a χ² table | Approximation error | Fisher's exact or merged cells — never raise α |
| "No difference found" | Ability to see δ_min | Power ≥ 0.80 at the smallest effect of interest (n = 63/arm for δ = 0.5σ) |

## Reading checklist for any significance claim

1. **How many tests were inspected**, and what correction covers them — including unplanned cuts.
2. **Stopping rule**: fixed n (declared when?), pre-planned interim, or SPRT — "peeked until significant" voids the α.
3. **Effect size with interval**, not just p — and whether the interval's band matters practically.
4. **Power or MDE at the design**: what effect size was this study capable of seeing? Non-significance is only informative relative to it.
5. **Which reference distribution** (z, t, χ², permutation, Fisher) and whether its assumptions hold at this n.
