# Flashcards — Random Variables

## Definition Cards

### Card 1
**Front**: Define a random variable precisely.
**Back**: A measurable function X: Ω → R on a probability space — a
labeling of outcomes by numbers; all randomness comes from P, none from
X itself.

### Card 2
**Front**: State the PMF axioms for a discrete variable.
**Back**: p(k) = P(X = k) >= 0 for each support value, and the whole
table sums to 1 over the support.

### Card 3
**Front**: State the CDF definition and its three structural properties.
**Back**: F(x) = P(X <= x); nondecreasing, right-continuous, limits 0
and 1 at −∞ and +∞ respectively.

### Card 4
**Front**: Relation between PMF and CDF for a discrete variable?
**Back**: F(x) = Σ_{k <= x} p(k), and jump sizes recover the pmf:
p(k) = F(k) − F(k−1).

### Card 5
**Front**: State LOTUS exactly.
**Back**: E[g(X)] = Σ_k g(k) p(k) — apply the function at the support
values FIRST, weight by the pmf second; it requires no independence or
transform machinery.

## Theorem Cards

### Card 6
**Front**: Linearity of expectation — hypothesis and claim?
**Back**: E[aX + bY] = a E[X] + b E[Y] with NO hypothesis linking X and
Y (dependence irrelevant); constants pass through, sums average
separately.

### Card 7
**Front**: Variance computational identity?
**Back**: Var(X) = E[X^2] − (E[X])^2, obtained by expanding the squared
deviation and applying linearity.

### Card 8
**Front**: Variance under affine maps, Var(aX + b)?
**Back**: a^2 Var(X); the shift contributes nothing, the scale
contributes squared.

### Card 9
**Front**: When does Var(X + Y) equal Var(X) + Var(Y)?
**Back**: Exactly under zero covariance; independence suffices but is
not necessary (the general formula adds 2 Cov(X, Y)).

### Card 10
**Front**: Definition of independence for two discrete variables?
**Back**: Joint pmf factorizes: p(x, y) = p(x) p(y) for every pair —
stronger than zero covariance.

## Judge-the-Number Cards

### Card 11
**Front**: Two-dice sum: E, E[X^2], Var?
**Back**: E = 7 exactly, E[X^2] = 329/6, Var = 35/6 — both variance
routes printed identical machine output.

### Card 12
**Front**: X on {1,2} with halves: E[X], E[1/X], 1/E[X] — inequality?
**Back**: 3/2, 3/4, 2/3 respectively; 3/4 > 2/3, the convexity exhibit.
