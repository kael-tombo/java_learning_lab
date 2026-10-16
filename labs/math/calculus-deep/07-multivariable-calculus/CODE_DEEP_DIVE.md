# Code Deep Dive: Multivariable Calculus

Stdlib only (math). Observed outputs in comments.

## 1. Gradient and Directional Derivative

```python
import math
f = lambda x, y: x*x*y + 3*x*y*y
fx = lambda x, y: 2*x*y + 3*y*y
fy = lambda x, y: x*x + 6*x*y
print(f(2,1), fx(2,1), fy(2,1))  # observed 10 7 16
print(math.sqrt(49+256))        # observed 17.46424919657298 = |grad|
print((7*3 + 16*4)/5)           # observed 17.0 = directional derivative along (3/5,4/5)
```

## 2. Tangent Plane vs True Value

```python
print(10 + 7*0.01 + 16*0.02)  # observed 10.39 = plane prediction at (2.01,1.02)
print(f(2.01, 1.02))           # observed 10.394513999999997 = true value
h = 1e-5
print((f(2+h,1)-f(2-h,1))/(2*h))  # observed 7.0000000000902665 confirms fx = 7
```

## 3. Minimum Search and Fubini Check

```python
g = lambda x, y: x*x + y*y - 4*x - 2*y + 5
print(g(2,1))  # observed 0
print(min(g(2+dx,1+dy) for dx in [-0.1,0,0.1] for dy in [-0.1,0,0.1]))  # observed 0: grid min at (2,1)
def midpoint2(n):
    s = 0.0
    for i in range(n):
        for j in range(n):
            x = (i+0.5)/n*2; y = (j+0.5)/n
            s += (x + 2*y)
    return s/n/n*2*1
print(midpoint2(200))  # observed 4.0: double Riemann sum equals the iterated value 4
```
