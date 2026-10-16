# Code Deep Dive: Derivative Rules

Stdlib only (math). Observed outputs in comments; h = 1e-5 central
differences throughout.

## 1. Central-Difference Harness

```python
import math
def central(f, x, h=1e-5):
    return (f(x+h) - f(x-h)) / (2*h)
print(central(lambda t: t*t*math.exp(t), 2.0))  # observed 59.112448794529364 (exact 59.1124487914452)
print(central(lambda t: math.log(t*t+1), 2.0))  # observed 0.8000000000008 (exact 0.8)
print(central(lambda t: (t**3+1)/(t-1), 2.0))   # observed 2.9999999998864264 (exact 3)
```

## 2. Exact Formulas vs Numeric

```python
import math
print(math.exp(2)*8)        # observed 59.1124487914452 = e^2(2x+x^2) at x=2
print(4/5)                  # observed 0.8 = 2x/(x^2+1) at x=2
print(3*math.sin(3.0))      # observed 0.4233600241796016 = 3 sin(6x) at x=0.5
print(central(lambda t: math.sin(3*t)**2, 0.5))  # observed 0.42336002392673316
```

## 3. Tangent Line Check

```python
# f(x)=(x^3+1)/(x-1): f(2)=9, f'(2)=3, so f(2.001) ~= 9.003
q = lambda t: (t**3+1)/(t-1)
print(q(2.001), 9 + 3*0.001)  # observed 9.003002998001996 vs 9.003: linear error O(h^2)
```

## 4. MVT Point Search

```python
# x^2 on [1,3]: secant 4.0; scan f'(x)=2x for match
print((9-1)/(3-1))  # observed 4.0; c=2.0 gives f'(c)=4.0 exactly
```
