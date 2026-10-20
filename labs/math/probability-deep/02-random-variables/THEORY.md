# Random Variables — Theory

## 1. What a Random Variable Is
A random variable X on a probability space (Ω, F, P) is a function
X: Ω → R that is measurable — for every set of reals one cares about,
the outcomes that map into it form an event of F. Nothing mysterious: X
is a bookkeeping device that attaches a number to each outcome, and all
its "randomness" is inherited from P on Ω.

## 2. The Induced Distribution
X drags the measure along: P_X(B) = P({ω : X(ω) ∈ B}). Everything about
X is contained in this pushed-forward measure; the original Ω can be
forgotten. For X taking values in a countable set {x1, x2, ...}:
- PMF: p(k) = P(X = k), with Σ_k p(k) = 1 and each p(k) >= 0.
- CDF: F(x) = P(X <= x), a step function absorbing mass as x grows.

## 3. CDF — Exact Statement of Properties
- Nondecreasing: x <= y implies F(x) <= F(y) (events nest).
- Right-continuous, with limits F(x) → 0 as x → −∞ and → 1 as x → +∞.
- For a discrete X the inverse relation is the sum:
  F(x) = Σ_{k <= x} p(k), and p(k) = F(k) − F(k−1) — the jump sizes.
- Any function F with the three properties above is the CDF of some X
  (Lebesgue's inversion theorem); the two roles are reversible.

## 4. Expectation
For a discrete X with finite mean-summable support:
  E[X] = Σ_k k · p(k),
the PMF-weighted center of mass. Expectation of a function — the
"LOTUS" principle — needs no new machinery:
  E[g(X)] = Σ_k g(k) p(k).
Care point: E[g(X)] ≠ g(E[X]) in general for nonlinear g (see
MATH_FOUNDATION.md for an executed counterexample).

## 5. Linearity of Expectation — Statement and Mechanism
For random variables X, Y (jointly defined on Ω) and constants a, b:
  E[aX + bY] = a E[X] + b E[Y].
No independence assumption appears in the hypothesis — the result holds
for arbitrarily dependent variables. The discrete proof is a swap of
finite (or absolutely convergent) double sums:
Σ_x Σ_y (ax + by) p(x, y) = a Σ_x x Σ_y p(x, y) + b Σ_y y Σ_x p(x, y).

## 6. Variance
Definition: Var(X) = E[(X − E[X])^2], always >= 0. The computational
identity, expanded straight from the definition and linearly:
  Var(X) = E[X^2] − (E[X])^2.
Scaling rules — Var(aX + b) = a^2 Var(X) (the shift b drops out because
variance is E of a squared deviation), and Var(X + Y) = Var(X) + Var(Y)
only under zero covariance, which independence guarantees (Lab 04
revisits the general formula). Standard deviation is sqrt(Var(X)), the
natural scale on which deviations live.

## 7. Joint Distributions of Two Variables
Two discrete variables have a joint PMF p(x, y) = P(X = x, Y = y);
marginals recover p(x) = Σ_y p(x, y). Independence of variables means
p(x, y) = p(x) p(y) for every pair — a stronger condition than merely
uncorrelated behavior (counterexample executed in Lab 04).
