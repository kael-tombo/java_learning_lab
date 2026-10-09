# How It Works: Random Variables

## 1. From outcomes to numbers
A random variable is a function X on Ω. Probability on Ω induces a *push-forward* measure on ℝ: P(X ∈ B) = P({ω : X(ω) ∈ B}). For the 3-flip example the eight sequences map to {0,1,2,3}; the three sequences with exactly one head (HTT, THT, TTH) all land on 1, so P(X = 1) = 3/8. The mapping collapses outcomes, and the PMF is just counting how many land on each number.

## 2. PMF → CDF → density: three views, one distribution
PMF (discrete): p(k). CDF: F(x) = Σ_{k ≤ x} p(k), a staircase. Continuous: F is differentiable and f = F′. Because F always exists, it is the canonical object; PMF/PDF are conveniences for their respective cases.

## 3. Expectation: one operator, two mechanisms
Discrete: Σ x·p(x) — a weighted average. Continuous: ∫ x·f(x) dx — a weighted average with the weights spread over an interval. Both are the same measure integral E[X] = ∫ x dF(x); the machinery differs, the meaning (balance point) does not.

## 4. Why E is linear and Var is not
E[aX + bY] = aE[X] + bE[Y] follows by splitting one sum/integral — no independence needed. Variance expands as E[(X+Y)²] − (E[X]+E[Y])², and the cross term 2E[XY] − 2E[X]E[Y] = 2Cov(X,Y) survives unless X and Y are uncorrelated. This is why the variance of a *difference* of two independent estimates adds, but the variance of a paired difference subtracts the covariance twice.

## 5. Transformations carry mass correctly
Y = g(X): pull y back to the set g⁻¹({y}), sum (discrete) or integrate with the Jacobian |dx/dy| (continuous). For Y = 5X + 1 the inverse is a single branch with |dx/dy| = 1/5, giving f_Y(y) = f_X((y−1)/5)/5; the factor 1/5 is exactly what makes ∫f_Y = 1 while stretching the support by 5.

## 6. Moments summarize, the distribution decides
E and Var compress a whole distribution to two numbers — sufficient for affine questions and, by the CLT, for sums. Non-linear decisions (P(loss > threshold), E[utility]) need the full distribution; labs 03 (named families), 07 (tails) and 08 (priors) each go deeper on exactly that gap.

## Worked example: transforming a uniform draw

Problem: generate Y = eˣ where X ~ Uniform(0, 1) is unavailable directly, but you can draw U ~ Uniform(0, 1).

Method (inverse CDF): F_Y(y) = P(eˣ ≤ y) = P(X ≤ ln y) = ln y for 1 ≤ y ≤ e.
So F_Y(y) = ln y, and F_Y⁻¹(u) = eᵘ. Draw U and set Y = eᵁ.

Check the moments against theory:
- E[Y] = ∫₁ᵉ y · (1/y) dy = ∫₁ᵉ 1 dy = e − 1 ≈ 1.718.
- E[Y²] = ∫₁ᵉ y² · (1/y) dy = ∫₁ᵉ y dy = (e² − 1)/2 ≈ 3.1945.
- Var(Y) = 3.1945 − 1.718² ≈ 0.2530, SD ≈ 0.503.

Note the trap: Y's density on [1, e] is 1/y — it is *not* uniform, even though the transform is monotone. Transforming the bounds of a uniform is not enough; transform the density by the Jacobian: f_Y(y) = f_X(g⁻¹(y)) · |d/dy g⁻¹(y)|.
