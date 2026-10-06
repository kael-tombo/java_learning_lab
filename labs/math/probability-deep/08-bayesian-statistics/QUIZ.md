# Bayesian Statistics — Quiz (15 Questions with Worked Answers)

Priors, posteriors, conjugacy, and the boundary cases where Bayes and frequentism genuinely disagree.

---

## Q1 — Bayes theorem needs care with continuous variables
**Q.** State Bayes' theorem for a parameter with a prior and a likelihood.

**A.** p(θ|x) = p(x|θ)·p(θ) / p(x), where p(x) = ∫p(x|θ)p(θ)dθ is the marginal likelihood (evidence). The posterior is proportional to likelihood × prior. The catch: "p(θ)" for a continuous θ is a *density*, not a probability; statements like "P(θ ∈ A)" are what carry meaning, and those come from integrating the density. A prior density and a posterior density are well-defined, but a flat "prior probability" for a continuous parameter is not — it is a density, and the reference measure matters.

---

## Q2 — Conjugacy: beta-binomial
**Q.** Derive the posterior for the binomial success probability under a Beta prior.

**A.** Prior: p ~ Beta(α, β), density p^{α-1}(1-p)^{β-1}. Likelihood: x successes in n trials, L(p) ∝ p^x (1-p)^{n-x}. Posterior ∝ p^{α+x-1}(1-p)^{β+n-x-1} — a Beta(α+x, β+n-x). The parameters add exactly as if α, β were prior counts of successes and failures. So the Beta prior is conjugate: the posterior is in the same family. This is why Beta-Binomial, Gamma-Poisson, Normal-Normal, and Dirichlet-Multinomial are the "closed-form" pairs; outside them, you need numerical integration or MCMC.

---

## Q3 — The prior never washes out completely
**Q.** Two scientists with different priors analyse the same data — do they agree?

**A.** In the limit of a lot of data, asymptotically yes: the likelihood dominates and both posteriors concentrate on the same point (Bernstein–von Mises theorem, under regularity). For a fixed, moderate sample, they do not: a strong prior shifts the posterior mean. The often-heard claim "with enough data the prior does not matter" is the asymptotic statement; it is false at finite n, and the magnitude of the prior's influence is roughly the prior precision divided by prior+data precision. A prior that encodes real information (e.g. "drug efficacy cannot be negative") should not wash out — it is the regularisation that keeps the inference sane.

---

## Q4 — Improper priors can give improper posteriors
**Q.** Why does "flat prior on the whole real line" sometimes fail?

**A.** A flat prior π(θ) ∝ 1 on ℝ has infinite total mass — it is not a proper probability distribution. The posterior p(θ|x) ∝ L(θ;x)·1 is proper only if the likelihood is integrable in θ. If the likelihood has a fat tail in θ (e.g. a uniform location model where L(θ) is flat beyond the data), the posterior remains improper, and "P(θ ∈ A)" is undefined. The fix is to ensure the likelihood is integrable, or to use a proper weakly-informative prior. Improper priors that yield proper posteriors are often convenient, but the integrability check is on you.

---

## Q5 — Credible vs confidence intervals
**Q.** A 95% credible interval vs a 95% confidence interval — what does each condition on?

**A.** A 95% credible interval contains 95% of the posterior mass: P(θ ∈ C | x) = 0.95, conditioning on the observed data. A 95% confidence interval guarantees coverage over the *sampling distribution of the procedure*: over many datasets, 95% of the intervals contain the true θ. The credible interval conditions on this dataset; the confidence interval conditions on the procedure. Numerically they often coincide for large samples (Bernstein–von Mises), but the interpretation is fundamentally different, and conflating them is the most common Bayesian–frequentist slip.

---

## Q6 — MAP vs posterior mean
**Q.** When does the MAP equal the MLE, and when does the posterior mean differ?

**A.** The MAP maximises the posterior density p(θ|x) ∝ L(θ;x)·π(θ). With a flat prior, the prior drops out and the MAP equals the MLE. With an informative prior, the MAP is pulled toward the prior mode, while the posterior mean is pulled too but additionally weights the posterior mass — it minimises the expected squared error under the posterior. The two coincide when the posterior is symmetric and the prior is unimodal; they diverge for skewed posteriors (e.g. near a boundary, or with a heavy-tailed prior). In practice the posterior mean is the standard point estimate under squared error; the MAP is what MAP-estimation methods report.

---

## Q7 — Bayes factors
**Q.** How does a Bayes factor compare hypotheses, and what can go wrong with flat priors?

**A.** The Bayes factor B₁₀ = p(x|H₁)/p(x|H₀) compares the marginal likelihoods — how well each hypothesis predicted the data. Unlike a p-value, it is a measure of *evidence for one hypothesis over the other*, not "evidence against H₀ alone." The catch: the marginal likelihood depends on the prior over the parameters *within* each hypothesis. A diffuse prior under H₁ spreads mass thinly, lowering the marginal likelihood — the "Lindley paradox": with a very flat prior under the alternative, the same data can favour the null. Bayes factors are only meaningful with priors that encode a real predictive distribution, not a placeholder.

---

## Q8 — The likelihood principle
**Q.** State the likelihood principle and why frequentist tests violate it.

