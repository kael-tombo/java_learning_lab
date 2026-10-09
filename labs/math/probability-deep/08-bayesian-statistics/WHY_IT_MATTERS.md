# Why It Matters: Bayesian Statistics

## It is the only framework that answers the question people ask
"Is the treatment working?" "What is the probability this segment converts better?" "What happens if we ship?" Bayesian inference returns P(statement | data, model) directly: posterior means for decisions, credible intervals for reporting, posterior predictives for forecasting. Frequentist machinery returns P(data | null) and a procedure's coverage — powerful, but a translation the practitioner must perform themselves.

## Where it is already load-bearing
- **Spam filtering**: naive-Bayes odds per word (Graham 2002) — probably the most-deployed Bayesian computation on earth.
- **A/B and adaptive experimentation**: posterior-based bandits (Thompson sampling) choose the variant *proportionally to its posterior probability of being best*, trading exploration/exploitation without a fixed-horizon test — Thompson (1933), still the standard in ad ranking and clinical trial adaptive designs.
- **Medicine**: posterior probabilities of efficacy drive phase-II decisions; Bayesian hierarchical models pool multi-site trial data (partial pooling, as treated in Gelman et al., *Bayesian Data Analysis*).
- **Reliability/rare events**: with 0 failures in 1000 trials, the frequentist 95% upper bound on failure rate is 3/1000 (rule of three) while the posterior with a weak prior concentrates nearby — but only Bayes can say "the probability the rate exceeds 10⁻⁴ is 0.97."

## Hierarchical modeling is the practical superpower
School-level test scores, patient-level reactions, user-level conversion rates: exchangeable groups share strength via a population prior. This shrinks noisy group estimates toward the mean exactly in proportion to their data (partial pooling) — automatic regularization (lab 06's bias-variance tradeoff, priced by the hierarchy) and the correct handling of groups that individually have n = 3.

## The costs, stated plainly
1. **Prior sensitivity** must be reported for small n — otherwise the prior is doing the work invisibly.
2. **Computation is real**: MCMC needs ESS ≥ 400 and split-R̂ < 1.01 per reported quantity; a fast wrong answer (unconverged chain) is worse than a slow right one.
3. **Model criticism still required**: posteriors are conditional on the model; posterior predictive checks (lab 03's families) are the Bayesian's goodness-of-fit.

## The hand-off
Every earlier lab reappears inside one formula: axioms (01) guarantee the posterior is a probability measure, random variables (02) define θ, distributions (03) define the likelihood, multivariate structure (04) appears in hierarchical priors, LLN/CLT (05) justify prior-fading and MCMC error bars, estimation (06) supplies MLEs as posterior modes, and testing (07) reappears as Bayes factors.

## A decision, priced end to end

Two ad variants; the posterior on lift Δ = p_B − p_A is N(0.010, 0.006²) — +1.0 points with 1-σ 0.6 points. Three numbers fall out of that one distribution, with no new data:

1. **P(Δ > 0) = Φ(1.667) = 0.952** — the probability statement a p-value cannot make directly.
2. **E[Δ | Δ > 0] = 0.0106** (truncated-normal mean) — the *expected* lift if the variant is better, which is what a ship decision under linear loss actually consumes.
3. **What more data buys**: posterior σ falls as 1/√(n), so doubling traffic takes 0.006 to 0.0042 — whether the wait is worth it is (cost of delay) versus (posterior mass on bad outcomes × downside).

That is the full loop lab 06 could only approximate with a point estimate: estimate, uncertainty, decision — one posterior, no translation table between three frameworks, and the answer to "how sure are you?" is a number with units.
