# Mathematical Optimization: A Comprehensive Treatment

## 1. Fundamentals of Optimization

### 1.1 Problem Formulation
An optimization problem seeks to minimize (or maximize) an objective function f(x) subject to constraints gᵢ(x) ≤ 0, hⱼ(x) = 0.

### 1.2 Types of Optimization
- **Unconstrained**: No constraints on variables
- **Constrained**: Subject to equality/inequality constraints
- **Convex**: Both objective and feasible set are convex
- **Non-convex**: Multiple local optima possible
- **Continuous**: Variables are real numbers
- **Discrete**: Variables are integers or categorical

### 1.3 Optimality Conditions
- First-order necessary: ∇f(x*) = 0 (unconstrained)
- Second-order necessary: ∇²f(x*) is positive semidefinite
- KKT conditions for constrained problems

## 2. Gradient Descent and Variants

### 2.1 Vanilla Gradient Descent
x_{k+1} = x_k - α ∇f(x_k)

The learning rate α controls step size. Too large causes divergence; too small causes slow convergence.

### 2.2 Momentum
v_{k+1} = βv_k + α∇f(x_k)
x_{k+1} = x_k - v_{k+1}

Accumulates gradient history to accelerate convergence in consistent directions.

### 2.3 Nesterov Accelerated Gradient
v_{k+1} = βv_k + α∇f(x_k - βv_k)
x_{k+1} = x_k - v_{k+1}

Looks ahead by computing gradient at the extrapolated point.

### 2.4 AdaGrad
Adapts learning rate per parameter based on historical gradient magnitudes. Performs well on sparse data.

### 2.5 Adam
Combines momentum with adaptive learning rates. Maintains both first and second moment estimates with bias correction.

## 3. Newton's Method

### 3.1 Optimization
x_{k+1} = x_k - [∇²f(x_k)]⁻¹ ∇f(x_k)

Quadratic convergence near the optimum, but requires computing the Hessian (O(n²) storage, O(n³) inversion).

### 3.2 Root Finding
Newton's method finds roots of f(x) = 0 via x_{k+1} = x_k - f(x_k)/f'(x_k).

### 3.3 Quasi-Newton Methods
Approximate the Hessian using gradient differences:
- BFGS: Broyden-Fletcher-Goldfarb-Shanno algorithm
- L-BFGS: Limited-memory BFGS for large problems

## 4. Lagrange Multipliers

### 4.1 Equality Constraints
For min f(x) subject to g(x) = 0, the Lagrangian is L(x, λ) = f(x) + λg(x).

The KKT conditions:
∇ₓL = 0 and ∂L/∂λ = 0

### 4.2 Inequality Constraints
For g(x) ≤ 0, complementary slackness: λ ≥ 0, λg(x) = 0

### 4.3 Duality
The dual problem provides a lower bound on the primal optimum. Strong duality holds for convex problems with Slater's condition.

## 5. Convex Optimization

### 5.1 Convex Sets and Functions
A function f is convex if f(θx + (1-θ)y) ≤ θf(x) + (1-θ)f(y) for θ ∈ [0,1].

### 5.2 Properties
- Every local minimum is global
- Subgradient methods apply
- Efficient interior-point methods exist

### 5.3 Applications
- Linear programming (LP)
- Quadratic programming (QP)
- Semidefinite programming (SDP)
- Second-order cone programming (SOCP)

## 6. Line Search Methods

### 6.1 Exact Line Search
Minimize φ(α) = f(x_k + αp_k) exactly.

### 6.2 Backtracking Line Search
Reduce α until sufficient decrease (Armijo condition) is satisfied.

### 6.3 Wolfe Conditions
Ensure both sufficient decrease and curvature conditions.

## 7. Conjugate Gradient Methods

For quadratic problems, conjugate gradient converges in n steps. Uses conjugate directions instead of steepest descent.

## 8. Constrained Optimization

### 8.1 Penalty Methods
Add penalty term for constraint violations: f(x) + ρ·Σ max(0, gᵢ(x))²

### 8.2 Augmented Lagrangian
Combines Lagrangian and penalty approaches for better conditioning.

### 8.3 Sequential Quadratic Programming (SQP)
Solves a sequence of quadratic approximations to the original problem.

## 9. Global Optimization

### 9.1 Simulated Annealing
Probabilistic hill-climbing that accepts worse solutions with decreasing probability.

### 9.2 Genetic Algorithms
Evolutionary approach using selection, crossover, and mutation.

### 9.3 Particle Swarm Optimization
Swarm intelligence based on social behavior models.

## 10. Convergence Analysis

- Gradient descent: O(1/k) for convex, O(c^k) for strongly convex
- Newton: O(c^(2^k)) quadratic convergence
- Adam: O(1/k) for convex objectives
- BFGS: Superlinear convergence under mild conditions
