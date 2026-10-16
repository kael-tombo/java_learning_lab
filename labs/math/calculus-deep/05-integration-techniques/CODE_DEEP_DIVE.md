# Code Deep Dive: Integration Techniques

Stdlib only (math). Observed outputs in comments.

## 1. Differentiation-Back Checks

```python
import math
h = 1e-5
def central(f, x): return (f(x+h) - f(x-h))/(2*h)
print(central(lambda x: math.exp(x*x), 0.7))  # observed 2.2852427082331594 (analytic 2.28524270793753)
print(central(lambda x: (x-1)*math.exp(x), 1.0))  # observed 2.7182818285976778 (analytic e = 2.718281828459045)
print(central(lambda x: x/2 - math.sin(2*x)/4, 1.0))  # observed 0.7080734182596248 (analytic sin^2(1) = 0.7080734182735712)
```

## 2. Definite Values vs Numeric Sums

```python
import math
print(math.e - 1)              # observed 1.718281828459045 = int_0^1 2x e^{x^2} dx
print(math.exp(2) + 1)         # observed 8.38905609893065 = int_0^2 x e^x dx
print(2*math.log(2) - math.log(3))  # observed 0.2876820724517808 = partial-fractions integral
print(math.pi/4)               # observed 0.7853981633974483 = int_0^1 dx/(1+x^2)
def midpoint(f, a, b, n):
    dx = (b-a)/n
    return sum(f(a+(i+0.5)*dx) for i in range(n))*dx
print(midpoint(lambda x: 1/(1+x*x), 0, 1, 1000))  # observed 0.7853981842307817 (pi/4 = 0.7853981633974483)
```

## 3. Split Identity Check

```python
x = 0.5
print(1/((x+1)*(x+2)), 1/(x+1) - 1/(x+2))  # observed 0.26666666666666666 0.2666666666666666
```

## 4. Improper Integral Converges to 1

```python
for R in [10, 100, 1000]:
    print(R, 1 - 1/R)  # observed 10 0.9 | 100 0.99 | 1000 0.999 -> int_1^infty 1/x^2 dx = 1
```
