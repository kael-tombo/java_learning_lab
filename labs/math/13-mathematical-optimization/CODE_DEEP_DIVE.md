# Code Deep Dive — Optimization, Stepped Through in the Open

Three runnable programs (stdlib only); every output block is a
verbatim captured run (PYTHONHASHSEED=0).

## 1. Five Learning Rates, Six Exact Steps Each

```python
from fractions import Fraction as F

print("f(x) = x^2, gradient 2x, start x0 = 5, update x <- x - eta*2*x:")
for eta in [F(1, 5), F(2, 5), F(11, 20), F(1), F(21, 20)]:
    x = F(5)
    traj = []
    for k in range(6):
        traj.append(x)
        x = x - eta * 2 * x
    print("eta = %s: %s" % (eta, " -> ".join(str(t) for t in traj)))

print("f(x, y) = x^2 + 10*y^2 from (5, 1):")
for eta in [F(9, 100), F(3, 40)]:
    x, y = F(5), F(1)
    arc = []
    for k in range(8):
        arc.append((x, y))
        x, y = x - eta * 2 * x, y - eta * 20 * y
    print("eta = %s: x chain %s" % (eta, " -> ".join(str(t[0]) for t in arc)))
    print("          y chain %s" % (" -> ".join(str(t[1]) for t in arc)))
```

Observed output:

```text
f(x) = x^2, gradient 2x, start x0 = 5, update x <- x - eta*2*x:
eta = 1/5: 5 -> 3 -> 9/5 -> 27/25 -> 81/125 -> 243/625
eta = 2/5: 5 -> 1 -> 1/5 -> 1/25 -> 1/125 -> 1/625
eta = 11/20: 5 -> -1/2 -> 1/20 -> -1/200 -> 1/2000 -> -1/20000
eta = 1: 5 -> -5 -> 5 -> -5 -> 5 -> -5
eta = 21/20: 5 -> -11/2 -> 121/20 -> -1331/200 -> 14641/2000 -> -161051/20000
f(x, y) = x^2 + 10*y^2 from (5, 1):
eta = 9/100: x chain 5 -> 41/10 -> 1681/500 -> 68921/25000 -> 2825761/1250000 -> 115856201/62500000 -> 4750104241/3125000000 -> 194754273881/156250000000
          y chain 1 -> -4/5 -> 16/25 -> -64/125 -> 256/625 -> -1024/3125 -> 4096/15625 -> -16384/78125
eta = 3/40: x chain 5 -> 17/4 -> 289/80 -> 4913/1600 -> 83521/32000 -> 1419857/640000 -> 24137569/12800000 -> 410338673/256000000
          y chain 1 -> -1/2 -> 1/4 -> -1/8 -> 1/16 -> -1/32 -> 1/64 -> -1/128
```

Converging, oscillating, orbiting, diverging — all four destinies are
visible in the six printed steps, and none of the bookkeeping left
exact fractions.

## 2. Convexity by Hessian Minors

```python
from fractions import Fraction as F

hes = {
    "x^2 + y^2":      [[F(2), F(0)], [F(0), F(2)]],
    "x^2 - y^2":      [[F(2), F(0)], [F(0), F(-2)]],
    "x*y":            [[F(0), F(1)], [F(1), F(0)]],
    "x^2 + 6xy + y^2": [[F(2), F(6)], [F(6), F(2)]],
    "x^2 + 4y^2":     [[F(2), F(0)], [F(0), F(8)]],
}
for name, HT in hes.items():
    lead, det_ = HT[0][0], HT[0][0] * HT[1][1] - HT[0][1] * HT[1][0]
    if det_ > 0 and lead > 0:
        verdict = "positive definite -> strictly convex"
    elif det_ >= 0 and lead >= 0:
        verdict = "positive semidefinite -> convex"
    else:
        verdict = "indefinite -> NOT convex (saddle directions exist)"
    print("%-18s minors %s, %s: %s" % (name, lead, det_, verdict))
print("for H = [[2,6],[6,2]]: det = 2*2 - 6*6 = -32; eigen lam^2 - 4*lam - 32 = 0 -> lam = 8, -4")
print("(x+3y)^2 - 8y^2 = x^2 + 6xy + 9y^2 - 8y^2 = x^2 + 6xy + y^2, so f4 is two-sided")
```

