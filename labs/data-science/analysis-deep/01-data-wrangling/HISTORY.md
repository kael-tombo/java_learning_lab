# Data Wrangling - History

## Examining data before modelling: Tukey 1977

John Tukey's "Exploratory Data Analysis" (1977) made careful, skeptical
looking at raw data a discipline rather than a chore. Its stem-and-leaf
displays, five-number summaries, and box plots were tools for noticing dirt -
skew, gaps, strays - before any model was fit. Modern profiling (missing
counts, ranges, fence flags) is that program running on bigger files.

## The box plot and the 1.5 x IQR fence

Tukey's box plot draws the box from Q1 to Q3 and extends whiskers to the
most extreme points within 1.5 x IQR of the quartiles; points beyond are
plotted individually as candidates for attention. The 1.5 multiplier is a
practical convention from Tukey, not a theorem: roughly 99% of normal data
falls inside, so flags are rare under normality and informative otherwise.

## ETL came first, wrangling named it later

Extract-transform-load pipelines for warehouses date back decades before the
word "wrangling" became fashionable in the 2010s data-science boom. The
problems are identical (conform types, conform keys, survive bad rows); what
changed is who does it - analysts in code rather than warehouse engineers in
proprietary tools - and the insistence on scripted, reviewable steps.

## Missing-data theory: Rubin and Little

The MCAR / MAR / MNAR taxonomy comes from Donald Rubin (1976) and is the
backbone of Roderick Little and Rubin's "Statistical Analysis with Missing
Data" (first edition 1987). Their point stands: the validity of deletion or
imputation depends on the mechanism, and MNAR always needs extra assumptions.

## Anscombe 1973 as a cleaning moral

F. J. Anscombe's 1973 quartet showed identical summary statistics hiding
wildly different data, including an outlier-driven set. For wrangling, the
moral is direct: never accept a column on its mean alone - look at the
shape, because one 60.0 among the 14s rewrites the story.

## What this lineage teaches

Every generation rediscovers the same lesson: the file is guilty until
proven innocent. Tukey gave the plots, Rubin gave the missingness logic,
and ETL practice gave the pipeline shape this lab follows.
