# Calculus Code Deep Dive (Python)

## 1. Numerical Differentiation
```python
def derivative(f, x, h=1e-5):
    """Central difference approximation of f'(x)."""
    return (f(x + h) - f(x - h)) / (2 * h)

# Example: derivative of x^2 at x=3 should be ~6
print(derivative(lambda x: x**2, 3))  # 6.000000000006
```

**Why central difference?** Error is O(h²) vs O(h) for forward difference. The symmetric cancellation eliminates the first-order error term.

## 2. Symbolic Differentiation with SymPy
```python
from sympy import symbols, diff, sin, exp, integrate, series

x = symbols('x')
f = x**3 * sin(x)
print(diff(f, x))        # 3*x**2*sin(x) + x**3*cos(x)
print(integrate(f, x))   # -x**3*cos(x) + 3*x**2*sin(x) + 6*x*cos(x) - 6*sin(x)
```

## 3. Numerical Integration
```python
def simpson(f, a, b, n=1000):
    """Simpson's rule: O(h^4) accuracy."""
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        x = a + i * h
        total += (4 if i % 2 else 2) * f(x)
    return total * h / 3

# ∫[0,1] 4/(1+x²) dx = π
print(simpson(lambda x: 4/(1+x**2), 0, 1))  # 3.1415926535...
```

## 4. Limit Computation
```python
from sympy import limit, oo

print(limit((1 + 1/x)**x, x, oo))   # E (Euler's number)
print(limit(sin(x)/x, x, 0))         # 1
```

## 5. Taylor Series Approximation
```python
import math

def taylor_sin(x, terms=10):
    """Compute sin(x) via Maclaurin series."""
    result = 0.0
    for n in range(terms):
        sign = (-1)**n
        result += sign * x**(2*n + 1) / math.factorial(2*n + 1)
    return result

print(taylor_sin(math.pi/4))  # 0.7071067811865475
```

## 6. Gradient Descent (Optimization)
```python
def gradient_descent(f, df, x0, lr=0.01, epochs=1000):
    """Minimize f using gradient descent."""
    x = x0
    for _ in range(epochs):
        x = x - lr * df(x)
    return x

# Minimize f(x) = (x-3)^2, minimum at x=3
print(gradient_descent(lambda x: (x-3)**2, lambda x: 2*(x-3), x0=0))
```

## 7. Euler's Method for ODEs
```python
def euler(f, y0, t0, tn, steps):
    """Solve dy/dt = f(t, y) numerically."""
    dt = (tn - t0) / steps
    t, y = t0, y0
    for _ in range(steps):
        y += dt * f(t, y)
        t += dt
    return y

# dy/dt = y, y(0)=1 → y(t) = e^t
print(euler(lambda t, y: y, 1.0, 0, 1, 10000))  # ~2.718
```

## 8. Performance Tips
- Use NumPy vectorization for array-valued functions
- `scipy.integrate.quad` for production integration
- `scipy.misc.derivative` for robust numerical differentiation
- Cache factorial computations in series evaluations
- Use `numba.jit` for tight numerical loops
