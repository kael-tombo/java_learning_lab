# Calculus Theory

## 1. Limits
A limit describes the value a function approaches as its input approaches some point.

**Formal definition (epsilon-delta):**
lim(x→a) f(x) = L means: for every ε > 0, there exists δ > 0 such that
0 < |x - a| < δ implies |f(x) - L| < ε.

**Key limit laws:**
- Sum: lim[f + g] = lim f + lim g
- Product: lim[f · g] = lim f · lim g
- Quotient: lim[f/g] = lim f / lim g (if lim g ≠ 0)
- Chain: lim f(g(x)) = f(lim g(x)) when f is continuous

**Special limits:**
- lim(x→0) sin(x)/x = 1
- lim(x→∞) (1 + 1/x)^x = e
- lim(x→0) (e^x - 1)/x = 1

**L'Hôpital's Rule:** If lim f/g yields 0/0 or ∞/∞, then
lim f/g = lim f'/g' (provided the latter limit exists).

## 2. Derivatives
The derivative measures instantaneous rate of change.

**Definition:** f'(x) = lim(h→0) [f(x+h) - f(x)]/h

**Differentiation rules:**
- Power: d/dx[x^n] = n·x^(n-1)
- Product: (fg)' = f'g + fg'
- Quotient: (f/g)' = (f'g - fg')/g²
- Chain: d/dx[f(g(x))] = f'(g(x))·g'(x)

**Common derivatives:**
- d/dx[sin x] = cos x
- d/dx[cos x] = -sin x
- d/dx[e^x] = e^x
- d/dx[ln x] = 1/x

**Applications:**
- Velocity: v(t) = s'(t)
- Acceleration: a(t) = v'(t) = s''(t)
- Optimization: critical points where f'(x) = 0
- Related rates: chain rule across variables

## 3. Integrals
Integration accumulates quantities; it is the reverse of differentiation.

**Indefinite integral:** ∫f(x)dx = F(x) + C where F'(x) = f(x)

**Definite integral:** ∫[a,b] f(x)dx = F(b) - F(a) (Fundamental Theorem)

**Integration techniques:**
- Substitution: ∫f(g(x))g'(x)dx = ∫f(u)du
- Integration by parts: ∫u dv = uv - ∫v du
- Partial fractions: decompose rational functions
- Trig substitution: for √(a²-x²), √(a²+x²), √(x²-a²)

**Applications:**
- Area under curves
- Volume of revolution (disk/washer methods)
- Arc length: ∫√(1 + [f'(x)]²)dx
- Work: ∫F(x)dx

## 4. Infinite Series
A series sums infinitely many terms.

**Convergence tests:**
- Divergence test: if lim a_n ≠ 0, series diverges
- Geometric: Σar^n converges iff |r| < 1, sum = a/(1-r)
- p-series: Σ1/n^p converges iff p > 1
- Comparison test: compare to known series
- Ratio test: lim|a_(n+1)/a_n| < 1 implies convergence
- Alternating series test: decreasing terms → 0 implies convergence

**Taylor series:** f(x) = Σ f^(n)(a)/n! · (x-a)^n
- e^x = Σ x^n/n!
- sin x = Σ (-1)^n x^(2n+1)/(2n+1)!
- cos x = Σ (-1)^n x^(2n)/(2n)!

**Power series:** variable-centered series with radius of convergence.

## 5. Multivariable Extensions
- Partial derivatives: ∂f/∂x holds other variables constant
- Gradient: ∇f points in direction of steepest ascent
- Double integrals: ∫∫f(x,y)dA for area/volume
- Line integrals: integrate along curves
