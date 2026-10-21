# Numerical Methods: A Comprehensive Treatment

## 1. Numerical Integration

### 1.1 Riemann Sums
The simplest numerical integration: ∫_a^b f(x)dx ≈ Σ f(xᵢ)Δx. Left, right, and midpoint rules give O(1/n) accuracy.

### 1.2 Trapezoidal Rule
∫_a^b f(x)dx ≈ h/2 · [f(a) + 2Σ f(a+ih) + f(b)]

Error: O(h²), requires function to be C².

### 1.3 Simpson's Rule
∫_a^b f(x)dx ≈ h/3 · [f(a) + 4Σ_{odd} f(a+ih) + 2Σ_{even} f(a+ih) + f(b)]

Error: O(h⁴), exact for polynomials up to degree 3.

### 1.4 Romberg Integration
Extrapolation technique combining trapezoidal rules at different step sizes. Uses Richardson extrapolation to achieve high-order accuracy.

### 1.5 Gaussian Quadrature
Optimal quadrature rules that achieve degree 2n-1 precision with n points. Gauss-Legendre uses Legendre polynomial roots.

### 1.6 Adaptive Quadrature
Subdivide integration interval based on local error estimates. More efficient for functions with varying behavior.

## 2. Root Finding

### 2.1 Bisection Method
Guaranteed convergence for continuous functions with sign change. Linear convergence rate, one bit per iteration.

### 2.2 Newton-Raphson Method
x_{k+1} = x_k - f(x_k)/f'(x_k). Quadratic convergence but requires derivative. May diverge for poor initial guesses.

### 2.3 Secant Method
Approximates derivative using finite differences:
x_{k+1} = x_k - f(x_k)(x_k - x_{k-1})/(f(x_k) - f(x_{k-1}))

Superlinear convergence (order φ ≈ 1.618), no derivative needed.

### 2.4 False Position (Regula Falsi)
Combines bisection and secant: maintains sign change bracket while using secant formula. Guaranteed convergence but may be slow.

### 2.5 Brent's Method
Hybrid method combining bisection, secant, and inverse quadratic interpolation. Guaranteed convergence with superlinear rate.

## 3. Interpolation

### 3.1 Lagrange Interpolation
p(x) = Σ yᵢ · ℓᵢ(x) where ℓᵢ(x) = Π_{j≠i} (x - xⱼ)/(xᵢ - xⱼ)

O(n²) to evaluate, numerically unstable for many points.

### 3.2 Newton's Divided Differences
p(x) = c₀ + c₁(x-x₀) + c₂(x-x₀)(x-x₁) + ... + cₙ(x-x₀)...(x-x_{n-1})

Efficient O(n²) construction, O(n) evaluation. Easy to add new points.

### 3.3 Spline Interpolation
Piecewise low-degree polynomials with smoothness constraints.
- Cubic splines: C² continuous, natural or clamped boundary conditions
- B-splines: basis functions for stable computation
- Clamped splines: specified derivative at endpoints

### 3.4 Runge's Phenomenon
High-degree polynomial interpolation on equispaced points oscillates near boundaries. Remedy: use Chebyshev nodes or splines.

## 4. ODE Solvers

### 4.1 Euler's Method
y_{k+1} = y_k + h · f(t_k, y_k). Simple but O(h) error. Stiff equations require tiny steps.

### 4.2 Heun's Method (Improved Euler)
y_{k+1} = y_k + h/2 · [f(t_k, y_k) + f(t_{k+1}, y_k + h·f(t_k, y_k))]

O(h²) accuracy, better stability than Euler.

### 4.3 Runge-Kutta Methods
RK4: Classical fourth-order method
k₁ = f(tₖ, yₖ)
k₂ = f(tₖ + h/2, yₖ + h·k₁/2)
k₃ = f(tₖ + h/2, yₖ + h·k₂/2)
k₄ = f(tₖ + h, yₖ + h·k₃)
y_{k+1} = yₖ + h/6 · (k₁ + 2k₂ + 2k₃ + k₄)

O(h⁴) accuracy.

### 4.4 Adaptive Step Size Methods
- Runge-Kutta-Fehlberg (RKF45): 4th/5th order pair for error estimation
- Dormand-Prince (DP54): Used in MATLAB's ode45
- Adjust step size to maintain local error within tolerance

### 4.5 Stiff Solvers
- Backward Euler (implicit): A-stable for stiff problems
- BDF methods: Backward Differentiation Formulas
- Implicit Runge-Kutta: Fully implicit for maximum stability

## 5. Finite Differences

### 5.1 First Derivatives
- Forward: f'(x) ≈ [f(x+h) - f(x)]/h, O(h)
- Backward: f'(x) ≈ [f(x) - f(x-h)]/h, O(h)
- Central: f'(x) ≈ [f(x+h) - f(x-h)]/(2h), O(h²)

### 5.2 Second Derivatives
f''(x) ≈ [f(x+h) - 2f(x) + f(x-h)]/h², O(h²)

### 5.3 Higher-Order Derivatives
Use larger stencils for O(h⁴) accuracy:
f'(x) ≈ [-f(x+2h) + 8f(x+h) - 8f(x-h) + f(x-2h)]/(12h)

### 5.4 Partial Differential Equations
- Laplace equation: ∇²u = 0 (elliptic)
- Heat equation: u_t = αu_xx (parabolic)
- Wave equation: u_tt = c²u_xx (hyperbolic)

## 6. Error Analysis

### 6.1 Truncation Error
Error from approximation (e.g., replacing derivative with finite difference).

### 6.2 Roundoff Error
Error from finite precision arithmetic. Limiting factor for extremely small h.

### 6.3 Convergence
Method converges if error → 0 as h → 0.

### 6.4 Stability
Small perturbations in input produce bounded perturbations in output.

## 7. Condition Number and Well-Posedness

- Well-conditioned: small input changes = small output changes
- Ill-conditioned: small input changes = large output changes
- Condition number κ = ||J|| · ||x||/||f(x)|| where J is Jacobian

## 8. Advanced Topics

- Spectral methods: global basis functions for smooth problems
- Finite element method (FEM): variational formulation for PDEs
- Multigrid methods: efficient solvers for elliptic PDEs
- Monte Carlo methods: integration in high dimensions
- Fast Fourier Transform (FFT): for spectral derivatives
- Krylov subspace methods: GMRES, Conjugate Gradient for linear systems
