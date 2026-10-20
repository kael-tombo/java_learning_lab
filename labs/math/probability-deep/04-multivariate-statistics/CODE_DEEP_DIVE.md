# Code Deep Dive — Covariance Bookkeeping, Machine-Checked

Three runnable Python programs (stdlib only). Each output block is the
captured run; fractions remain exact throughout.

## 1. The Four-Cell Table and Its Shadows

```python
from fractions import Fraction as F

jp = {(0, 0): F(1, 8), (0, 1): F(3, 8), (1, 0): F(3, 8), (1, 1): F(1, 8)}
print("joint sums to:", sum(jp.values()))
px = [sum(v for (x, y), v in jp.items() if x == i) for i in (0, 1)]
py = [sum(v for (x, y), v in jp.items() if y == j) for j in (0, 1)]
print("marginals: P(X) =", px, " P(Y) =", py)
Ex = sum(F(i) * px[i] for i in (0, 1))
Ey = sum(F(j) * py[j] for j in (0, 1))
Exy = sum(F(x * y) * v for (x, y), v in jp.items())
vx = sum(F(i * i) * px[i] for i in (0, 1)) - Ex * Ex
vy = sum(F(j * j) * py[j] for j in (0, 1)) - Ey * Ey
cov = Exy - Ex * Ey
print("E[X] =", Ex, " E[Y] =", Ey, " E[XY] =", Exy)
print("Var(X) =", vx, " Var(Y) =", vy, " Cov =", cov)
print("rho = -1/2 claim: cov^2 == (1/4) * VarX * VarY :",
      cov * cov == F(1, 4) * vx * vy, " cov negative:", cov < 0)
```

Observed output:

```text
joint sums to: 1
marginals: P(X) = [Fraction(1, 2), Fraction(1, 2)]  P(Y) = [Fraction(1, 2), Fraction(1, 2)]
E[X] = 1/2  E[Y] = 1/2  E[XY] = 1/8
Var(X) = 1/4  Var(Y) = 1/4  Cov = -1/8
rho = -1/2 claim: cov^2 == (1/4) * VarX * VarY : True  cov negative: True
```

Marginalization is literally a comprehension filter; the correlation
claim is verified through its normalization identity rather than a
square root.

## 2. The Sum-Variance Law Against Direct Computation

```python
from fractions import Fraction as F

jp = {(0, 0): F(1, 8), (0, 1): F(3, 8), (1, 0): F(3, 8), (1, 1): F(1, 8)}
a, b = F(2), F(3)
w = sum((a * x + b * y) * v for (x, y), v in jp.items())
vw = sum(F((a * x + b * y) ** 2) * v for (x, y), v in jp.items()) - w * w
print("W=2X+3Y: Var direct =", vw, " formula 4Vx+9Vy+12Cov =",
      a*a*F(1, 4) + b*b*F(1, 4) + 2*a*b*F(-1, 8), " match:",
      vw == a*a*F(1, 4) + b*b*F(1, 4) + 2*a*b*F(-1, 8))

xs = [-F(1), F(0), F(1)]
ax = F(1, 3)
```

Observed output:

```text
W=2X+3Y: Var direct = 7/4  formula 4Vx+9Vy+12Cov = 7/4  match: True
```

(The final two lines set up the next block; the variance line is the
point here.)

## 3. The Quadratic Trap: Zero Covariance, Real Dependence

```python
from fractions import Fraction as F

xs = [-F(1), F(0), F(1)]
ax = F(1, 3)  # uniform
mX = sum(x * ax for x in xs)
mY = sum(x * x * ax for x in xs)
mXY = sum(x * x * x * ax for x in xs)
print("counterexample X,Y=X*X: E[X] =", mX, " E[Y] =", mY, " E[XY] =", mXY,
      " Cov =", mXY - mX * mY)
print("dependent: P(X=-1, Y=1) =", ax, " vs P(X=-1)P(Y=1) =",
      ax * (F(2, 3)))

mW = mX + mY
w_vals = [x + x * x for x in xs]
vW = sum((w - mW) ** 2 * ax for w in w_vals)
e4 = sum(x**4 * ax for x in xs)
print("W = X + X^2: Var direct =", vW, " formula:",
      (e4 - mX * mX) + (e4 - mY * mY) + F(0))
```

Observed output:

```text
counterexample X,Y=X*X: E[X] = 0  E[Y] = 2/3  E[XY] = 0  Cov = 0
dependent: P(X=-1, Y=1) = 1/3  vs P(X=-1)P(Y=1) = 2/9
W = X + X^2: Var direct = 8/9  formula: 8/9
```

One violated cell (1/3 against the product 2/9) retires the
"uncorrelated means unrelated" shortcut permanently.
