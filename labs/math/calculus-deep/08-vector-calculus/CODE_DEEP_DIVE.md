# Code Deep Dive: Vector Calculus

Stdlib only (math). Observed outputs in comments.

## 1. Div/Curl at Points

```python
print(2*1 + 2*2 + 2*3)  # observed 12 = div(x^2,y^2,z^2) at (1,2,3)
print(0 - 0, 0 - 0, 0 - 0)  # observed 0 0 0 = its curl components
print(0 - 0, 0 - 0, 1 + 1)  # observed 0 0 2 = curl(-y,x,0)
```

## 2. Line Integral: Closed Form vs Sum

```python
n = 100000
s = 0.0
for i in range(n):
    t = (i+0.5)/n
    s += 3*t*t/n
print(s)  # observed 0.9999999999750026 (exact 1)
```

## 3. Green and Gauss Spot-Checks

```python
import math
print(2*math.pi)  # observed 6.283185307179586 = unit-circle circulation of (-y,x)
print(2*math.pi*1**2)  # observed 6.283185307179586 = Green side: 2 * area
print(4*math.pi)  # observed 12.566370614359172 = flux of (x,y,z) through unit sphere
print(4/3*math.pi)  # observed 4.1887902047863905 = unit-ball volume
```

## 4. Path Independence

```python
# phi = x^2+y^2: axes path 1+1, diagonal int_0^1 4t dt
print(1 + 1, 4*0.5)  # observed 2 2.0: both paths give phi(1,1)-phi(0,0)
```
