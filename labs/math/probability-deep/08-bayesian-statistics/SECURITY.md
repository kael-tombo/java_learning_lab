# Security: Bayesian Statistics

## Spam filtering is the canonical deployed Bayes filter
**Paul Graham's "A Plan for Spam" (2002)** and the SpamAssassin implementation score a message by the odds form: log-score = log(prior odds) + Σ log P(word | spam)/P(word | ham), which is naive Bayes — conditional independence of words, violated in practice but rank-consistent. The filter's whole design is lab 01's base-rate lesson: with a prior of ~0.15 spam arriving, a handful of strong likelihood ratios decide, and weak words barely move the posterior.

## Detection with tiny base rates needs Bayes, and needs it honestly
At attack prevalence 0.01% (lab 01 SECURITY), even a strong test leaves P(real | alarm) ≈ 1%. The Bayesian fix is not "better threshold" but *context*: add features (geo-velocity impossible travel, token reuse) that multiply additional likelihood ratios — two independent features with LR = 20 each take posterior odds from 1:10 000 × 400 = 1:25, i.e. ~4%. Independence is the modeling assumption to document, because correlated features multiply evidence that was counted twice (COMMON_MISTAKES #2 in operational form).

## Adversaries can attack the prior itself
Baseline poisoning: an attacker who can influence the training window shifts the estimated prior (e.g. spam-class word rates, user behavior profiles), moving every future posterior. Countermeasures: robust/hierarchical priors (partial pooling limits how far one user's data can move the population prior), time-decay windows that exclude the incident period, and prior predictive checks that flag a distribution shift before it is used.

## Sequential updating is a feature — and a target
Bayesian sequential monitoring (posterior P(θ > θ* | data) crossing a decision threshold) shares the peeking problem of lab 07: continuous monitoring of a posterior probability will cross any threshold eventually. Use pre-specified decision thresholds with simulation-calibrated false-alarm rates, or SPRT/Bayes-factor boundaries whose error rates are provable under optional stopping.

## Dutch book as a security property
A credence set that violates the probability axioms admits a bet layout that guarantees loss regardless of outcome (de Finetti's Dutch book). In practice this is the "arbitrary risk score" problem: any scoring scheme combining threat likelihoods and impacts must behave like a coherent measure (monotone, additive over disjoint events), or adversaries can find input combinations that make your risk engine output near-zero for a real threat.

## What to review
- [ ] Prior source: measured, documented, and *not* already fit on the same data as the likelihood?
- [ ] Feature independence assumption: justified, or is evidence being double-counted?
- [ ] Is the decision threshold reached by monitoring calibrated for the look frequency?
- [ ] Can an adversary contaminate the window used to fit the prior?

## Worked: Bayesian poisoning of a word filter

An adversary who knows the filter scores in odds attacks the product directly. From the base case above (prior 1:10 000, LR 400, posterior 3.8%): each inserted white-noise word with P(w|spam)/P(w|ham) = 0.1 multiplies the evidence by 0.1.

1. Three poisoned words: LR 400 × 0.1³ = 0.4, posterior odds 4 × 10⁻⁵ → **0.004%** — the alarm is erased and no individual word looks suspicious.
2. Defenses that hold: cap each word's log-LR contribution (bounds one feature's leverage), score unique filtered tokens (repetition buys the attacker nothing), and alert on per-sender *score distribution* shift rather than per-message score.
3. General lesson: a Bayesian filter inherits the security of its independence assumption *and* of its prior estimates — both are attacker-writable inputs.

## Prior provenance is supply chain

Treat the prior like a dependency: versioned, reviewed, sourced from a window the adversary could not influence, shipped with the same signing as code. An unsigned prior moves every downstream posterior, and no convergence diagnostic will object — R̂ and ESS confirm the chain reached the wrong target *efficiently*, which is exactly how a poisoned prior survives review.
