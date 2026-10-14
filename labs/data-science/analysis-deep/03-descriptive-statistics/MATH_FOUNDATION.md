# Descriptive Statistics - Math Foundation

## Bessel's correction, derived

With true mean mu unknown, deviations about x-bar satisfy
sum (x_i - x-bar) = 0: one linear constraint, n - 1 free residuals.
E[sum (x_i - x-bar)^2] = (n-1) sigma^2, so dividing by n - 1 unbiasedly
estimates sigma^2, while dividing by n gives (n-1)/n sigma^2 - low by a
factor 6/7 here (30.82 vs 35.95).

## Variance of the mean

Var(x-bar) = sigma^2 / n: averaging seven values shrinks noise by sqrt(7).
With sample sd 6.00, the standard error of the mean is 6.00/sqrt(7) = 2.27.
This is why large n pins the center even when spread stays wide.

## Moment skew formula

m_k = (1/n) sum (x_i - x-bar)^k; skew = m_3 / m_2^{3/2}. For the lab data
m_3 = 99.36 (dominated by the 21's +1134.5 contribution against the left
tail's -528.78), m_2 = 30.82, giving 99.36/171.04 = 0.5802988304934447.
The single 21 contributes more than the entire left tail: moments magnify
strays by cubing.

## Excess kurtosis formula

kurt_excess = m_4 / m_2^2 - 3 = -0.6180158764966452 here. Subtracting 3
centers the normal at zero. Negative values mean fewer far-tail surprises
than normal with the same variance - consistent with max 21 sitting only
~1.9 population-sd above the mean.

## Pearson r bounds (Cauchy-Schwarz)

|s_xy| <= sqrt(s_xx s_yy) gives |r| <= 1, equality for exact linear
dependence. Lab: 20.0 <= sqrt(10 x 40.8) = 20.199, ratio 0.9901475429766744.
Covariance 5.0 = 20.0/6 carries mixed units; r strips them.

## Quantile type-7 positions

h = 1 + (n-1)p on sorted data (1-based), blending neighbors fractionally.
n = 7: Q1 h = 2.5 -> (7+7)/2 = 7.0; Q3 h = 5.5 -> (12+15)/2 = 13.5;
IQR = 6.5. Linear blending makes quartiles continuous in the data.
