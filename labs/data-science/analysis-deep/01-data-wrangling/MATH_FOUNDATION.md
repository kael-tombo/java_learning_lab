# Data Wrangling - Math Foundation

## Sample mean and median

For observed values x_1..x_m: mean = (1/m) sum x_i. Median = middle sorted
value (odd m) or mean of the two middle values (even m).
Example: observed {2, 4, 8, 10} gives mean 24/4 = 6.0 and median
(4 + 8)/2 = 6.0.

## Unbiasedness of the observed mean under MCAR

If each cell is missing independently with probability q, the observed mean
is the average of a random subsample: E[observed mean] = mu, the true mean.
Under MAR or MNAR this equality fails, which is why the mechanism matters
before any fill.

## Variance shrinkage from mean imputation

Fill m - k observed cells plus k copies of the observed mean x-bar. The
imputed variance around x-bar is (1/n) sum_obs (x_i - x-bar)^2, i.e. the
observed sum of squares divided by the larger n instead of m. Roughly, the
variance is scaled by (n - k)/n: one fill in five cells shrinks variance to
about 80% of the observed value. Standard errors computed afterward are too
small unless adjusted.

## Quartiles, IQR, fences

With type-7 interpolation, Q1 = quantile(0.25), Q3 = quantile(0.75),
IQR = Q3 - Q1. Fences: L = Q1 - 1.5 x IQR, U = Q3 + 1.5 x IQR.
Example: Q1 = 13.0, Q3 = 14.75, IQR = 1.75, so
L = 13 - 2.625 = 10.375 and U = 14.75 + 2.625 = 17.375.

## z-scores

z_i = (x_i - x-bar) / s, with s the sample sd (divisor n - 1).
Example: x = 60, x-bar = 18.2, s = 14.72563901650602 gives
z = 41.8 / 14.7256 = 2.84, above the k = 2 screen. Note the circularity:
the outlier inflates s, shrinking its own z (masking).

## Forward-fill as a model

Forward-fill assumes x_t = x_{t-1} plus small noise (a random-walk prior).
Its error grows with gap length, so cap the maximum run of fills and leave
longer gaps missing rather than fabricating a plateau.
