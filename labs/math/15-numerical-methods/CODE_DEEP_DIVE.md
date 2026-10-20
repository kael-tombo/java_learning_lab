# Code Deep Dive - Root Finding and Rounding, Checked Line by Line

Three stdlib-only programs ran under PYTHONHASHSEED=0 and
PYTHONIOENCODING=utf-8; each output block below is verbatim stdout,
pasted from the capture, never retyped.

## 1. Bisection Rows, Newton Columns, and a Failure Cycle

```python
from fractions import Fraction as F


def f(x):
    return x * x * x - x - 2


root = 1.5213797968070963

a, b, fa = 1.0, 2.0, f(1.0)
for k in range(10):
    m = 0.5 * (a + b)
    if k < 4:
        print("bisect k=%d mid=%.8f f(mid)=%+.6f width=%.6f" % (k + 1, m, f(m), b - a))
    if fa * f(m) > 0:
        a = m
    else:
        b = m
print("after 10 halvings: a=%.6f b=%.6f bound |b-a|/2 = %.7f" % (a, b, (b - a) / 2))

x, ep = 2.0, 2.0 - root
for k in range(1, 4):
    x = x - f(x) / (3 * x * x - 1)
    e = x - root
    print("newton k=%d x=%.13f e=%.3e |e/e_prev|=%.4f |e/e_prev^2|=%.4f"
          % (k, x, e, abs(e / ep), abs(e / ep ** 2)))
    ep = e
print("Taylor constant f''(r)/(2f'(r)) = 6r/(2(3r^2-1)) =", 6 * root / (2 * (3 * root * root - 1)))


def g(x):
    return F(x) ** 3 - 2 * F(x) + 2


y = F(0)
arc = []
for k in range(8):
    y = y - g(y) / (3 * y * y - 2)
    arc.append(y)
print("Newton on x^3 - 2x + 2 from 0:", " -> ".join(str(t) for t in arc))
```

Observed output:

```text
bisect k=1 mid=1.50000000 f(mid)=-0.125000 width=1.000000
bisect k=2 mid=1.75000000 f(mid)=+1.609375 width=0.500000
bisect k=3 mid=1.62500000 f(mid)=+0.666016 width=0.250000
bisect k=4 mid=1.56250000 f(mid)=+0.252197 width=0.125000
after 10 halvings: a=1.520508 b=1.521484 bound |b-a|/2 = 0.0004883
newton k=1 x=1.6363636363636 e=1.150e-01 |e/e_prev|=0.2402 |e/e_prev^2|=0.5019
newton k=2 x=1.5303920521312 e=9.012e-03 |e/e_prev|=0.0784 |e/e_prev^2|=0.6816
newton k=3 x=1.5214414651351 e=6.167e-05 |e/e_prev|=0.0068 |e/e_prev^2|=0.7593
Taylor constant f''(r)/(2f'(r)) = 6r/(2(3r^2-1)) = 0.7678837587311055
Newton on x^3 - 2x + 2 from 0: 1 -> 0 -> 1 -> 0 -> 1 -> 0 -> 1 -> 0
```

The width column shows the bracket BEFORE the new midpoint is
admitted; 0.0004883 is the bound, half of the final 1/1024 width.
Newton's quadratic regime is visible in |e/e_prev^2| climbing
0.5019 -> 0.6816 -> 0.7593 toward the forecast 0.7679. The cycle
block runs in exact fractions on purpose: f maps 0 -> 1 and 1 -> 0
in integers, so the orbit is provably eternal.

## 2. Linear Versus Quadratic on x <- exp(-x)

```python
from math import exp

r = 0.5671432904097839    # fixed point of x -> exp(-x)

print("plain fixed point x <- exp(-x), from x0 = 1:")
x, ep = 1.0, 1.0 - r
for k in range(1, 5):
    x = exp(-x)
    e = x - r
    print("k=%d x=%.10f e=%+.3e ratio e/e_prev=%.4f" % (k, x, e, e / ep))
    ep = e

print("Newton on f(x) = exp(-x) - x from x0 = 1:")
y, ep = 1.0, 1.0 - r
for k in range(1, 4):
    y = y - (exp(-y) - y) / (-exp(-y) - 1)
    e = y - r
    print("k=%d y=%.16f e=%+.3e |e/e_prev|=%.4f |e/e_prev^2|=%.4f"
          % (k, y, e, abs(e / ep), abs(e / ep ** 2)))
    ep = e
print("linear rate |g'(r)| = exp(-r) =", exp(-r), "= r itself; Newton is quadratic")
```

Observed output:

