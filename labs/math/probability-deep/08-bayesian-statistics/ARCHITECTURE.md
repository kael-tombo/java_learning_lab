# Architecture: Bayesian Statistics Implementation

## Package layout
```
com.mathlab.bayes
├── model/       LogDensity (logLik + logPrior), BinomialModel, PoissonModel, NormalModel
├── conjugate/   BetaBinomial, GammaPoisson, NormalNormal          (exact path)
├── prior/       Beta, Gamma, Normal, HalfCauchy, JeffreysReference
├── sampler/     MetropolisRW, Gibbs, HMC (autodiff gradients), ADVI
├── diagnostics/ SplitRhat, ESS, MCSE, TraceStats
├── summarize/   CredibleInterval (equal-tail, HDI), PosteriorSummary
├── compare/     MarginalLikelihood (bridge), BayesFactor, LOO-CV
└── verify/      ConjugateOracle, CoverageStudy
```

## Design decisions
1. **One LogDensity contract.** Priors, likelihoods, samplers and optimizers meet at `double logDensity(double[] θ)`. Conjugate classes are a *separate*, exact path — never synthesized from the generic one — so tests can compare MCMC against 11/14 directly.
2. **Priors are values with metadata.** Each prior records its effective strength (α + β for Beta) and its parameterization (flat-in-p vs flat-in-log-odds); summaries print both, so COMMON_MISTAKES #5 ("uniform in the wrong parameter") surfaces in output rather than in review.
3. **Diagnostics mandatory before summaries.** `PosteriorSummary.of(chain)` throws `InsufficientDiagnostics` unless split-R̂ < 1.01 and ESS ≥ 400 hold for every summarized quantity. There is no API to print a 95% credible interval from an undiagnosed chain.
4. **Chains are immutable arrays of primitives.** Diagnostics, summaries and plots all read the same `double[c][n][p]` block; no sampler-specific state leaks past sampling.

## Validation invariants
- Conjugate vs MCMC posterior mean agreement within 2·MCSE (MCSE = sd/√ESS) on the Beta(11,3) oracle: 0.7857.
- Grid-evaluated posterior integrates to 1 ± 1e-9.
- Prior predictive simulation reproduces the prior's declared moments.
- Coverage study: credible intervals built from a well-specified model cover at the nominal rate *averaged over the prior* (a property frequentist coverage does not share — checked separately with a fixed-θ study).

## Test topology
Hand-computed oracles: Beta(2,2) + 9H1T → Beta(11,3), mean 0.7857, var 0.01122, P(p>0.5) = 0.9888; medical-test posterior 1/6; Poisson-Gamma update arithmetic; seeded Metropolis run whose ESS/R̂ land in the documented acceptance bands.

5. **Model index is data too.** `compare/` returns prior odds × BF as *posterior* odds and refuses to print "model 1 wins" without an explicit prior-odds input — COMMON_MISTAKES #8 and #10 are unrepresentable through this API.
6. **Prior predictive is a first-class test.** `verify/PriorPredictiveCheck` renders prior-predictive draws before any fitting; a model whose prior predictive excludes the observable's plausible range fails CI the way a wrong integral does — before a single posterior is sampled.
