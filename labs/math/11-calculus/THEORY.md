# Calculus: Limits, Derivatives, Integrals, and Series

## 1. Limits

### 1.1 Definition
lim(x→a) f(x) = L means f(x) approaches L as x approaches a

### 1.2 Types
- Two-sided: lim(x→a) f(x)
- One-sided: lim(x→a⁺) f(x) or lim(x→a⁻) f(x)
- Infinite: lim(x→∞) f(x) = ±∞ or finite

### 1.3 Properties
- lim(f + g) = lim f + lim g
- lim(cf) = c·lim f
- lim(fg) = lim f · lim g
- lim(f/g) = lim f / lim g (if limit ≠ 0)

## 2. Continuity

### 2.1 Definition
f is continuous at a if:
1. f(a) exists
2. lim(x→a) f(x) exists
3. lim(x→a) f(x) = f(a)

### 2.2 Types
- Removable discontinuity: hole
- Jump discontinuity
- Infinite discontinuity

## 3. Derivatives

### 3.1 Definition
f'(x) = lim(h→0) [f(x+h) - f(x)]/h

### 3.2 Rules
- Constant: (c)' = 0
- Power: (xⁿ)' = nxⁿ⁻¹
- Sum: (f+g)' = f' + g'
- Product: (fg)' = f'g + fg'
- Quotient: (f/g)' = (f'g - fg')/g²
- Chain: (f(g(x)))' = f'(g(x))·g'(x)

### 3.3 Applications
- Tangent line: y - f(a) = f'(a)(x - a)
- Related rates
- Optimization
- Motion: velocity = s'(t), acceleration = s''(t)

## 4. Integrals

### 4.1 Indefinite Integrals
- Antiderivative: F'(x) = f(x)
- ∫ f(x)dx = F(x) + C

### 4.2 Definite Integrals
- Area under curve from a to b
- ∫ₐᵇ f(x)dx = F(b) - F(a)

### 4.3 Techniques
- Substitution
- Integration by parts
- Partial fractions
- Trigonometric substitution

### 4.4 Applications
- Area between curves
- Volume (disk/washer, shell)
- Arc length
- Surface area

## 5. Sequences and Series

### 5.1 Sequences
- Convergence: lim(n→∞) aₙ = L
- Divergence: no limit

### 5.2 Series
- Geometric: Σarⁿ = a/(1-r) for |r|<1
- Harmonic: Σ 1/n diverges
- p-series: Σ 1/n^p converges if p>1

### 5.3 Power Series
- f(x) = Σ cₙ(x-a)ⁿ
- Radius of convergence
- Taylor series: f(x) = Σ f⁽ⁿ⁾(a)/n! · (x-a)ⁿ

## 6. Multivariable Calculus

### 6.1 Partial Derivatives
- ∂f/∂x, ∂f/∂y
- Gradient: ∇f = (∂f/∂x, ∂f/∂y)

### 6.2 Multiple Integrals
- ∬f(x,y)dA
- Change of variables / Jacobian

### 6.3 Vector Calculus
- Divergence: ∇·F
- Curl: ∇×F
- Line integrals
- Green's, Stokes', Divergence theorems

## Sourced field notes (fetched Oct 2026 — verify before citing)

- MIT OCW Scholar 18.01SC Single Variable Calculus (Fall 2010, Prof. David Jerison et al.) — https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010 — Unit 1 (differentiation: definition, basic rules) maps directly onto lab §3 derivative rules; work the secant/tangent worked examples before coding the difference quotient.
- MIT OCW Scholar 18.01SC Unit 2, Part B: Optimization, Related Rates and Newton's Method — https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/unit-2-applications-of-differentiation/part-b-optimization-related-rates-and-newtons-method/ — use its optimization problem sets to ground lab §3.3 (tangent line, related rates, optimization) exercises.
- MIT OCW Scholar 18.01SC Unit 3 (definite integral + Fundamental Theorems) and Unit 4 (integration techniques) — https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/unit-3-the-definite-integral-and-its-applications/ — mirrors lab §4 techniques (substitution, parts, partial fractions); attempt the Unit 3–4 problem sets alongside the lab's area/volume drills.
- MIT OCW Scholar 18.01SC Unit 5, Part B: Taylor Series — https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/unit-5-exploring-the-infinite/part-b-taylor-series/ — pairs with lab §5.3 power/Taylor series; check radius-of-convergence examples against the lab's geometric/p-series convergence exercises.