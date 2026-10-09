# Mental Models: Random Variables

## 1. A Random Variable Is a Measuring Tape Laid on Ω
The sample space is abstract (coin sequences, particle positions); the random variable is the function that reads off a number. Two different variables can sit on the same Ω — X = first head position, Y = number of heads — with different distributions. The model lives in the measure on Ω; the *usable* answer lives in the push-forward to ℝ.

## 2. The CDF Is a Bank Statement
F(x) = P(X ≤ x) accumulates every deposit up to x. Discrete: F is a staircase whose jumps are the PMF (jump size = P(X = k)). Continuous: F is smooth and f = F′. Mixed: a staircase with a smooth ramp — one formula, F, covers all three, which is exactly why Kolmogorov formalized through F rather than through densities.

## 3. Expectation as a Balance Point
Put each value x on a beam weighted by its probability; E[X] is where the beam balances. Consequences fall out mechanically: the balance point of aX + b is a·(balance) + b, and the balance point of a convex g(X) lies *above* g of the balance point (Jensen).

## 4. Variance as Average Radius Squared
Var(X) = E[(X − μ)²] — mean squared distance from the balance point. Squaring makes ± deviations interchangeable and punishes outliers quadratically, which is why a single 10σ event dominates the variance of a sample of 1 000.

## 5. Density Is Bookkeeping, Not Reality
f(x) has units of 1/x: double the measurement unit (cm → inches) and f rescales by the Jacobian so that probability stays invariant. Any statement in terms of f that changes under unit conversion is wrong; statements in terms of integrals are right.

## 6. The MGF Is a Zip File for Moments
M(t) = E[e^{tX}] generates every moment by differentiation: M′(0) = E[X], M″(0) = E[X²]. Two distributions with all moments equal can still differ (lognormal vs. others), so the *determining* transform is the characteristic function E[e^{itX}] — the same idea, but one that always exists and never overflows.

## Model 4: sum vs. average — where √n comes from

For i.i.d. Xᵢ with variance σ²:
- Var(X₁ + ... + Xₙ) = nσ² → SD of the *sum* grows like √n.
- Var(X̄) = σ²/n → SD of the *average* shrinks like √n.

So averaging reduces noise, but only by √n: cutting the standard error by 2 requires 4× the data. This one model explains why the CLT has √n in it, why A/B tests need large samples, and why pooling studies helps less than intuition suggests.

## Model 5: probability as area

A density is not a probability — f(0.3) can exceed 1. Probability is *area under the curve* over an interval. Two consequences students trip on:
- Making the support narrower with the same shape raises the density height (a density on [0, 0.5] uniform must be 2).
- P(X = x) = 0 for any continuous variable, yet P(a ≤ X ≤ b) > 0. The event "exactly 3.000…" is impossible; "within 3 ± 0.001" is not.

## Model 6: the likelihood is not the probability

P(data | θ) and P(θ | data) are different objects. The distribution tells you what data to expect from a known θ; the likelihood is that same expression read as a function of θ with the data held fixed. Confusing the two is the single most common error in estimation.

## Model 7: the 2-SD rule is a *normal* rule

| Number of SDs | % within (normal) | % within (arbitrary distribution, Chebyshev bound) |
|---|---|---|
| 1 | 68.3% | ≥ 0% (bound gives nothing) |
| 2 | 95.4% | ≥ 75% |
| 3 | 99.7% | ≥ 88.9% |

Chebyshev's inequality (1867) holds for *any* distribution: P(|X − μ| ≥ kσ) ≤ 1/k². Quote the 68-95-99.7 rule only after justifying normality; quote Chebyshev when you cannot.
