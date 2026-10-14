# Feature Engineering - References

## Christopher Bishop, Pattern Recognition and Machine Learning

Linear basis-function models (Chapter 3): polynomial and interaction
expansions as engineered features, with the overfitting cost of each added
term made exact. The theory behind the area-x-rooms product.

## Hastie, Tibshirani, and Friedman, The Elements of Statistical Learning

Regularization chapters show why scaling precedes penalized fits (penalties
assume comparable units) and how folds must enclose all supervised
preprocessing - the canonical anti-leakage reference.

## Andrew Gelman et al., Regression and Other Stories

Rescaling predictors (including dividing by 2 sd for comparability with
binary inputs) for interpretable coefficients. The practical companion to
the demo's three scaling lenses.

## Hadley Wickham and Garrett Grolemund, R for Data Science (factors)

Ordered vs unordered categoricals handled exactly: factor levels, ordering,
and collapsing rare levels. Mirrors the one-hot/ordinal decision here with
worked data examples.

## John Tukey, Exploratory Data Analysis (1977)

The re-expression ladder: logs and roots for skew before modelling. Read
the transform chapters before reaching for heavier machinery on tailed
predictors.

## George Box and David Cox, "An Analysis of Transformations" (1964)

The power-transform paper generalizing log into fitted lambda. Cited
wherever Box-Cox is mentioned as the principled extension of the lab's log.

## OpenJDK documentation: Math, Arrays, collections

Specs for `Math.log`, `Arrays.toString`, and `List`/`Map` indexing behind
the snippets. Deterministic outputs rest on these contracts.

## How to read them for this lab

Start with Tukey for transforms and Wickham for categoricals, then Bishop
for why expansions overfit and HTF for why penalties need scaling and folds
must enclose preprocessing. Keep Gelman nearby when coefficients must read
as decisions, Box-Cox when log feels arbitrary, and the OpenJDK docs
whenever a hash, log, or sort edge case is load-bearing.
