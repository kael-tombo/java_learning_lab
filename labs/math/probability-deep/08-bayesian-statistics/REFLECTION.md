# Reflection: Bayesian Statistics

## Do the update on paper
Prior Beta(2,2), data 9H/1T: write the three kernels (prior, likelihood, posterior), identify Beta(11,3), compute the posterior mean (0.7857), variance (0.01122) and P(p > 0.5) = 0.9888 via the binomial identity. If you can reproduce all four numbers unaided, the algebra of updating is yours.

## Questions to work through
1. The same data with priors Beta(0.5, 0.5), Beta(2,2) and Beta(100,100): compute the three posterior means. Which conclusions changed? Write the one sentence you would put in a report about prior sensitivity at n = 10.
2. State P(μ > 0 | data) as a Bayesian and as a frequentist. What does each refuse to say, and why? Under what decision loss is the Bayesian's statement the *optimal* action?
3. Spam filter with correlated words: naive Bayes multiplies P("viagra" | spam)·P("cheap" | spam). Given they co-occur, is the combined likelihood ratio too large or too small, and what is the practical consequence for the threshold?
4. MCMC: your chain gives a posterior mean of 0.791 with MCSE 0.02. The conjugate answer is 0.7857. Is there a bug? What would convince you either way (ESS, chain count, R̂)?
5. A Bayes factor of 3 for a diffuse prior on θ surprises your colleague ("my p-value was 0.001!"). Explain the Jeffreys–Lindley tension: what does a diffuse prior do to P(D | M₁)?

## Self-check table
| Concept | Can state it | Can compute it | Can break it |
|---|---|---|---|
| Bayes rule in odds form | | | |
| Beta–Binomial / Gamma–Poisson updates | | | |
| Credible vs confidence interval | | | |
| Marginal likelihood / Bayes factors | | | |
| MCMC diagnostics (R̂, ESS, MCSE) | | | |
| Prior sensitivity & hierarchical pooling | | | |

## Milestones
- [ ] Derive Beta(11,3) from Beta(2,2) + (9,1) without notes
- [ ] Compute the medical-test posterior (16.7%) both by table and by odds
- [ ] Explain why empirical Bayes on the same data double-counts
- [ ] Name the three MCMC diagnostics and their thresholds (1.01 / 400)
- [ ] Defend a specific prior for a specific problem in two sentences

- [ ] Reproduce a P(θ > 0) = 0.9918-style probability by standardizing a normal posterior — and again from draws
- [ ] Run a prior-predictive check that made you revise a prior, and say what the check caught

## The one habit worth keeping

Before every model: simulate from the prior, then fit, then simulate from the posterior — and ask each time whether the real data could plausibly have come from that draw. This loop (prior predictive → fit → posterior predictive) catches scale errors, over-strong priors, and wrong likelihood families before anyone quotes a 95% interval, and it costs nothing but a for-loop.
