# Math Foundation - Causal Inference

## 1. Average treatment effect

ATE = E[Y(1) - Y(0)] over the population. An RCT estimates it by
E[Y | treated] - E[Y | control], valid because randomization makes
treatment independent of both potential outcomes.

## 2. Confounding bias decomposition

The naive contrast decomposes exactly:

  E[Y|T=1] - E[Y|T=0] = ATE + selection bias

Selection bias is the difference in baseline outcomes Y(0) between the
groups that chose (or were chosen for) treatment vs control. In the
Confound demo the naive gap is -0.3267 while the adjusted gap is
-0.0067: nearly the whole naive number is selection bias.

## 3. Stratified adjustment identity

With strata proportions w_k and within-stratum gaps g_k, the adjusted
estimate is sum_k w_k * g_k. This equals the population ATE if
treatment is unconfounded within strata (the no-unmeasured-confounding
assumption again). Weighting by stratum size is what stops a small odd
stratum from dominating.

## 4. Difference-in-differences algebra

effect = (T_post - T_pre) - (C_post - C_pre). Rearranged, it is the
change in the treated-control gap. Under parallel trends the control
change equals the treated group's counterfactual change, leaving the
causal effect. Any group-specific shock breaks the equality - the math
shows exactly where the assumption enters.

## 5. Instrumental-variables ratio (concept)

With a valid binary instrument, the Wald form is
effect = (outcome gap by Z) / (treatment gap by Z): the outcome shift
scaled by how much Z moved treatment. Weak relevance (tiny denominator)
blows up variance; violated exclusion biases everything. Both failure
modes are visible directly in the ratio.

## 6. Bayes-free warning for matching

Matching balances measured covariates only. The residual bias from an
unmeasured confounder U is proportional to U's links with treatment and
outcome - sensitivity analysis varies those links to bound the damage,
which EXERCISES.md practices qualitatively.
