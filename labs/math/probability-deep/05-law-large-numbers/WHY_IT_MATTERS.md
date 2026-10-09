# Why It Matters: Law of Large Numbers and CLT

## What would break without it
- **Every confidence interval** in lab 06 assumes X̄ − μ is approximately N(0, σ²/n). Without the CLT there is no 1.96, no Student t, no "±2 percentage points."
- **Polling and A/B tests**: a 1 000-person poll reports ±3% precisely because SE = √(p(1−p)/n) with n = 1000 gives ≤ 1.6% and 1.96 × 1.6 ≈ 3.1%. The number on the news is a CLT artifact, not a convention.
- **Quality control**: Shewhart's x̄ charts (1924) at Western Electric treat out-of-control signals as normal-tail events; the whole of statistical process control is "assume CLT, flag 3σ."
- **Monte Carlo integration**: error ~ 1/√N is the reason a simulation can certify π to 4 digits with 10⁸ samples and no way to get there faster with the same method.

## The failure mode that costs money
Convergence of averages is *not* convergence of tails. Insurance and fund returns with heavy tails (Pareto α ≤ 2, no finite variance) show sample means that look stable for years and then jump — Mandelbrot's cotton-price work (1963) was exactly this observation. A risk model that quotes "our loss distribution is normal with σ = 5%" understates 1-in-100-year events when the true tail is Pareto.

## The failure mode that misleads people
"The coin will land heads about half the time" is LLN for *fractions*; it does not say heads and tails alternate or that a 10-head streak is unlikely *where it occurs*. Gambler's-fallacy thinking — expecting the streak to be "corrected" — confuses the average over a sequence with a constraint on the next draw. The distribution of the longest run of heads in n flips is a separate calculation (it grows like log₂ n).

## The number to remember
Relative precision improves as 1/√n: to halve the standard error you must quadruple the data. That single scaling governs sample-size planning in lab 06, power in lab 07, and bootstrap width in every simulation you will run.

## Decision table: what 1/√n governs in the real world

| Field | The quantity | The 1/√n consequence | Cost of ignoring it |
|---|---|---|---|
| Polling | ± margin at 95% | 1000 respondents ≈ ±3.1% | Published margins that are 2–4× too tight |
| A/B testing | detectable effect at fixed power | halve the MDE → 4× the traffic | Tests stopped early; "wins" that don't replicate |
| Monte Carlo (finance, rendering) | error of a simulated expectation | 10⁶ draws ≈ 3 good digits | Certificates of precision the run never earned |
| Manufacturing (Shewhart charts) | control limits from σ/√n | out-of-control = a 3σ *mean* shift | Scrap from alarms on normal noise, or missed drift |
| Clinical trials | CI width for the primary endpoint | sample size computed once, up front | Underpowered trials (lab 07's 173/arm arithmetic) |
| Telemetry baselines | warm-up time for a learned threshold | n = 100 → ±2.5%, n = 400 → ±1.3% | Monitors blind during warm-up; false alarms after |

## Reading checklist for any claim with an error bar

1. **Is the statistic a mean/sum?** Quantiles, maxima and ratios have different limits (EVT, delta method) — the √n rule doesn't transfer.
2. **What n produced it, and what n_eff?** If the source is a time series, the honest number is smaller; ask for the ACF.
3. **What is the bias floor?** If the estimator converges to the wrong value, the interval's width is irrelevant.
4. **How many metrics were examined before this one was reported?** Selection widens the *effective* error bar; family-wise rate belongs next to every p and every ±.
