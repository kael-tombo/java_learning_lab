# Descriptive Statistics - References

## John Tukey, Exploratory Data Analysis (1977)

Five-number summaries, box plots, resistant description. The authority for
reporting quartiles first and moments second on skewed data.

## William Press et al., Numerical Recipes

Accurate summation, sorting/selection for quantiles, and the numerical
caution behind two-pass variance computation. Read before implementing
moments on large or large-mean data.

## Christopher Bishop, Pattern Recognition and Machine Learning

Chapter 1 treats sample mean, variance, and covariance as estimators with
bias properties - the probabilistic home of the n vs n - 1 distinction and
of covariance as an unnormalized association.

## Hastie, Tibshirani, and Friedman, The Elements of Statistical Learning

Correlation-based screening, linear association, and where naive moment
summaries break down on real data. Frames the lab's r computation inside
model-building practice.

## Andrew Gelman and Jennifer Hill, Data Analysis Using Regression and
Multilevel/Hierarchical Models

Shows means, sds, and correlations doing real work inside regression
displays - and how skewed predictors distort them, motivating the
median/IQR habit.

## F. J. Anscombe, "Graphs in Statistical Analysis" (1973)

The quartet paper: identical summaries, different shapes. Cited wherever
this lab warns that 0.99 or 10.57 alone proves nothing about form.

## OpenJDK documentation: Arrays, Math, Map

Specs for `Arrays.sort`, `Math.sqrt`, and map iteration used in the
snippets. The ground truth for edge behavior (NaN ordering, clone
semantics) assumed throughout.

## How to read them for this lab

Work Bishop's estimator-bias passages with pen and paper on the seven
values; follow Press when your variance loop meets large means; keep Tukey
open to remember quartiles come first on skew; cite Anscombe whenever anyone
proposes acting on r = 0.99 without the scatter.
