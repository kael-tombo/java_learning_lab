# Why It Exists: Bayesian Statistics

## The gap the rule fills
Frequentist probability is P(event | model): it can say how often data like yours occur if μ = 100, but never P(μ = 100 | data) — the quantity every practitioner actually wants. Three arguments forced the question:

1. **One-off events have no frequencies.** "Probability this machine fails before Tuesday" or "probability this defendant is guilty" has no long-run series to average over. Only a degree-of-belief semantics (Ramsey 1926/1931, de Finetti 1930s, Savage 1954) can attach a number at all.
2. **Existing knowledge must enter.** Re-running a clinical trial from a flat prior discards decades of safety data. The prior is the *only* place prior evidence lives; hierarchical models (school-level effects partially pooled to a population distribution) make this quantitative and automatic.
3. **Decisions need posteriors.** A decision under squared loss is E[θ | data]; under asymmetric loss it is a posterior quantile; expected utility integrates over the posterior. Wald's decision theory (1950) supplies the machinery — Bayes supplies the distribution it consumes.

## Why it took three centuries to compute
The rule is 1763; practical posteriors are 1990. Laplace could only integrate models where ∫θ^k e^{−θ} patterns made closed forms; Fisher and Neyman rejected subjective priors in the 1920s–30s (the "Bayesian desert" era); Jeffreys's *Theory of Probability* (1939) was ignored for a generation. **Gelfand & Smith (1990)** changed the constraint: MCMC turns "compute the integral" into "sample from it," and any model with a computable log-posterior became estimable. Stan/HMC and autodiff (2010s) removed the gradient burden.

## What the Bayesian frame uniquely provides
- **Direct probability statements** about parameters (credible intervals, P(θ > 0)).
- **Seamless pooling** through hierarchy — the fix for Simpson-type aggregation problems (lab 04) in a probabilistic form.
- **Occam's razor with a number**: the marginal likelihood penalizes complexity automatically.
- **A coherent answer to "how sure are you?"** for every quantity, including model index — the thing p-values structurally cannot do (COMMON_MISTAKES #1 across both paradigms).

## What it demands in return
A prior, documented and sensitivity-checked; and computational honesty — diagnostics (R̂, ESS) rather than a chain that "looked fine."

## What each frame can and cannot say, row by row

| Situation | Frequentist answer | Bayesian answer |
|---|---|---|
| "Is μ = 100?" after seeing data | P(data this extreme \| μ = 100) | posterior density at 100, normalized |
| Zero failures in 1 000 trials | upper bound 3/1000 (rule of three) | P(rate > 10⁻³ \| 0 failures), prior stated |
| Sun rose for 5 000 years | no probability about tomorrow's sun | rule of succession: failure = 1/(1 826 252) ≈ 5.5 × 10⁻⁷ |
| A defendant's guilt | "guilt rate" over repetitions that never happen | P(guilt \| evidence) — one-off, by design |
| 3 students in each of 3 schools | three under-powered tests or one pooled test | hierarchy shrinks each group by estimated τ |
| Which of two models produced D | a p-value per model, no ratio between them | posterior odds = prior odds × BF |

The frequentist column is not wrong — it answers questions about *procedures*, which is exactly what lab 07's error rates need. It goes silent where the practitioner asks about *this* θ, *this* one-off event, *this* model index — and the Bayesian column speaks there because the prior is the one place one-off reasoning is allowed to live.
