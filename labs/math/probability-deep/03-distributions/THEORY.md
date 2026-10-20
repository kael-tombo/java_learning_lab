# Distributions — Theory

## 1. From Table to Curve
A distribution is the induced measure of a random variable. Discrete
variables store mass at points (a PMF); continuous variables smear mass
over intervals (a PDF). Both are read through one shared instrument,
the CDF.

## 2. PDF Axioms and the CDF Relations
A density f: R → [0, ∞) obeys exactly two rules:
- Nonnegativity: f(x) >= 0 everywhere.
- Total mass: ∫ f(x) dx over the whole line equals 1.
Then P(a <= X <= b) = ∫_a^b f(x) dx, and the CDF is F(x) =
∫_{−∞}^{x} f(t) dt. At every continuity point of f the differentiation
recovers the density: F'(x) = f(x). Two subtleties worth stating
exactly:
- P(X = x) = 0 for a continuous variable — single points carry no mass,
  so P(X <= x) and P(X < x) coincide.
- The pdf value is not a probability; only its integrals over intervals
  are. Densities may exceed 1 (Uniform on [0, 1/2] has f = 2).

## 3. Named Families — Exact Definitions
- Uniform(a, b): f(x) = 1/(b−a) on [a, b], zero elsewhere; F(x) =
  (x−a)/(b−a) inside, a straight ramp.
- Exponential(λ): f(x) = λ e^{−λx} for x >= 0; CDF
  F(t) = 1 − e^{−λt}; survival P(X > t) = e^{−λt}.
- Binomial(n, p): P(k) = C(n,k) p^k (1−p)^{n−k} for k = 0..n; mean np,
  variance np(1−p).
- Poisson(λ): P(k) = e^{−λ} λ^k / k!; mean λ and variance λ; arises as
  the binomial limit n·p → λ.
- Normal(μ, σ^2): f(x) = (1/(σ√(2π))) exp(−(x−μ)^2/(2σ^2)); the
  standardized variable Z = (X − μ)/σ is Normal(0, 1), and
  Φ(z) = (1 + erf(z/√2))/2.

## 4. Memorylessness — Statement
The exponential is the only continuous distribution with the property
  P(X > s + t | X > s) = P(X > t) for all s, t >= 0.
The survival ratio e^{−λ(s+t)}/e^{−λs} collapses to e^{−λt}: elapsed
age leaves no trace. Geometric is its discrete-only analogue.

## 5. Normal Tail Machinery
By symmetry of the standardized density: Φ(−z) = 1 − Φ(z), so two-sided
interval probabilities are reductions to Φ at positive arguments, e.g.
P(|Z| < 1) = 2Φ(1) − 1. Quantile rules with computed backing: the
interval [μ − σ, μ + σ] holds about 68% of the mass and
[μ − 2σ, μ + 2σ] about 95% — decimals for both sit in
MATH_FOUNDATION.md, calculated rather than recited from memory.

## 6. Why Families Are Named at All
Modeling reduces description to parameters: count successes (binomial),
time-to-first-event with constant hazard (exponential), many weak
independent causes with small rates (Poisson), sums of many comparable
contributions (normal — the CLT of Lab 05 upgrades this to a theorem).
Each family's parameter-fitting is unique to its shape, which is why
identification precedes estimation in any applied pipeline.
