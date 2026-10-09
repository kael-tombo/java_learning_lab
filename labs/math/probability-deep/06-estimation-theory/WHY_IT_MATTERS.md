# Why It Matters: Estimation Theory

## Everything reported is an estimate
A poll's "52% ± 3", a service's p99 latency, a model's learned weights, a sensor's calibration offset — all are point estimates plus a claim about uncertainty. Estimation theory is what makes "± 3" mean something: SE from information, intervals from Wald or likelihood ratio, coverage verified over repeated samples. Without it, error bars are decoration.

## Precision has a floor and a price
Cramér–Rao says Var(θ̂) ≥ 1/(n·I(θ)): to halve the error you either double n or find a statistic with more information (better measurement, fewer nuisance parameters). This is the arithmetic behind
- **clinical trials**: sample size from the target SE (lab 07 computes 63/arm for a 0.5σ effect at 80% power);
- **sensor design**: whether a cheaper sensor can meet the calibration spec at all (if I(θ) is too small, no n will save you);
- **A/B testing**: minimum detectable effect = function of n and variance, not of wishful thinking.

## Bias–variance is the design language of machine learning
Regularization (ridge/lasso), shrinkage estimators and early stopping all add bias to remove variance — the James–Stein result (1961) and empirical-Bayes shrinkage are the theoretical licenses. Understanding E[(θ̂ − θ)²] = bias² + variance is what separates "my model overfits" (too much variance, or selection on training likelihood) from a fix, rather than a hope.

## Bad estimation has a paper trail
- Quoting σ̂² with n instead of n−1 understates variance 10% at n = 10.
- Wald intervals on skewed positive parameters produce impossible negative bounds and under-cover.
- Baseline mean/σ for fraud detection poisoned by outliers (lab 06 SECURITY) — estimator choice *is* the security control.
- Reporting MLE point estimates without information-based SEs hides when the data were uninformative.

## The hand-off
Point estimates are inputs to decisions (lab 07: is θ̂ far enough from θ₀ to act?) and to updating (lab 08: turn the likelihood into a posterior). Knowing θ̂ without knowing its sampling distribution is precisely the gap this lab closes.

## Reading checklist for any published estimate

1. **Point estimate *and* its interval** — an estimate without a SE is an opinion with a decimal point; demand the interval and the n it came from.
2. **Which SE?** Observed information, sandwich, or bootstrap — and what each one assumes (i.i.d.? correct family? neither?). The label tells you which failure modes were ruled out.
3. **Which divisor, explicitly** — n or n−1, and consistency between the estimate and its SE (mixing them inflates or deflates every t-statistic in the paper).
4. **Bias at *your* n, not asymptotically** — asymptotic unbiasedness with a 10% bias at n = 20 means the interval is centered wrong for exactly the study you ran.
5. **For ratios, rates, variances: was the interval built symmetrically?** A ±z·SE on a positive parameter implies impossible negative values and under-covers; log-scale or profile LR is the repair.