Observed output:

```text
x^2 + y^2          minors 2, 4: positive definite -> strictly convex
x^2 - y^2          minors 2, -4: indefinite -> NOT convex (saddle directions exist)
x*y                minors 0, -1: indefinite -> NOT convex (saddle directions exist)
x^2 + 6xy + y^2    minors 2, -32: indefinite -> NOT convex (saddle directions exist)
x^2 + 4y^2         minors 2, 16: positive definite -> strictly convex
for H = [[2,6],[6,2]]: det = 2*2 - 6*6 = -32; eigen lam^2 - 4*lam - 32 = 0 -> lam = 8, -4
(x+3y)^2 - 8y^2 = x^2 + 6xy + 9y^2 - 8y^2 = x^2 + 6xy + y^2, so f4 is two-sided
```

## 3. Vertex-Enumerated LP and the Tilted Quartic's Two Basins

```python
from fractions import Fraction as F
from itertools import combinations

cons = [("x+y", lambda x, y: x + y <= 4), ("x+3y", lambda x, y: x + 3 * y <= 6),
        ("x>=0", lambda x, y: x >= 0), ("y>=0", lambda x, y: y >= 0)]
lines = {("x+y"): (F(1), F(1), F(4)), ("x+3y"): (F(1), F(3), F(6)),
         ("x>=0"): (F(1), F(0), F(0)), ("y>=0"): (F(0), F(1), F(0))}
verts = [(F(0), F(0))]
for (i, j) in combinations(lines, 2):
    a, b, c = lines[i]
    d, e, g = lines[j]
    det = a * e - b * d
    if det != 0:
        x, y = (c * e - b * g) / det, (a * g - c * d) / det
        if all(fnc(x, y) for _, fnc in cons):
            verts.append((x, y))
            print("vertex %s & %s: (%s, %s) feasible, z = %s" % (i, j, x, y, 2 * x + 3 * y))
        else:
            print("vertex %s & %s: (%s, %s) infeasible" % (i, j, x, y))
best = max(verts, key=lambda v: 2 * v[0] + 3 * v[1])
print("LP optimum at x = %s, y = %s, z = %s" % (best[0], best[1], 2 * best[0] + 3 * best[1]))

def f(q):
    return q ** 4 / 4 - 2 * q * q + q / 4

print("exact f(-2) = %s vs f(2) = %s: the +x/4 tilt makes the LEFT basin lower" % (f(F(-2)), f(F(2))))
x = F(-1)
x = x - F(1, 10) * (x ** 3 - 4 * x + F(1, 4))
print("exact step 1 from x0 = -1: x1 = %s" % x)
for start in [F(-3), F(-1), F(0), F(1, 5), F(3)]:
    q = float(start)
    for k in range(200):
        q = q - 0.1 * (q ** 3 - 4 * q + 0.25)
    print("start %s -> GD lands at x = %.4f with f = %.4f" % (start, q, q ** 4 / 4 - 2 * q * q + q / 4))
```

Observed output:

```text
vertex x+y & x+3y: (3, 1) feasible, z = 9
vertex x+y & x>=0: (0, 4) infeasible
vertex x+y & y>=0: (4, 0) feasible, z = 8
vertex x+3y & x>=0: (0, 2) feasible, z = 6
vertex x+3y & y>=0: (6, 0) infeasible
vertex x>=0 & y>=0: (0, 0) feasible, z = 0
LP optimum at x = 3, y = 1, z = 9
exact f(-2) = -9/2 vs f(2) = -7/2: the +x/4 tilt makes the LEFT basin lower
exact step 1 from x0 = -1: x1 = -53/40
start -3 -> GD lands at x = -2.0305 with f = -4.5038
start -1 -> GD lands at x = -2.0305 with f = -4.5038
start 0 -> GD lands at x = -2.0305 with f = -4.5038
start 1/5 -> GD lands at x = 1.9680 with f = -3.5040
start 3 -> GD lands at x = 1.9680 with f = -3.5040
```

The matching endpoints −4.5038 and −3.5040 are basin verdicts, not
noise: the invariant left/right two minima genuinely differ by ~1.0
because the +x/4 tilt breaks the symmetric quartic's equality
f(−2) = f(2) into −9/2 versus −7/2.
