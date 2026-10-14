# Feature Engineering - History

## Dummy variables: regression's original encoding

Regressions have used 0/1 indicator columns for categories since the early
20th century - one-hot encoding under its birth name. The cautions are as
old: the dummy-variable trap (perfect collinearity with an intercept) and
proliferating sparse columns for high-cardinality fields. Modern one-hot is
that practice renamed, with regularization softening the trap.

## Galton, regression, and shrinkage (1886)

Francis Galton's 1886 regression work showed extreme measurements pull back
toward the mean - the intuition behind smoothing target encodings toward the
global mean today. A rare level's raw mean outcome is an extreme measurement;
shrinking it toward the overall mean before trusting it is Galton's lesson
applied to categories.

## Bayes (1763) behind smoothed means

Thomas Bayes' posthumous 1763 essay founded inverse probability: combine a
prior with observations to get a posterior. Smoothed target encoding is that
recipe exactly - global mean as prior, level observations as data, encoded
value as posterior. Small levels stay near the prior; large levels earn
their own rate.

## Tukey and re-expression (1977)

John Tukey's EDA devoted a ladder of re-expressions (log, root, reciprocal)
to straightening relationships and symmetrizing skew. The lab's log(area)
step (3.91/4.38/4.79) is one rung of Tukey's ladder, applied before
modelling rather than after failure.

## Box-Cox (1964)

George Box and David Cox's 1964 paper parameterized the power-transform
choice (lambda fitted by likelihood), generalizing Tukey's ladder into one
estimable transform. Log is the lambda = 0 member; the paper turned
transform-picking from craft into estimation.

## Feature hashing (2009)

Kilian Weinberger and colleagues' 2009 "Feature Hashing for Large Scale
Multitask Learning" hashed open vocabularies into fixed-width vectors,
trading exact identity for bounded memory. The trick that lets text-scale
categoricals into linear models without a vocabulary at all.

## Pearson and Spearman in the background

Correlation screens (Pearson 1890s, Spearman 1904) decide which engineered
features survive: near-duplicate products and encodings show up as |r| near
1 long before they destabilize a fit. Engineer freely, correlate ruthlessly.
