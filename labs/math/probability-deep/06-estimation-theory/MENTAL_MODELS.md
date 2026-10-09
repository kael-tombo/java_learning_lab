# Mental Models: Estimation Theory

## 1. An Estimator Is a Machine, an Estimate Is One Output
θ̂ = g(X₁, …, Xₙ) is a function of random inputs — it has a sampling distribution *before* you see data. The number you report is one draw from that distribution. Everything (bias, variance, CI) is a property of the machine; your single output cannot show you its spread.

## 2. MSE Is a Budget You Allocate
MSE = bias² + variance. A biased-but-tight estimator (shrinkage, MLE of Uniform's endpoint) and an unbiased-but-loose one (moment estimators) are two allocations of the same budget. Maximum likelihood buys zero asymptotic bias in regular families at the cost of small-sample bias in some; Bayes estimators (lab 08) accept bias for large variance reductions.

## 3. Fisher Information = Curvature
I(θ) = −E[∂²ℓ/∂θ²]: a log-likelihood that curves sharply means small parameter changes wreck the fit → data are informative; a flat ridge means many θ explain the data equally → θ̂ will be noisy. The Cramér–Rao bound 1/(n·I) then reads: *precision is curvature times data*. Plot ℓ(θ) and you see your SE.

## 4. Sufficiency = No Data Left Behind
A statistic T is sufficient if the likelihood factors as g(T(x), θ)·h(x) — all θ-relevant content compressed into T (binomial: only k matters, not which trials succeeded). Estimating from T loses nothing, and Rao–Blackwell says any estimator can be improved by conditioning on T until nothing remains to condition on.

## 5. Confidence Is About the Procedure, Not the Parameter
A 95% CI is a rule that covers the true θ in 95% of repeated samples — the interval you hold is one realization and either contains θ or doesn't. Saying "there is a 95% probability θ lies here" is the Bayesian reading (lab 08); the frequentist reading is about *coverage of the recipe*.

## 6. Two Rates: √n and n
Regular families: √n(θ̂ − θ) → N(0, 1/I) — Gaussian, everyone's default. Endpoint/support problems (Uniform(0,θ), Pareto tail index): convergence at rate n with extreme-value, non-Gaussian limits (Wilks' theorem also fails). Recognizing which regime you are in decides your error bars and your sample-size math.

## 7. The Likelihood Is a Surface, Not a Number

L(θ) after the log is a landscape: its peak is θ̂, its curvature at the peak is the information, its ridge width is your SE. Optimization problems become topography problems — a long ridge means two parameters trade off (correlation), a boundary peak means asymptotic normality fails (Uniform's max, mixture weight = 0), and a flat top means the data cannot identify the parameter at all. Reading a likelihood profile tells you more about whether to trust θ̂ than any convergence flag.

## 8. Rao–Blackwell Is Compilation

Conditioning a crude estimator on the sufficient statistic is a *rewrite*: same target, provably smaller variance, no data lost. The mental move generalizes beyond the theorem — whenever a statistic is sufficient, any estimator that ignores it is doing unnecessary work; and whenever you *can't* condition (no sufficient statistic exists, as in the t-distribution's scale), that's the signal that exact variance formulas won't be found and the bootstrap is the honest path.

## 9. Intervals Are Tests Run Backwards

A 95% CI is the set of θ₀ that a test would not reject at α = 0.05 — Wald (center at θ̂, flat curvature), LR (uses the actual likelihood drop χ²₁ = 3.84), and score (evaluates curvature at θ₀, not at θ̂) are three different tests inverted, and they disagree exactly when the likelihood is asymmetric or the boundary is near. Ask "which test was inverted?" whenever an interval surprises you; the answer explains Wald-vs-Wilson-vs-profile discrepancies without any of them being "wrong."