**A.** The likelihood principle: all evidence from the data is in the likelihood function; two experiments with the same likelihood function carry the same evidence about θ. Frequentist p-values violate it because they integrate the sampling distribution over *all possible outcomes*, not just the one observed — two experiments that generate the same likelihood for the observed data but different sample spaces get different p-values. The stopping rule that generated the data, for instance, does not enter the likelihood but does enter the p-value. Bayesian inference, being a functional of the likelihood and prior only, satisfies the likelihood principle by construction.

---

## Q9 — Posterior predictive checking
**Q.** How do you check whether a Bayesian model fits?

**A.** Draw samples θ⁽ˢ⁾ from the posterior p(θ|x_obs), then generate replicated data x^{rep,(s)} from p(x|θ⁽ˢ⁾). Compare the distribution of a test statistic T(x) computed on the replicates to T(x_obs). If T(x_obs) is in the extreme tail of the replicate distribution, the model is missing structure that T captures. This is the Bayesian analogue of a goodness-of-fit test, but built from the predictive distribution instead of the sampling distribution of a statistic. It is the standard sanity check after MCMC: a model that cannot reproduce a summary of the observed data needs a different structure, not a different prior.

---

## Q10 — Hierarchical models and partial pooling
**Q.** Why does a hierarchical model shrink extreme group estimates?

**A.** In a hierarchical model, group-level parameters θ_j are drawn from a common distribution with mean μ and variance τ². The posterior for θ_j is a precision-weighted average of the group's own data and the population mean: θ_j | data heavy-shrink where the group has few samples. Complete pooling (one common mean) over-shrinks; no pooling (separate fits) over-fits. Partial pooling gets the variance-bias tradeoff right: small groups shrink hard toward the mean, large groups barely move. This is the formal version of "borrowing strength," and it is why hierarchical models are the default for grouped data — sports batting averages, hospital outcomes, A/B test segments.

---

## Q11 — Conjugate prior updating as a sufficient statistic
**Q.** Why is the Beta prior update a sufficient statistic of the data?

**A.** After n trials, the posterior depends on the data only through the count of successes x, not through the order in which they occurred. The pair (α, β) acts as a counter of successes and failures — a sufficient statistic for the binomial. The prior encodes a pseudo-sample of α successes and β failures; the posterior adds the observed counts. So the Beta prior is not just a "guess" — it is a data summary, and the update is the same likelihood-computation that a frequentist would do on a sample of size α+β.

---

## Q12 — MCMC: what is the stationary distribution?
**Q.** In Metropolis–Hastings, what does the chain converge to?

**A.** The chain is a Markov chain on θ-space with stationary distribution p(θ|x): it leaves the posterior invariant. Starting from any θ⁽⁰⁾, the distribution of θ⁽ᵗ⁾ converges to p(θ|x) under mild conditions. The Metropolis–Hastings accept-reject step is exactly what enforces detailed balance with respect to p(θ|x) ∝ L·π — the proposal can move freely, but the accept ratio π·L·q_reverse/(L·π·q_forward) makes the chain reversible with the posterior as its stationary law. After a burn-in, the chain draws are (correlated) samples from the posterior.

---

## Q13 — Bayesian decision theory
**Q.** Why is the posterior mean the right point estimate under squared error?

**A.** For a point estimate δ(x), minimise the posterior expected loss E[(θ-δ(x))² | x]. Expanding: = E[θ²|x] - 2δ(x)E[θ|x] + δ(x)². Differentiating in δ and setting to zero gives δ*(x) = E[θ|x] — the posterior mean. For absolute-error loss the median is optimal; for 0-1 loss it is the mode. So "Bayesian point estimation" is not one procedure; it is a family indexed by the loss function. Picking the posterior mean silently encodes squared error as the loss; the MAP silently encodes a mode-seeking loss.

---

## Q14 — The base-rate fallacy and Bayes
**Q.** A test is 99% sensitive and 99% specific; the disease prevalence is 0.1%. If I test positive, what is the probability I have the disease?

**A.** By Bayes: P(D|+) = P(+|D)P(D) / [P(+|D)P(D) + P(+|¬D)P(¬D)] = 0.99·0.001 / (0.99·0.001 + 0.01·0.999) = 0.00099 / (0.00099 + 0.00999) ≈ 0.09. Despite the 99% numbers, a positive test raises the probability from 0.1% to only ~9% — because the false-positive rate applies to the much larger healthy group. This is the base-rate fallacy, and it is the concrete reason Bayes' theorem is not optional in screening tests and diagnostic screening.

---

## Q15 — Prior predictive vs posterior predictive
**Q.** What is the difference, and which one do you check against data?

**A.** Prior predictive: p(x) = ∫p(x|θ)π(θ)dθ — the marginal distribution of data before seeing any. Posterior predictive: p(x_new | x_obs) = ∫p(x_new|θ)p(θ|x_obs)dθ — the distribution of new data given the observed data. The prior predictive is a *sanity check on the prior+likelihood* (does the model say plausible data *before* fitting?); the posterior predictive is a *fit check* (does the model reproduce the data *after* fitting?). The two answer different questions and both are useful; conflating them is a standard source of confusion.

---

