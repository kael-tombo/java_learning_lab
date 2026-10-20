# Bayesian Statistics — Lab 08 of Probability Deep

Bayesian updating as exact arithmetic: conjugate posteriors computed
in rationals, priors whose fingerprints survive the data, and every
number pasted from a captured run rather than asserted.

## What this lab actually teaches

- THEORY.md: Bayes' theorem as the prior-triple bookkeeping,
  Beta-Binomial conjugacy stated exactly, posterior mean/mode closed
  forms, the posterior predictive versus the plug-in rate (9/14 vs
  7/10), sequential-equals-batch sufficiency, Normal-Normal
  conjugacy, and the MAP/mean/credible-interval distinctions.
- MATH_FOUNDATION.md: the central update fully exhibited —
  Beta(2, 2) + seven heads and three tails = Beta(9, 5), mean 9/14,
  mode 2/3, normalization B(9, 5) = 8!4!/13! = 1/6435 — plus the
  three-priors comparison (flat 1/5 vs Jeffreys 7/10).
- CODE_DEEP_DIVE.md: two executed Python programs — sequential
  updating against one batch update (machine-equal posteriors) and
  the three-priors divergence on different datasets, both in exact
  fractions — plus what the conjugate engine never does (no
  integration, no sampling).
- EXERCISES.md: five problems with worked solutions that quote the
  captured outputs (a fresh HHT dataset through the same engine,
  all-tails under a flat prior, and more).
- FLASHCARDS.md: ten front-back cards, every number carried from the
  verified runs.

## What to do with it

Work THEORY then MATH_FOUNDATION with a pencil, then run the deep
dive yourself: a two-parameter counter is the entire Bayesian
machinery for the coin case, and seeing 7/10 versus 9/14 side by side
makes the prior's contribution concrete in one arithmetic step.

## Prerequisites

Law of large numbers (Lab 05) and estimation theory (Lab 06); Lab 01's
conditional-probability axioms for the theorem statement itself.
