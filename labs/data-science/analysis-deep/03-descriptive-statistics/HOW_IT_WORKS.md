# Descriptive Statistics - How It Works

## Center in three passes

Mean needs one pass (sum, divide by 7: 74/7 = 10.571428571428571). Median
needs a sorted copy ([3,7,7,9,12,15,21]) and picks index 3: 9.0. Mode needs
a frequency map and keeps the argmax: 7.0 with count 2. Mean and median
disagree by 1.57 - the first computed evidence of right skew.

## Spread in two normalizations

Accumulate ss = sum (x - mean)^2 = 215.71428571428572 once, then report both
normalizations: /7 for description (30.816326530612248), /6 for estimation
(35.952380952380956). Square roots give the two sds. Computing ss in one
pass from a precomputed mean is exact enough here; the two-pass form (mean
first, then deviations) is the numerically safer habit for large data.

## Shape from moments

Center the data at the mean, accumulate the 2nd/3rd/4th powers, divide by n,
form the ratios: skew = m_3/s^3 = 0.5802988304934447, excess kurtosis =
m_4/m_2^2 - 3 = -0.6180158764966452. Positive skew with mean > median is the
consistent pair; the negative excess kurtosis says tails are mild.

## Association from cross-sums

For xs 1..5 and ys {2,4,5,8,10}: center both (mx 3.0, my 5.8), accumulate
s_xy = 20.0, s_xx = 10.0, s_yy = 40.8. Covariance 20/4 = 5.0; r =
20/sqrt(408) = 0.9901475429766744. One shared loop computes all three sums,
so the program cannot report a covariance inconsistent with its r.

## Reporting order

Center, then spread (both normalizations labelled), then quartiles, then
shape, then association. Each layer checks the last: median vs mean flags
skew, IQR vs sd flags tails, scatter would check r.

## What each layer rules out

Center rules out "nothing to see" (mean/median gap says skew). Spread rules
out false precision (two divisors, labelled). Quartiles rule out tail
surprises hiding in the sd. Shape numbers rule out normal-by-default. The r
rules out independence - and the scatter rule (plot it) rules out mistaking
0.99 for understanding.
