# Exercises — Distributions

Worked solutions; every number quoted is a run output from
CODE_DEEP_DIVE.md or a trivially checkable consequence of two such
outputs.

## Problem 1. Round-Trip a Piecewise Density
On [0, 2], place f(x) = x/2 extended by zero outside. Check the two pdf
axioms, then build F and differentiate back.

**Solution**: Mass: ∫_0^2 (x/2) dx = [x^2/4]_0^2 = 1 ✓ and f >= 0 ✓.
CDF: F(x) = x^2/4 on [0, 2], with F(2) = 1, F(1) = 1/4. Differentiating
recovers f = x/2 on the interior. Contrast with the lab's uniform case
(F(1) = 1/2 there): same-shape CDF logic, different derivative-back
answer — the round trip is what licenses the density claim.

## Problem 2. Binomial Tail by Hand-Machine Agreement
For Bin(10, 1/3), confirm P(X <= 1) and decompose it.

**Solution**: The run printed the exact value 2048/19683. Decomposition:
P(X = 0) = (2/3)^10 and P(X = 1) = 10(1/3)(2/3)^9; factor out
(2/3)^9 to get (2/3 + 10/3)(2/3)^9 = 4(2/3)^9 = 2048/19683. Machine
fraction and closed form coincide — no decimal was touched.

## Problem 3. Memorylessness Under an Unfamiliar Clock
For Exponential(1), evaluate P(X > 1.5 | X > 1) and explain what value
the memorylessness theorem forces.

**Solution**: By the theorem it must equal P(X > 0.5) = e^{−0.5} =
0.6065306597126334 — the run verified this both via the division
P(X > 1.5)/P(X > 1) and a direct exponent, digit-identical. Forgetting
the first hour of elapsed life is a certified property of this family;
try the same division on a uniform survival curve and watch it fail.

## Problem 4. Poisson Modeling at a Quiet Help Desk
Calls arrive as Poisson(λ = 2) per minute. Find P(exactly one silent
minute), i.e., k = 0, and the model's mean and variance.

**Solution**: P(X = 0) = e^{−2} = 0.1353352832366127 (run value). For
Poisson the mean and variance both equal λ, so each is 2. Both answers
come from the family statement — no simulation required — and the
printed 12-column table shows the mass decaying past the peak at
k = 1, 2 as the rates e^{−2} 2^k/k! divide by growing k!.

## Problem 5. Programming: Normal Middle and Tails
Implement `phit(z)` via `math.erf` returning Φ(z), then report
P(−1 < Z < 1), P(−2 < Z < 2), and P(Z > 2) to 16 digits.

**Solution skeleton**:

```python
import math

print("P(-1<X<1) =", 0.5 * (1 + math.erf(1 / math.sqrt(2))) - 0.5 *
      (1 + math.erf(-1 / math.sqrt(2))))
print("P(-2<X<2) =", 0.5 * (1 + math.erf(2 / math.sqrt(2))) - 0.5 *
      (1 + math.erf(-2 / math.sqrt(2))))
print("P(X>2) =", 1 - 0.5 * (1 + math.erf(2.0 / math.sqrt(2.0))))
```

Executed values: P(−1 < Z < 1) = 0.6826894921370856, P(−2 < Z < 2) =
0.9544997361036418 (verified by rerun), P(Z > 2) =
0.022750131948179098 — the engineered statements behind the 68/95
rule, each one an erf evaluation rather than a magic percent.
