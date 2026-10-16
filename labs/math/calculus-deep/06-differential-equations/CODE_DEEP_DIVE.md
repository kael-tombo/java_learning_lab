# Code Deep Dive: Differential Equations

Stdlib only (math). Observed outputs in comments.

## 1. Residual Checks (Substitution Verification)

```python
import math
print(3*math.exp(2))                    # observed 22.16716829679195 = growth y(1)
print(math.log(2)/2)                    # observed 0.34657359027997264 = doubling time
print(math.sqrt(13))                    # observed 3.605551275463989 = separable y(3)
print(math.sqrt(13)*(3/math.sqrt(13))-3) # observed 0.0 = yy' - x residual
y = lambda t: 3 - 2*math.exp(-2*t)
yp = lambda t: 4*math.exp(-2*t)
print(y(0), y(1))                       # observed 1.0 2.7293294335267744
print(yp(0.5) + 2*y(0.5) - 6)           # observed 0.0 = linear ODE residual
```

## 2. Euler Iteration

```python
import math
yh = 1.0
for i in range(10):
    yh += 0.1*yh
print(yh, math.e)  # observed 2.5937424601 2.718281828459045
print(1.1**10)     # observed 2.5937424601: iteration equals (1+h)^n exactly
```

## 3. Logistic Climb Toward y = 10

```python
z = 2.0
for i in range(50):
    z += 0.1*z*(1 - z/10)
print(z)  # observed 9.761170243292469; monotone rise toward the stable equilibrium 10
```
