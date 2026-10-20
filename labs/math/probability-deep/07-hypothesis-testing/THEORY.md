# Hypothesis Testing — Theory

## 1. The Architecture of a Test
A statistical test pairs a null hypothesis H0 with an alternative H1,
computes a test statistic T from the data, and pre-declares a rejection
region R: if T lands in R, reject H0. Everything quantitative follows
from the two conditional error probabilities the pair (H0, R) creates.

## 2. The Two Errors — Exact Definitions
- Type I error: rejecting H0 when H0 is true. The size (significance
  level) of a test is alpha = P(T ∈ R | H0) — a probability computed
  under H0 only.
- Type II error: failing to reject H0 when H1 is true. Its probability
  is beta = P(T ∉ R | H1); power is 1 − beta, a function of the true
  parameter, not a single number.
The asymmetry is constitutional: alpha is engineered by DESIGN once
and for all; beta depends on the unknown truth and the sample size.

## 3. Exact Binomial Tests — A Complete Tiny Example
Data: n = 10 coin flips; H0: p = 1/2. Statistic T = number of heads.
The two-sided rejection region {k <= 1} ∪ {k >= 9} has size
alpha = [C(10,0) + C(10,1) + C(10,9) + C(10,10)] / 2^10 = 22/1024 =
11/512 ≈ 0.0215 (executed). Shrink or grow the region and the arithmetic
moves: the one-sided region {k >= 8} has size 56/1024 = 7/128 ≈ 0.0547,
which is why "at least one head-tail extreme on either side" is cheaper
to guarantee than "this side only". Every figure is a coefficient sum
over 2^10, machine-exact.

## 4. Power and Its Shape
Power(k region | true p) = P(T ∈ R | p). For the region above at
p = 3/10 the run measured beta = 4252739841/5000000000 = 0.8505479682,
power ≈ 0.1494520318 — at 10 flips the test discovers a 30% coin only
15% of the time. Symmetry: the beta at p = 7/10 equals that at 3/10
(executed equality), the reflection about p = 1/2. Power curves rise
toward the rejected tails — a table, not a slogan.

## 5. The p-Value, Stated Correctly
The p-value is the probability, computed UNDER H0, of a result at
least as extreme as the one observed (extremeness measured by the test
statistic's ordering, one- or two-sided by design). It is NOT the
probability that H0 is true, and objections to interpreting it as such
require a Bayesian prior for H0 (Lab 08's machinery). Small p signals
surprise under H0, not guilt.

## 6. Permutation Tests — Exactness by Construction
Under H0 of exchangeability (the group labels carry no information),
every reassignment of the observed values across the two groups is
equally likely. The exact permutation p-value is the fraction of the
(enumerable) relabelings whose statistic meets or beats the observed
one — no distribution family assumed at all. For 3-vs-3 samples the
space has exactly C(6,3) = 20 labelings, so any p-value is a multiple
of 1/20; executed: one-sided 1/20, two-sided 1/10 — the run printed
both counts.

## 7. Testing Discipline
alpha is fixed BEFORE data arrive; regions are two-sided unless a
one-sided alternative was pre-registered; p-values are compared to
alpha, never to thresholds like 0.05 as if legislated; and reporting
an exact permutation p-value alongside a parametric one is the sanity
check that costs nothing on tiny samples.
