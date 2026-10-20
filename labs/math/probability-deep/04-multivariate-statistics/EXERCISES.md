# Exercises — Multivariate Statistics

Solutions quote run outputs from CODE_DEEP_DIVE.md; derived steps stay
in exact rational arithmetic.

## Problem 1. Correlation With a Square root Avoided
Using the four-cell table (Var = 1/4 each, Cov = −1/8), prove ρ = −1/2
without floating point.

**Solution**: ρ = Cov / sqrt(VarX VarY); here sqrt(1/16) = 1/4 is exact,
so ρ = (−1/8)/(1/4) = −1/2. The machine check — cov^2 == (1/4)·VarX·VarY
printed True — certifies the square of ρ; the sign (cov negative True)
fixes the minus. Both halves together pin ρ = −1/2 exactly.

## Problem 2. Conditional Rows Reversed
From the same table, give the conditional distribution of Y given X = x
for both x ∈ {0, 1}, and connect it to the correlation sign.

**Solution**: Row x = 1: cells 3/8 and 1/8, rescaled by 1/2 →
(3/4, 1/4). Row x = 0: rescaled → (1/4, 3/4). Conditioning flips the
likely answer back and forth, the table-face of negative association.
Product rule audit: the independence candidate p_X(x) p_Y(y) equals
1/4 at every cell, while the observed cells are 1/8, 3/8, 3/8, 1/8 —
all four disagree, so dependence holds on the entire grid, not a
single witness cell.

## Problem 3. General Linear Combination, Heavy Coefficients
On the same table compute Var(4X − 5Y) via the formula and confirm it
with the direct definition.

**Solution**: Formula route: a²VarX + b²VarY + 2ab·Cov =
16·(1/4) + 25·(1/4) + 2·4·(−5)·(−1/8) = 4 + 25/4 + 5 = 61/4.
Direct route: W = 4X − 5Y takes values 0, −5, 4, −1 with masses
1/8, 3/8, 3/8, 1/8. Then E[W] = (0 − 15 + 12 − 1)/8 = −1/2 and
E[W²] = (75 + 48 + 1)/8 = 124/8 = 31/2, so
Var(W) = 31/2 − 1/4 = 62/4 − 1/4 = 61/4. Both roads print 61/4 —
the cross term +5 (scale product 20 times covariance −1/8, doubled)
is exactly what the negative covariance buys back.

## Problem 4. Programming: Covariance Matrix From a Table
Implement `cov_matrix(joint)` that maps a dict {(x, y): Fraction} to
the 2x2 exact covariance matrix [[VarX, Cov], [Cov, VarY]] and run it
on the four-cell table; verify the diagonal and the −1/8 off-diagonal.

**Solution skeleton**:

```python
from fractions import Fraction as F

def cov_matrix(jp):
    px = {x: sum(v for (a, b), v in jp.items() if a == x) for x, _ in jp}
    py = {y: sum(v for (a, b), v in jp.items() if b == y) for _, y in jp}
    mx = sum(F(x) * v for x, v in px.items())
    my = sum(F(y) * v for y, v in py.items())
    cov = sum(F(x * y) * v for (x, y), v in jp.items()) - mx * my
    vx = sum(F(x * x) * v for x, v in px.items()) - mx * mx
    vy = sum(F(y * y) * v for y, v in py.items()) - my * my
    return [[vx, cov], [cov, vy]]

jp = {(0, 0): F(1, 8), (0, 1): F(3, 8), (1, 0): F(3, 8), (1, 1): F(1, 8)}
print(cov_matrix(jp))
```

Executed on the lab table it returned
[[Fraction(1, 4), Fraction(-1, 8)], [Fraction(-1, 8), Fraction(1, 4)]]
— the diagonal carries the variances from MATH_FOUNDATION.md, the
off-diagonal repeats the −1/8, and symmetry holds by construction.

## Problem 5. A Cell That Convicts
For the quadratic trap (X uniform on {−1,0,1}, Y = X^2), list one joint
cell where independence fails and give both sides of the comparison.

**Solution**: Cell (−1, 1): the joint mass is 1/3 (X = −1 forces
Y = X^2 = 1), while the independence product is
P(X = −1) P(Y = 1) = 1/3 · 2/3 = 2/9. Run printed exactly this pair
(1/3 vs 2/9) alongside Cov = 0 — one cell beats one second-moment
number when it comes to detecting dependence.
