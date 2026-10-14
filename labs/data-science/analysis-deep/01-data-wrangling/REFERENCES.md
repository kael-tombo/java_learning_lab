# Data Wrangling - References

## John Tukey, Exploratory Data Analysis (1977)

The founding text for skeptical data examination. Chapters on stem-and-leaf,
five-number summaries, and box plots are directly the profiling and fence
logic used in this lab.

## R. J. A. Little and D. B. Rubin, Statistical Analysis with Missing Data

The reference for MCAR, MAR, and MNAR and for why the mechanism governs the
remedy. Read the taxonomy chapters before choosing deletion or imputation.

## Hadley Wickham, R for Data Science (tidy data chapters)

The clearest exposition of tidy rectangular data: one variable per column,
one observation per row. The dedup-key and coercion discipline here is the
Java-only version of that tidying.

## Andrew Gelman and Jennifer Hill, Data Analysis Using Regression and
Multilevel/Hierarchical Models

Shows how missingness and grouping choices propagate into regression
conclusions - the downstream cost of careless wrangling, with worked
examples.

## William Press et al., Numerical Recipes

Sorting, selection, and interpolation routines behind quantile computation.
Useful when the O(n log n) sort in the snippets needs a faster or
streaming replacement.

## OpenJDK documentation: java.util, Double, Arrays

Authoritative specs for `Double.NaN` semantics, `Arrays.sort` behavior on
doubles, `LinkedHashMap` ordering guarantees, and `Double.parseDouble`
grammar. Consult these before assuming any edge-case behavior.

## F. J. Anscombe, "Graphs in Statistical Analysis" (1973)

The quartet paper. Short, readable, and the best antidote to trusting a
cleaned column's mean without inspecting its shape.

## Christopher Bishop, Pattern Recognition and Machine Learning

Chapter 1 discusses missing data and the role of modelling assumptions when
values are absent - the probabilistic companion to the mechanism taxonomy
used in this lab.

## Hastie, Tibshirani, and Friedman, The Elements of Statistical Learning

Covers how data preparation choices surface in model assessment: a cleaning
shortcut that leaks or distorts the training distribution reappears as
optimistic error estimates, which their validation chapters teach you to
distrust.
