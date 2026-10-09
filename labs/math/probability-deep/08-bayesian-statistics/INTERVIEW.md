# Interview: Bayesian Statistics

### Q1. Medical test: 1% prevalence, 99% sensitivity, 95% specificity. P(disease | +)?
**A.** 16.7%. P(+) = 0.01·0.99 + 0.99·0.05 = 0.0594; P(D | +) = 0.0099/0.0594 = 1/6. In odds: prior 1:99 × LR 19.8 = posterior odds 0.2:1 → 1/6. The follow-up to expect: "so should everyone test positive?" — no: the positive predictive value is governed by the base rate, which is why screening programs target high-risk populations (raising the prior) rather than relying on test accuracy alone.

### Q2. Derive the Beta–Binomial posterior and explain what the prior "is."
**A.** Prior π(p) ∝ p^{α−1}(1−p)^{β−1}; likelihood for k heads in n ∝ pᵏ(1−p)^{n−k}; product ∝ p^{α+k−1}(1−p)^{β+n−k−1} → Beta(α+k, β+n−k). In the mean formula the prior acts as α pseudo-heads and β pseudo-tails: posterior mean = (α+k)/(α+β+n) = the weighted average of prior mean α/(α+β) and data mean k/n. Beta(2,2) therefore has strength α+β = 4 against your n observations — with n = 1000 the prior's weight is 4/1004 ≈ 0.4%; with n = 5 it is 4/9 ≈ 44%.

### Q3. Credible interval vs confidence interval — and when do they numerically coincide?
**A.** Credible: 95% of the posterior mass lies in the interval, given model and prior — a statement about *this* θ. Confidence: 95% of repeated-sample intervals contain θ — a statement about the *procedure*; it does not license P(θ ∈ I). They coincide numerically with a flat prior, large n, and regular models (posterior ≈ N(θ̂, 1/I) and Wald ≈ likelihood-based ≈ Bayesian). They diverge exactly where it matters: small n, informative priors, parameters near boundaries.

### Q4. Your MCMC gives 50 000 draws. How do you know they're usable?
**A.** Four checks: (1) **split-R̂ < 1.01** across ≥ 4 over-dispersed chains — detects non-mixing and mode-splitting; (2) **ESS ≥ 400** for every quantity reported — 50 000 autocorrelated draws with τ = 100 are only 500 effective, and MCSE = sd/√ESS tells you the simulation error on your posterior mean; (3) **trace/rank plots** show a fuzzy caterpillar with no trend or stuck segments; (4) **posterior predictive checks** — even a perfectly converged chain is wrong if the model is. If diagnostics fail: non-centered parameterization, stronger/adaptive mass matrix, or reparameterize — never "just run longer" on a multimodal posterior.

### Q5. Bayes factor vs p-value — what does each measure?
**A.** p = P(data as extreme | H₀): compatibility of data with one model, no priors, no statement about H₁. BF₁₀ = P(D | M₁)/P(D | M₀): the *evidence ratio* between models, integrated over each model's prior — so it can favor either side, and posterior model odds = prior odds × BF (p-values have no such multiplication rule). BF is sensitive to the prior width under M₁ (Jeffreys–Lindley: a very diffuse prior dilutes evidence, favoring M₀), which is why you specify and sensitivity-check it. Rule of thumb scales (Kass & Raftery 1995: 3–20 moderate, >100 strong) are for *odds*, not error rates.

### Q6. "The prior is subjective — doesn't that make results irreproducible?"
**A.** Two answers. (1) The prior's *influence* is measurable: report its effective sample size beside n — Beta(2,2) contributes 4 pseudo-observations against n = 1000 (0.4%) — plus a sensitivity band over reasonable priors; conclusions that don't move were never hostage to subjectivity. (2) Where priors must be conventional they are standardized: half-Cauchy(0, 2.5) on scales (Gelman 2006), LKJ(2) on correlation matrices (Lewandowski, Kurowicka & Joe 2009). Irreproducibility comes from *undisclosed* choices, not from priors existing.

### Q7. Compute P(θ > 0) from a normal posterior — two ways.
**A.** Analytic: posterior N(1.2, 0.5²) gives P(θ > 0) = Φ(1.2/0.5) = Φ(2.4) = 0.9918 — standardize the threshold, read one normal table. From draws: the fraction of MCMC samples above 0, with MCSE = √(0.99 × 0.01 / 2000) = 0.002 at 2 000 effective draws. If the two disagree by more than ~2 MCSE, the normal approximation (not the sampler) is the thing to distrust — skew or a boundary is at work.

### Q8. Bayes' rule never says "prefer simple models" — so where does the complexity penalty come from?
**A.** From averaging. Evidence = ∫L(θ)π(θ)dθ: if the prior spreads mass over width 2 but the likelihood only fits within 0.1, at most about 0.1/2 = 5% of the model's prior territory earns credit, while a model whose prior sits on the fit keeps all of it. Flexibility is hedging, and hedging is billed — nothing in the rule says "simple," but a diffuse prior spends its own mass on θ values the data hate. This is also why BF moves with prior *width*: same rule, different bill (Jeffreys–Lindley).

### Q9. Thompson sampling or a fixed-horizon A/B test — when does each win?
**A.** Fixed-n wins when you need one pre-committed error rate for a yes/no decision (regulator, lab 07's contract) and traffic is cheap relative to review. Thompson wins when rounds are many and regret costs money: it exploits from the first pull (picks follow the posterior, weak arms die after a few observations), adapts to drift, and *cannot* peek because there is no interim test to violate — there is no α to defend. The price: no single error-rate sentence, so constraints (min allocation, equipoise) must be built into the sampling rule itself.

### Q10. Three schools, three students each. What does the hierarchy do that separate analyses can't?
**A.** Partial pooling: each school's estimate shrinks toward the grand mean by its own precision, so n = 3 borrows from the other schools rather than reporting noise or being discarded — and the shrinkage *weight* is itself estimated (between-school τ). When schools genuinely differ, τ grows and pooling weakens; when they don't, pooling is heavy. That is lab 06's bias-variance trade priced per group by a hyperprior instead of a hand-tuned knob — and it is why group-level conclusions from separate analyses systematically over-disperse.
