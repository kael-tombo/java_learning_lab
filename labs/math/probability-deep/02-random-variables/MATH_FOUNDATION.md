# Random Variables — Math Foundation

Computed in exact rational arithmetic with Python `fractions` (CODE_DEEP_DIVE.md
holds the run transcripts); nothing below is hand-derived.

## 1. Two Dice, Sum Variable — The Full Table
X = sum of two fair dice. Exact PMF entries observed:
P(X = 2) = 1/36, P(X = 7) = 6/36 = 1/6, P(X = 12) = 1/36, and the whole
table sums to 1 machine-verified. The distribution is the pushforward
count of the 36-sample fiber structure, barely more than counting.

## 2. Expectation and Variance, Both Routes
Observed: E[X] = 7 exactly, E[X^2] = 329/6. Variance two ways:
E[X^2] − (E[X])^2 = 329/6 − 49 = 35/6, and the definition route
Σ (k − 7)^2 p(k) gives the identical 35/6 (the run prints
`equal: True`). The two formulas agree on the same exhibit rather than
being asserted in parallel.

## 3. CDF of a Three-Point PMF
Take P(X = 0) = 1/4, P(X = 1) = 1/2, P(X = 2) = 1/4. Observed jumps:
F(x) = 0 below 0; F(0) = 1/4; F(1) = 3/4; F(x) = 1 for x >= 2. Jump
sizes read back the PMF: F(1) − F(0) = 1/2 = p(1), exactly the
inverse-sum relation of THEORY.md.

## 4. Moments of the Three-Point Variable
Observed: E = 1 and Var = 1/2 (via E[X^2] = 3/2 minus E^2 = 1). A
symmetric PMF about its mean is no accident here — p(0) = p(2) pins the
average at 1, while the spread is governed by the ±1 displacements each
carrying mass 1/2.

## 5. LOTUS Counterexample, Live
X lives on {1, 2} with probabilities 1/2, 1/2. Observed:
E[X] = 3/2, E[1/X] = 3/4, 1/E[X] = 2/3 — unequal, prints `unequal: True`.
The inequality E[1/X] > 1/E[X] here is the discrete face of convexity of
t ↦ 1/t: averaging reciprocals weights small denominators upward.

## 6. Single Die Moments
For one fair die: E = 7/2, E[X^2] = 91/6, Var = 91/6 − 49/4 = 35/12
(exact, via the expanded identity). These underpin the two-dice case:
differences of means add (7 = 7/2 + 7/2), variances add for independent
variables (35/6 = 35/12 + 35/12) — a preview of Lab 04's rule, executed
on the two relationships.

## 7. Product Moment of Two Dice
With X, Y the two faces: E[XY] = 91/6 (the squared-sum trick under
independence), E[X] E[Y] = 49/4, so Cov = 91/6 − 49/4 = 35/12 = Var of
one die. Equality Cov(X, Y) = Var(X) holds for i.i.d. pairs — checked
numerically here, generalized in Lab 04.

## 8. Accumulation on the Sum Variable
Observed: P(sum odd) = 1/2, P(X = 7 | odd sum) = (6/36)/(18/36) = 1/3,
and P(X <= 7) = 21/36 = 7/12. Jump bookkeeping cross-checks the latter:
F(3) = (1 + 2)/36 = 3/36, then steps of 3/36, 4/36, 5/36, 6/36 at
x = 4, 5, 6, 7 accumulate to 21/36. The conditional rescale merely
divides fiber counts inside the odd-sum subpopulation.
