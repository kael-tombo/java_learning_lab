# Code Deep Dive: Derivative Applications

Stdlib only (math). Observed outputs in comments.

## 1. Critical Points and Classification

```python
f = lambda x: x**3 - 3*x**2 - 9*x + 5
fp = lambda x: 3*x**2 - 6*x - 9
f2 = lambda x: 6*x - 6
print(f(-1), f(3))        # observed 10 -22
print(f2(-1), f2(3))      # observed -12 12  -> max at -1, min at 3
print([fp(x/10) for x in [-11, 0, 31]])  # observed [1.23, -9.0, 1.23]: +, -, + chart
```

## 2. Box Volume Scan (EVT Comparison)

```python
V = lambda x: x*(12-2*x)**2
for x in [0, 1.5, 2.0, 2.5, 6.0]:
    print(x, V(x))
# observed: 0 0 | 1.5 121.5 | 2.0 128 | 2.5 122.5 | 6.0 0
print(24*2-96)  # observed -48 = V''(2) < 0 confirms local max
```

## 3. Related Rates

```python
import math
print(4*math.pi*25*2)  # observed 628.3185307179587 = 200*pi
```

## 4. Linear Approximation Error

```python
import math
print(math.sqrt(26), 5.1, 5.1 - math.sqrt(26))  # observed 5.0990195135927845 5.1 0.0009804864072155
print(1/500)  # observed 0.002 -> bound (M/2)h^2 = 0.001 covers the error
```
