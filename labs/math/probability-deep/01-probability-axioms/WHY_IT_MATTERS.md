# Why It Matters: Probability Axioms

## Every downstream result rests on these three lines
Non-negativity, normalization and countable additivity are the only assumptions behind:

- **Marginalization and the total probability theorem** — used constantly in lab 02 when a mixed discrete/continuous variable is split.
- **Conditional independence factorization** — the reason a Bayesian network (lab 08) with 30 variables can be evaluated locally instead of over 2³⁰ states.
- **The law of large numbers and CLT** (lab 05) — both are literally statements about infinite sums of probabilities, meaningless without countable additivity.
- **Estimators, likelihoods, hypothesis tests** (labs 06–07) — the likelihood L(θ) = P(data|θ) is a conditional probability whose normalization over data is what makes MLE and Bayes comparable.

Break the axioms (allow negative "probabilities", or sums that exceed 1) and every one of those results can produce a certainty greater than 1 or an estimator that does not converge.

## Concrete consequences of getting it wrong
- **Insurance and finance:** premium = expected loss = Σ pᵢ·lossᵢ. Double-counting overlapping risks (missing inclusion–exclusion) overstates or understates reserves.
- **Medicine:** a screening program justified by "99% accurate" instead of P(D|+) ≈ 16.7% (1% prevalence) treats thousands of healthy people — a documented pattern in mammography and PSA screening debates.
- **Machine learning:** naive Bayes spam filters, topic models and any calibrated classifier rely on the product rule; a normalizer computed off by 2× silently breaks threshold decisions.
- **Reliability:** "the 97 components are each 99.9% reliable, so the system is 99.9% reliable" is a direct violation — under independence the system is 0.999⁹⁷ ≈ 0.9075, about 90.8%.

## The discipline it teaches
Ask always: what is the sample space, what is the measure, and is the conditioning event of positive probability? Labs 02–08 all assume those questions were answered first.

## What breaks when an axiom is silently violated

- **Non-normalized weights.** A table summing to 0.98 inflates every conditional computed from it by ~2%, and the error compounds through nested conditionals.
- **Overlapping risks summed directly.** Reserves computed as Σpᵢ ignore P(A ∩ B); with positively correlated risks the error is large in exactly the scenarios being insured.
- **Zero treated as impossible.** Quality control and security both live in the 10⁻⁶ region; a "probability zero, so skip it" shortcut excuses the exact failures being guarded against.
- **Independence assumed, not tested.** 97 components at 99.9% reliability give 0.999⁹⁷ ≈ 0.9075 — 90.8%, not 99.9%. Every redundancy calculation is a factorization claim, and factorization is an axiom-level assumption.
- **Conditioning direction swapped.** Screening, fraud and spam all hinge on P(cause | signal); reporting P(signal | cause) instead is the single most expensive sentence-level error in applied probability.

## Where each axiom shows up in code review

| Axiom | What it guarantees in software | What breaks without it |
|---|---|---|
| P ≥ 0 | A "probability" report cannot be negative — validators and log-odds math stay real-valued | A negative weight in a resampling scheme silently corrupts every weighted estimate |
| P(Ω) = 1 | Normalization constants are checkable: a categorical distribution's weights must sum to 1 | Missing normalization means your sampler's acceptance rate is unmeasurable |
| Countable additivity | Probabilities of infinite unions (e.g. P(eventually ever)) equal the limit of finite sums | Monte Carlo estimators of rare-event probabilities stop converging; tail sums drift with the run length |

A practical audit question for any pipeline that emits probabilities: do the reported values pass these three checks on every record? They are cheap, and a failure always points at a modeling bug, not a statistical fluke.
