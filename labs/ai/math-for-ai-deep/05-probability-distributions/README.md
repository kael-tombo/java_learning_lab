# 05-probability-distributions - Probability Distributions
## Overview
Gaussian pdf peaks at 1/sqrt(2 pi) for N(0,1); ~68% mass within 1 std, ~95% within 2. Bayes rule P(D|+) = sens*prior / P(+) corrects for base rates.
## Key formulas
- N(x) = e^(-(x-mu)^2/2s^2)/(s sqrt(2 pi)).
- Posterior = sens*prior / (sens*prior + fpr*(1-prior)).
## What the snippets show
- Mt05A: pdf values plus 0.6827/0.9545 constants.
- Mt05B: full numerator/denominator/posterior trace.
## Try it
Raise prior to 0.2 and confirm the posterior jumps above 0.8.
## Formula reference
- Gaussian N(x) = e^(-(x-mu)^2/2s^2)/(s sqrt(2 pi)); 68/95/99.7 rule.
- Bayes: P(D|+) = sens*prior/(sens*prior + fpr*(1-prior)).
- Expectation linear; variance of sum needs covariance terms.
## Worked example
- 1/sqrt(2 pi) = 0.3989; e^-0.5/sqrt(2 pi) = 0.2420.
- Numerator 0.99*0.01 = 0.0099; denominator + 0.05*0.99 = 0.0594.
- Posterior 0.1667: 5 of 6 positives are false despite 99% sensitivity.
## Pitfalls
- Base-rate neglect: strong tests still mislead on rare conditions.
- Gaussian assumption on skewed data; check or transform.
- Precision vs recall tradeoff lives in the threshold, not the test.
## Connections
- Beta-Binomial lab updates this prior with counts.
- Softmax outputs are categorical distributions over classes.
## Exercises
1. Raise prior to 0.2; recompute posterior.
2. Evaluate N(1) for mu = 1, sig = 2.
3. Flip sens/FPR roles; explain the result.