```text
plain fixed point x <- exp(-x), from x0 = 1:
k=1 x=0.3678794412 e=-1.993e-01 ratio e/e_prev=-0.4603
k=2 x=0.6922006276 e=+1.251e-01 ratio e/e_prev=-0.6276
k=3 x=0.5004735006 e=-6.667e-02 ratio e/e_prev=-0.5331
k=4 x=0.6062435351 e=+3.910e-02 ratio e/e_prev=-0.5865
Newton on f(x) = exp(-x) - x from x0 = 1:
k=1 y=0.5378828427399902 e=-2.926e-02 |e/e_prev|=0.0676 |e/e_prev^2|=0.1562
k=2 y=0.5669869914054133 e=-1.563e-04 |e/e_prev|=0.0053 |e/e_prev^2|=0.1826
k=3 y=0.5671432859891230 e=-4.421e-09 |e/e_prev|=0.0000 |e/e_prev^2|=0.1810
linear rate |g'(r)| = exp(-r) = 0.5671432904097838 = r itself; Newton is quadratic
```

One race, two speeds. The plain fixed point multiplies its error by a
factor near -0.567 each step (linear, alternating sign); Newton squares
it, landing 4.4e-9 away in three steps, with |e/e_prev^2| = 0.1810
matching the theory constant r/(2(1 + r)) from the foundation file.

## 3. Quadrature Ratios and Two Cancellation Setups

```python
from math import exp

I = exp(1) - 1.0    # exact value of the integral of e^x on [0,1]

def trapz(n):
    h = 1.0 / n
    return h * (0.5 * (1.0 + exp(1)) + sum(exp(k * h) for k in range(1, n)))

def simp(n):
    h = 1.0 / n
    s = 1.0 + exp(1)
    s += 4 * sum(exp((2 * k - 1) * h) for k in range(1, n // 2 + 1))
    s += 2 * sum(exp(2 * k * h) for k in range(1, n // 2))
    return s * h / 3

prevT = prevS = None
for n in (4, 8, 16, 32):
    et, es = abs(trapz(n) - I), abs(simp(n) - I)
    if prevT is None:
        print("n=%2d trapz err=%.9f | simp err=%.9f" % (n, et, es))
    else:
        print("n=%2d trapz err=%.9f ratio %.2f | simp err=%.9f ratio %.2f"
              % (n, et, prevT / et, es, prevS / es))
    prevT, prevS = et, es
print("exact = e - 1 = %.15f | theory: trapz ~ (e-1)h^2/12 = %.3e at n=32; simp ~ (e-1)h^4/180"
      % (I, (I) / 12 / 32 ** 2))

big = 10 ** 16
print("exact ints: (10^16 + 1) - 10^16 =", (big + 1) - big)
print("in floats:  (10^16.0 + 1) - 10^16 =", float(big) + 1.0 - float(big))
B, C = 1e8, 1.0
disc = B * B - 4 * C
r_big = (B + disc ** 0.5) / 2
print("quadratic x^2 - 1e8 x + 1 = 0: naive small root %.10g, stable C/root_big = %.17g" % ((B - disc ** 0.5) / 2, C / r_big))
print("naive relative error against true 1e-8: %s" % ((abs((B - disc ** 0.5) / 2 - 1e-8) / 1e-8)))
```

Observed output:

```text
n= 4 trapz err=0.008940076 | simp err=0.000037013
n= 8 trapz err=0.002236764 ratio 4.00 | simp err=0.000002326 ratio 15.91
n=16 trapz err=0.000559300 ratio 4.00 | simp err=0.000000146 ratio 15.98
n=32 trapz err=0.000139832 ratio 4.00 | simp err=0.000000009 ratio 15.99
exact = e - 1 = 1.718281828459045 | theory: trapz ~ (e-1)h^2/12 = 1.398e-04 at n=32; simp ~ (e-1)h^4/180
exact ints: (10^16 + 1) - 10^16 = 1
in floats:  (10^16.0 + 1) - 10^16 = 0.0
quadratic x^2 - 1e8 x + 1 = 0: naive small root 7.450580597e-09, stable C/root_big = 1e-08
naive relative error against true 1e-8: 0.2549419403076172
```

Halving the panel divides the trapezoid error by 4.00 every time (order
h^2), and Simpson's by 15.91 -> 15.99 (order h^4, rounding home to 16);
the theory line is no decoration: 1.398e-04 matches the measured
0.000139832 at n = 32. Then the two subtraction exhibits: integers kept
the 1 where doubles lost it to 0.0, and the naive small root of
x^2 - 1e8*x + 1 missed by 25.49% while C/root_big reported 1e-08 exactly.
