# Descriptive Statistics - Theory

## 1. Measures of center

- **Mean:** x-bar = (1/n) sum x_i. Uses every value; follows skew and
  outliers (10.57 here vs median 9.0).
- **Median:** middle sorted value (9.0 for odd n = 7). Resists up to half
  the data being contaminated.
- **Mode:** most frequent value (7.0, appearing twice). The only center
  defined for nominal categories.
- Choice rule: symmetric data, report mean and sd; skewed data, report
  median and IQR (with the mean as a secondary number, never hidden).

## 2. Variance: n versus n - 1

- **Population variance:** sigma^2 = (1/n) sum (x_i - mu)^2. Exact
  description of a finite, fully observed set: 30.816326530612248 here.
- **Sample variance:** s^2 = (1/(n-1)) sum (x_i - x-bar)^2 = 35.952380952380956.
  Dividing by n - 1 (Bessel's correction) compensates because deviations
  about the fitted x-bar are systematically smaller than about the true mu.
- **Standard deviation:** square root of variance, back in data units:
  population 5.551245493635842, sample 5.99603043290984.
- Rule: describing the data in hand, n; estimating the source population
  from a sample, n - 1. Mixing them up shifts every downstream interval.

## 3. Shape: skew and kurtosis

- **Moment skew:** m_3 / s^3 where m_3 is the third central moment. Sign
  gives tail direction (0.58: right tail, matching mean > median).
- **Excess kurtosis:** m_4 / m_2^2 - 3, zero for the normal distribution.
  Here -0.62: flatter tails than normal (no far strays besides the mild 21).
- Both are moment ratios, so outliers dominate them - read them as shape
  hints, then look at the quartiles.

## 4. Quartiles and IQR

Q1 = 7.0, median = 9.0, Q3 = 13.5, IQR = 6.5 (type-7 interpolation). The
five-number summary (min 3, Q1, median, Q3, max 21) describes skew and spread
without any normality assumption, which is why it accompanies - and for
skewed data replaces - the mean/sd pair.

## 5. Covariance and Pearson's r

Sample covariance = s_xy / (n - 1); Pearson r = s_xy / sqrt(s_xx s_yy),
bounded in [-1, 1] and unit-free. The lab pair gives cov 5.0 and
r 0.9901475429766744: strong linear association, still not causation.
