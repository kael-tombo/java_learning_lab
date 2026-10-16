# Code Deep Dive: Integral Fundamentals

Stdlib only (math, fractions). Observed outputs in comments.

## 1. Exact Riemann Sums (Fractions)

```python
from fractions import Fraction
dx = Fraction(1, 2)
L = sum([Fraction(0), Fraction(1,4), Fraction(1), Fraction(9,4)]) * dx
R = sum([Fraction(1,4), Fraction(1), Fraction(9,4), Fraction(4)]) * dx
M = sum([Fraction(1,16), Fraction(9,16), Fraction(25,16), Fraction(49,16)]) * dx
print(L, float(L))  # observed 7/4 1.75
print(R, float(R))  # observed 15/4 3.75
print(M, float(M))  # observed 21/8 2.625
print(Fraction(8,3), float(Fraction(8,3)))  # observed 8/3 2.6666666666666665
```

## 2. Convergence as n Grows

```python
def midpoint(f, a, b, n):
    dx = (b-a)/n
    return sum(f(a + (i+0.5)*dx) for i in range(n)) * dx
for n in [4, 40, 400]:
    print(n, midpoint(lambda x: x*x, 0, 2, n))
# observed: 4 2.625 | 40 2.6662500000000007 | 400 2.6666625 -> 2.6666... = 8/3
```

## 3. FTC Evaluations

```python
import math
print((9+3)-(1+1))          # observed 10 = int_1^3 (2x+1) dx
print(math.e - 1)           # observed 1.718281828459045 = int_0^1 e^x dx
print((2.00001**3/3 - 1.99999**3/3)/0.00002)  # observed 4.000000000026205 = F'(2) = f(2)
```
