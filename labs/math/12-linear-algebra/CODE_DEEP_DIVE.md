# Code Deep Dive — Linear Algebra, Exact by Construction

Two runnable Python programs (stdlib only); output blocks below are
verbatim captured runs with PYTHONHASHSEED=0.

## 1. Elimination to the Last Fraction

```python
from fractions import Fraction as F

def det3(m):
    return sum(m[0][j] * (-1) ** j
               * (m[1][(j + 1) % 3] * m[2][(j + 2) % 3]
                  - m[1][(j + 2) % 3] * m[2][(j + 1) % 3])
               for j in range(3))

rows = [[F(2), F(1), F(-1), F(8)], [F(-3), F(-1), F(3), F(-11)], [F(-2), F(1), F(2), F(-3)]]
A0, b0 = [r[:3] for r in rows], [r[3] for r in rows]
mults = []
for piv in range(2):
    for r in rows[piv + 1:]:
        m = r[piv] / rows[piv][piv]
        mults.append(m)
        for c in range(4):
            r[c] -= m * rows[piv][c]
print("elimination multipliers:", [str(m) for m in mults])
z = rows[2][3] / rows[2][2]
y = (rows[1][3] - rows[1][2] * z) / rows[1][1]
x = (rows[0][3] - rows[0][1] * y - rows[0][2] * z) / rows[0][0]
print("back-substitution: x = %s y = %s z = %s" % (x, y, z))
print("pivot product 2 * 1/2 * -5 =", F(2) * F(1, 2) * F(-5), "= det(A) =", det3(A0))
res = [A0[i][0] * x + A0[i][1] * y + A0[i][2] * z for i in range(3)]
print("residual A@sol == b:", [res[i] == b0[i] for i in range(3)])
```

Observed output:

```text
elimination multipliers: ['-3/2', '-1', '4']
back-substitution: x = 13/5 y = 13/5 z = -1/5
pivot product 2 * 1/2 * -5 = -5 = det(A) = -5
residual A@sol == b: [True, True, True]
```

Two determinant routes agreeing (pivots 2, 1/2, -5 multiply to the
cofactor expansion's -5) is the certificate the golden rule wanted:
in exact arithmetic the residual is false or zero, never "small."

## 2. Identities, Eigenpairs, and One Amplifier

```python
from fractions import Fraction as F
from decimal import Decimal, getcontext

def mm(P, Q):
    return [[sum(P[i][k] * Q[k][j] for k in range(len(Q)))
             for j in range(len(Q[0]))] for i in range(len(P))]

def tp(M):
    return [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]

A = [[F(1), F(2), F(3)], [F(0), F(-1), F(4)]]
B = [[F(2), F(1)], [F(1), F(3)], [F(-1), F(1)]]
AB, BA = mm(A, B), mm(B, A)
print("(AB)^T == B^T A^T:", tp(AB) == mm(tp(B), tp(A)),
      "| trace(AB) == trace(BA):", sum(AB[i][i] for i in (0, 1)) == sum(BA[i][i] for i in (0, 1, 2)))
A2 = [[F(2), F(1)], [F(1), F(2)]]
for lam, v in [(F(1), [F(1), F(-1)]), (F(3), [F(1), F(1)])]:
    w = [A2[i][0] * v[0] + A2[i][1] * v[1] for i in (0, 1)]
    print("lam=%d: A2 v = %s == lam v: %s" % (lam, w, [w[i] == lam * v[i] for i in (0, 1)]))
getcontext().prec = 24
r2 = Decimal(2).sqrt()
C2 = [[Decimal(3), Decimal(1)], [Decimal(1), Decimal(1)]]
for lam in (2 - r2, 2 + r2):
    v = [Decimal(1), lam - 3]
    w = [C2[i][0] * v[0] + C2[i][1] * v[1] for i in (0, 1)]
    print("lam = %s: |Av - lam v|_max = %s" % (str(lam), max(abs(w[i] - lam * v[i]) for i in (0, 1))))
A3 = [[F(1), F(2)], [F(2), F(4001, 1000)]]
detA3 = A3[0][0] * A3[1][1] - A3[0][1] * A3[1][0]
print("det(A3) = %s | kappa_1 = 6001/1000 * 6001 = %s" % (detA3, F(6001, 1000) * F(6001)))
for rhs in [F(6001, 1000), F(6002, 1000), F(6004, 1000)]:
    xs = [(A3[1][1] * F(3) - A3[0][1] * rhs) / detA3,
          (A3[0][0] * rhs - A3[1][0] * F(3)) / detA3]
    print("b2 = %s -> x = (%s, %s)" % (rhs, xs[0], xs[1]))
Ainv = [[F(4001), F(-2000)], [F(-2000), F(1000)]]
AA = [[sum(A3[i][k] * Ainv[k][j] for k in (0, 1)) for j in (0, 1)] for i in (0, 1)]
print("A3 @ Ainv == I exactly:", AA == [[F(1), F(0)], [F(0), F(1)]])
```

Observed output:

```text
(AB)^T == B^T A^T: True | trace(AB) == trace(BA): True
lam=1: A2 v = [Fraction(1, 1), Fraction(-1, 1)] == lam v: [True, True]
lam=3: A2 v = [Fraction(3, 1), Fraction(3, 1)] == lam v: [True, True]
lam = 0.58578643762690495119831: |Av - lam v|_max = 0E-23
lam = 3.41421356237309504880169: |Av - lam v|_max = 0E-23
det(A3) = 1/1000 | kappa_1 = 6001/1000 * 6001 = 36012001/1000
b2 = 6001/1000 -> x = (1, 1)
b2 = 3001/500 -> x = (-1, 2)
b2 = 1501/250 -> x = (-5, 4)
A3 @ Ainv == I exactly: True
```

For the irrational case the residual `0E-23` is zero at the adopted
24-digit Decimal precision, not rounded noise: with v = (1, lam - 3),
row 1 of A v equals 3 + (lam - 3) = lam, and row 2 equals
1 + (lam - 3) = lam - 2, which equals lam * (lam - 3) = lam^2 - 3 lam
because lam^2 = 4 lam - 2. The certificate is algebra confirmed by
print, not numerics blessed with small error.
