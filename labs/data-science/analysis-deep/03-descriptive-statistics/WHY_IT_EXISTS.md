# Descriptive Statistics - Why It Exists

## Compression with a receipt

Raw columns cannot be argued about; summaries can. Mean, spread, quartiles,
and r compress n numbers into a handful a human can hold in mind - and each
comes with diagnostics (median vs mean, IQR vs sd) that say whether the
compression was fair. Statistics exists to make data discussable without
hiding the ways discussion can go wrong.

## The n vs n - 1 problem is unavoidable

Any sample-based science must generalize beyond the numbers in hand, and
the fitted mean always flatters the fit. Bessel's correction exists because
the bias is systematic, provable, and removable by dividing by n - 1. Labs
that report both normalizations (30.82 and 35.95 here) teach the habit of
labelling which question - describe or estimate - each number answers.

## Shape numbers prevent normal-by-default

Assuming normality is the silent default of t-tests, intervals, and control
limits. Skew (+0.58) and kurtosis (-0.62) exist to challenge that default
cheaply, before methods that depend on it are applied to data that violates
it.

## Association needs a unit-free dial

Covariance answers in squared mixed units nobody can compare across studies;
r maps every pair onto [-1, 1]. The dial exists so "strongly related" means
the same thing for heights and for stock prices - with the causation warning
attached, since Galton's own discoveries came bundled with that confusion.

## The alternative is vibes

"The data looks fine" is not a summary; neither is a single mean quoted to
three decimals. Descriptive statistics exists to replace vibes with named,
reproducible compressions plus the diagnostics (median vs mean, IQR vs sd)
that audit each compression. Without the audit half, summaries are marketing.

## Small-n honesty

On n = 7 every choice shows: divisor, interpolation rule, moment fragility.
Learning the machinery where each wire is visible is what makes later
large-n practice trustworthy - the formulas do not change, only the hiding
places for error grow.
