# Flashcards — Multivariate Statistics

## Definition Cards

### Card 1
**Front**: Define the joint PMF and the marginal recovery formulas.
**Back**: p(x, y) = P(X = x, Y = y), nonnegative summing to 1 over the
grid; marginals p_X(x) = Σ_y p(x, y) collapse the second axis.

### Card 2
**Front**: Covariance — computational definition and expanded one?
**Back**: Cov(X, Y) = E[(X − E[X])(Y − E[Y])] = E[XY] − E[X] E[Y]; the
identity holds by expanding deviations and applying linearity.

### Card 3
**Front**: Correlation coefficient definition and its exact range?
**Back**: ρ = Cov/(σ_X σ_Y) for positive variances; −1 <= ρ <= 1, with
endpoints exactly when one variable is an affine function of the other
almost surely.

### Card 4
**Front**: Covariance matrix — entries and the structural property?
**Back**: Σ_ij = Cov(X_i, X_j): variances on the diagonal, symmetric
elsewhere; Σ is positive semidefinite since a'Σa = Var(a·X) >= 0.

## Theorem Cards

### Card 5
**Front**: The variance law of sums — exact statement?
**Back**: Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X, Y); the extended form
is Var(Σ a_i X_i) = Σ_i Σ_j a_i a_j Cov(X_i, X_j).

### Card 6
**Front**: State bilinearity of covariance.
**Back**: Cov(aX + b, cY + d) = ac Cov(X, Y) — additive shifts vanish,
scales multiply through once each.

### Card 7
**Front**: Independence condition for discrete partners?
**Back**: p(x, y) = p_X(x) p_Y(y) at EVERY cell; one violated cell
suffices to certify dependence.

### Card 8
**Front**: Does zero covariance imply independence?
**Back**: Never in general — the X uniform on {−1,0,1}, Y = X^2 trap has
Cov = 0 (E[X^3] = 0 typed out) yet full determination, one violated cell
at (−1, 1): 1/3 vs product 2/9.

## Judge-the-Number Cards

### Card 9
**Front**: The four-cell table (1/8, 3/8, 3/8, 1/8): E[XY] and Cov?
**Back**: E[XY] = 1/8 (mass of cell (1,1), the only nonzero product) and
Cov = 1/8 − 1/4 = −1/8.

### Card 10
**Front**: Same table: Var(2X + 3Y)?
**Back**: 4·(1/4) + 9·(1/4) + 12·(−1/8) = 7/4 — formula and direct
computation printed identical values.

### Card 11
**Front**: Same table: correlation and conditional rows?
**Back**: ρ = −1/2 exactly; rows rescale to (3/4, 1/4) and (1/4, 3/4) —
conditioning reverses which Y value is favored.
