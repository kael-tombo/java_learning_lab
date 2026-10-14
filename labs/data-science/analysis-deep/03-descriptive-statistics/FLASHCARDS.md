# Descriptive Statistics - Flashcards

## Q1. Mean, median, mode of the lab data?

A: Mean 10.571428571428571, median 9.0, mode 7.0 (count 2). Mean > median
flags right skew.

## Q2. State Bessel's correction.

A: Sample variance divides by n - 1, not n: residuals about the fitted mean
have n - 1 free values, and E[ss] = (n-1) sigma^2.

## Q3. Both variances of the lab data?

A: Population 30.816326530612248 (sd 5.551245493635842); sample
35.952380952380956 (sd 5.99603043290984). Same ss 215.71428571428572.

## Q4. When do you divide by n vs n - 1?

A: n to describe the finite data in hand; n - 1 to estimate the source
population's variance from a sample.

## Q5. Moment skew formula and lab value?

A: m_3 / s^3 = 0.5802988304934447; positive sign means a right tail, here
driven largely by the 21.

## Q6. Excess kurtosis formula and lab value?

A: m_4 / m_2^2 - 3 = -0.6180158764966452; negative means milder tails than
normal. Subtract 3 centers normal at zero.

## Q7. Quartiles and IQR of the lab data?

A: Q1 7.0, median 9.0, Q3 13.5, IQR 6.5 (type-7 interpolation on n = 7).

## Q8. Pearson r formula and lab value?

A: s_xy / sqrt(s_xx s_yy) = 20/sqrt(408) = 0.9901475429766744, with sample
covariance 5.0. Bounded in [-1, 1], unit-free.

## Q9. Why report sd with IQR on skewed data?

A: The sd follows the tail (6.00 here) while IQR (6.5, resistant) describes
the bulk; together they reveal what either alone hides.

## Q10. What breaks correlation on constant input?

A: Zero spread makes r = 0/0 (NaN). Branch on zero s_xx/s_yy before
dividing and report "undefined", not a number.

## Q11. Pearson vs Spearman in one line each?

A: Pearson: linear co-movement of values. Spearman: monotone co-movement of
ranks, robust to outliers and curvature.

## Q12. Standard error of the lab mean?

A: se = 5.99603043290984 / sqrt(7) = 2.27: averaging seven values shrinks
noise by sqrt(7).

## Q13. Why two-pass variance computation?

A: Mean first, then deviations: avoids catastrophic cancellation of the
one-pass sum(x^2) - n*mean^2 form on large-mean data.

## Q14. What did Anscombe 1973 prove about summaries?

A: Identical means, variances, and correlations can describe different
shapes - so every moment here ships with quartile inspection.
