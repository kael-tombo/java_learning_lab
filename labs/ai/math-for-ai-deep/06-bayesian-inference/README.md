# 06-bayesian-inference - Bayesian Inference
## Overview
Conjugate Beta-Binomial: posterior = Beta(a+heads, b+tails). MAP adds a log-prior penalty to the likelihood, shrinking estimates toward the prior vs raw MLE.
## Key formulas
- Posterior mean = (a+h)/(a+b+n).
- MAP = argmin NLL + prior penalty (here 0.5 m^2).
## What the snippets show
- Mt06A: 0.5 -> 0.6429 update trace.
- Mt06B: grid minimum at m=2.0 over four candidates.
## Try it
Use 70/100 heads and watch the posterior converge toward 0.7.
## Formula reference
- Beta(a,b) prior + Binomial(h,t) -> Beta(a+h, b+t); mean (a+h)/(a+b+n).
- MAP = argmax loglik + logprior; MLE drops the prior term.
- Posterior predictive integrates over posterior, wider than plug-in.
## Worked example
- 2+7 = 9 heads-ish mass; 2+3 = 5; total 14; mean 9/14 = 0.6429.
- Prior weight 4 pseudo-counts pulls MLE 0.7 down to 0.6429.
- MAP grid: 10.5 / 7.0 / 7.88 / 10.5: quadratic NLL + 0.5 m^2 penalty.
## Pitfalls
- Prior sensitivity at small n; report prior + likelihood separately.
- MAP point hides uncertainty; full posterior when stakes high.
- Conjugacy is special; general models need MCMC/variational.
## Connections
- Regularization penalties are log-priors in disguise (L2 = Gaussian).
- RM training in RLHF is Bayesian-ish preference modeling.
## Exercises
1. Update with 70/100 heads; compare means.
2. Grid-search MAP with prior var 10.
3. Show MLE = MAP as prior flattens.
