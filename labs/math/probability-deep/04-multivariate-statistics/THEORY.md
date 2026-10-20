# Multivariate Statistics — Theory

## 1. Joint Distributions Take Over
Several random variables on one probability space are described by
their JOINT distribution. For discrete pairs: p(x, y) = P(X = x,
Y = y), nonnegative, summing to 1 over the grid. Single-variable
theory never dies; it reappears as a shadow:

- Marginal: p_X(x) = Σ_y p(x, y) — collapse the other axis.
- Conditional: p(y | X = x) = p(x, y) / p_X(x) when p_X(x) > 0 — a
  rescaled row of the table (continuous analogue: divide by the
  marginal density, not a table mass).

## 2. Independence — The Product Condition
Variables X, Y are independent iff p(x, y) = p_X(x) p_Y(y) for every
pair (x, y). One violated cell breaks the whole thing; independence is
a property of the table, not of one summary number. This distinction
becomes concrete with the executed counterexample below.

## 3. Covariance — Definition and Bilinearity
Definition: Cov(X, Y) = E[(X − E[X])(Y − E[Y])] = E[XY] − E[X] E[Y].
Sign language: positive covariance says the variables rise together,
negative says one rises while the other sinks, zero says the bilinear
test finds nothing. The computational identity holds by expanding the
product of deviations and applying linearity to each factor.

Useful exact properties:
- Bilinearity: Cov(aX + b, cY + d) = ac Cov(X, Y) — shifts die, scales
  multiply.
- Cov(X, X) = Var(X).
- The variance law of sums, general form:
  Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X, Y).
- Extended: Var(Σ a_i X_i) = Σ_i Σ_j a_i a_j Cov(X_i, X_j).

## 4. Correlation — Covariance Made Scale-Free
ρ(X, Y) = Cov(X, Y) / (σ_X σ_Y), defined when both variances are
positive. Exact statement: −1 <= ρ <= 1, with the endpoints attained
exactly when Y is an affine function of X (a.s.). Correlation is
covariance divided by the natural scales, so it commutes with
rescaling: multiplying either variable by a positive constant leaves
ρ unchanged (flipping sign on a negative constant).

## 5. The Covariance Matrix
For a vector (X1, ..., Xn) the covariance matrix Σ has entries
Cov(X_i, X_j): variances on the diagonal, symmetrical elsewhere. Exact
statement: Σ is positive semidefinite — for any real vector a, the
linear combination a·X has variance a' Σ a >= 0. This eigenvector
geometry (principal directions) is the object that later statistics
(PCA-style rotations) diagonalize.

## 6. Zero Covariance Is Not Independence — Exact Counterexample Class
Covariance sees only bilinear (second-moment) alignment. Let X be
uniform on {−1, 0, 1} and Y = X^2. Then E[X] = 0 and E[XY] =
E[X^3] = 0, so Cov = 0, while the variables are decisively dependent —
knowing X pins Y. The full execution of this example (joint masses 1/3
vs the independence product 2/9) lives in MATH_FOUNDATION.md; the
lesson: a zero covariance entry certifies nothing beyond second
moments.

## 7. Why Multivariate Structure Matters Downstream
Portfolio-style reasoning, regression coefficients, and Gaussians all
run on covariance bookkeeping; every one of those tools inherits the
bilinearity and semidefiniteness above. This lab fixes the algebra that
estimation (Lab 06) and Bayesian updating with vectors (Lab 08) reuse.
