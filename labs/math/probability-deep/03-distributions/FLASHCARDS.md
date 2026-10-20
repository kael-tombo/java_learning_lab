# Flashcards — Distributions

## Definition Cards

### Card 1
**Front**: The two PDF axioms?
**Back**: f(x) >= 0 everywhere, and the integral of f over the whole
line equals 1; probabilities are integrals over intervals only.

### Card 2
**Front**: State the three CDF-factor properties that make an F a valid
CDF.
**Back**: Nondecreasing, right-continuous, connecting limits 0 and 1 at
−∞ and +∞; conversely any such F is some variable's distribution.

### Card 3
**Front**: Density from CDF and back?
**Back**: F(x) = ∫_{−∞}^x f(t) dt, and F'(x) = f(x) wherever f is
continuous; the pair round-trips at continuity points.

### Card 4
**Front**: P(X = x) for a continuous variable?
**Back**: Exactly 0 — points carry no mass under a density, so strict
and weak interval bounds coincide.

## Theorem Cards

### Card 5
**Front**: State memorylessness for the exponential family.
**Back**: P(X > s + t | X > s) = P(X > t) for all s, t >= 0; the
exponential is the ONLY continuous family with this survival
self-similarity.

### Card 6
**Front**: Binomial(n, p): pmf, mean, variance?
**Back**: P(k) = C(n,k) p^k (1−p)^{n−k}, mean np, variance np(1−p);
binomial coefficients over a symmetric p give a symmetric pmf.

### Card 7
**Front**: Poisson(λ): pmf and its moment pair?
**Back**: P(k) = e^{−λ} λ^k / k!; mean = variance = λ; the binomial
limit when n is large, p small, and np stays at λ.

### Card 8
**Front**: Standardization of Normal(μ, σ²)?
**Back**: Z = (X − μ)/σ is Normal(0, 1), and Φ(z) =
(1 + erf(z/√2))/2 gives every normal probability through a single
function.

### Card 9
**Front**: Symmetry identity for Φ?
**Back**: Φ(−z) = 1 − Φ(z); two-sided interval reads reduce to positives:
P(|Z| < c) = 2Φ(c) − 1.

## Judge-the-Number Cards

### Card 10
**Front**: Φ(1) and Φ(2) to machine precision?
**Back**: 0.8413447460685428 and 0.9772498680518209 (erf-evaluated, not
recalled).

### Card 11
**Front**: Truncated Poisson(2) through k = 11 — how close to 1?
**Back**: 0.9999986353848405; the deficit 1.4e−06 is truncation mass
beyond k = 11.

### Card 12
**Front**: Uniform[0,2]: F(1) and total density mass?
**Back**: F(1) = 1/2 exactly (rational), total mass 1 exactly — the
straight-ramp CDF closes its integral.
