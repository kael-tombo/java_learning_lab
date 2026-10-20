# Distributions — Math Foundation

Figures come from executed Python (snippets and transcripts in
CODE_DEEP_DIVE.md): fractions where the family is discrete, full-
precision decimals from math.exp / math.erf where it is not.

## 1. Uniform[0, 2] — Density, CDF, Round Trip
Density 1/2 on the interval. Observed: F(−0.5) = 0, F(1) = 1/2, F(2) = 1,
F(3) = 1, and the total mass ∫_0^2 (1/2) dx = 1 exactly. Derivative
back: d/dx (x/2) = 1/2 = f on the interval — the straight-ramp CDF
round-trips through differentiation without residue.

## 2. Exponential(1) — Survival and Memorylessness, in Decimals
Observed with full precision:
P(X > 1) = 0.36787944117144233 (that is e^{−1}) and F(1) =
0.6321205588285577. The memoryless identity was executed as a division:
P(X > 1.5) / P(X > 1) = 0.6065306597126334, and the run compared it to
e^{−0.5} = 0.6065306597126334 — digit-identical, confirming
P(X > s+t | X > s) on the pair s = 1, t = 1/2.

## 3. Binomial(4, 1/2) — The Exact Objects
Observed pmf: [1/16, 1/4, 3/8, 1/4, 1/16] over k = 0..4, summing to 1.
Moments: E = 2 = np and Var = 1 = np(1−p), each extracted from the
table and matching the parameter formulas at n = 4, p = 1/2. The
binomial coefficients {1, 4, 6, 4, 1} over 16 make the symmetry of the
table visible before any formula is cited.

## 4. Binomial(10, 1/3) — Asymmetric Case
Observed exactly: total mass 1, E = 10/3, Var = 20/9, and
P(X <= 1) = 2048/19683. Verify the tail by its parts: P(0) = (2/3)^10
and P(1) = 10(1/3)(2/3)^9 sum to (2/3)^9 (2/3 + 10/3) = 4(2/3)^9 =
2048/19683 — the run's fraction reproduces the algebra without a
single hand-cast decimal.

## 5. Poisson(2) — Decimal Truth and Truncation Error
Observed mass list (k = 0..11):
0.13533528, 0.27067057, 0.27067057, 0.18044704, 0.09022352,
0.03608941, 0.0120298, 0.00343709, 0.00085927, 0.00019095, 3.819e-05,
6.94e-06. Their sum is 0.9999986353848405: the missing 1.4e−06 is
truncation, and the exact P(X = 0) = e^{−2} = 0.1353352832366127 pins
the leading entry. Peak at k = 1, 2 (tie at rate 2) is visible in the
table itself.

## 6. Standard Normal — Φ Through erf
Observed decimals: Φ(0) = 0.5 (symmetry made concrete), Φ(0.5) =
0.691462461274013, Φ(1) = 0.8413447460685428, Φ(2) =
0.9772498680518209. Derived interval reads: P(−1 < Z < 1) =
0.6826894921370856 (the famous 68% rule exhausted to 16 digits) and
P(Z > 2) = 0.022750131948179098, so the two-sided exceedance beyond ±2
is about 4.55% — the engine behind the folklore-but-verified 95%.

## 7. Parameter Read-Off Practice
Given only the tables above: Bin(4, 1/2) is recovered from the shape
symmetric about 2; Poisson(2) declares its λ in the mean; Exponential(1)
declares its λ in the survival slope. The whole modeling skill of this
lab is moving between printed numbers and parameter values without
re-deriving the family from scratch.
