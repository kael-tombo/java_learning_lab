# Optimization Theory — Exercises (5 Problems with Hints)

---

## Problem 1: Gradient Descent with Backtracking Line Search

**Implement gradient descent with Armijo backtracking for the Rosenbrock function:**
$$f(x,y) = 100(y - x^2)^2 + (1 - x)^2$$

**Starting at $(x_0, y_0) = (-1.2, 1)$, use $\alpha_0 = 1$, $\beta = 0.5$, $c = 10^{-4}$. Track iterates until $\|\nabla f\| < 10^{-6}$.**

### Requirements:
- Compute gradient analytically: $\nabla f = [-400x(y-x^2) - 2(1-x), 200(y-x^2)]^T$
- Implement backtracking: while $f(x - \alpha \nabla f) > f(x) - c \alpha \|\nabla f\|^2$, $\alpha \leftarrow \beta \alpha$
- Output: iteration, $(x,y)$, $f$, $\|\nabla f\|$, $\alpha$ accepted
- Plot convergence path on contour plot (optional)

### Hints:
1. **Global minimum:** $(1,1)$ with $f=0$.
2. **Rosenbrock is non-convex** but has a unique global minimum; gradient descent may need many iterations (~1000+).
3. **Backtracking parameters:** $c=10^{-4}$ is standard; $\beta=0.5$ halves step each rejection.
4. **Expected iterations:** ~50-100 with good line search; much more with fixed small step.

### Extension:
- Compare with fixed step size $\alpha = 0.001$ (slow) vs $\alpha = 0.01$ (may diverge).
- Implement Wolfe conditions (sufficient decrease + curvature).

---

## Problem 2: Newton's Method with Damping

**Apply Newton's method to minimize $f(x) = \log(1 + e^{x_1}) + \log(1 + e^{x_2}) + \frac{1}{2}(x_1^2 + x_2^2)$ (logistic loss + L2 regularization). Compare pure Newton vs. damped Newton with backtracking.**

### Requirements:
- Compute gradient and Hessian analytically
- Pure Newton: $x_{k+1} = x_k - H^{-1} g$
- Damped Newton: backtracking line search on Newton step
- Start at $x_0 = (10, -10)$
- Print iterations, $f$, $\|g\|$, step size

### Hints:
1. **Gradient:** $g_i = \frac{e^{x_i}}{1+e^{x_i}} + x_i = \sigma(x_i) + x_i$ where $\sigma$ is sigmoid.
2. **Hessian:** Diagonal! $H_{ii} = \sigma(x_i)(1-\sigma(x_i)) + 1$ (always $\geq 1$).
3. **Pure Newton** should converge in ~5-10 iterations (quadratic near optimum).
4. **Damped Newton** needed far from optimum where Newton step may overshoot.
5. **Optimum:** Near $(0,0)$ since regularization pulls to origin.

### Extension:
- Add off-diagonal terms to make Hessian non-diagonal.
- Compare with BFGS quasi-Newton.

---

## Problem 3: Constrained QP with KKT

**Solve the box-constrained QP:**
$$\min_{x \in \mathbb{R}^2} \frac{1}{2}x^T Q x + c^T x \quad \text{s.t.} \quad 0 \leq x_1 \leq 1, \; 0 \leq x_2 \leq 2$$
with $Q = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}$, $c = \begin{bmatrix} -2 \\ -4 \end{bmatrix}$.

**Solve analytically using KKT conditions, then implement projected gradient descent to verify.**

### Requirements:
- Enumerate active constraint combinations (4 box constraints = 16 cases)
- For each case, solve KKT system; check feasibility
- Implement projected gradient: $x_{k+1} = \Pi_{[0,1]\times[0,2]}(x_k - \alpha (Qx_k + c))$
- Compare solutions

### Hints:
1. **Unconstrained optimum:** $x^* = -Q^{-1}c = \begin{bmatrix} 0 \\ 2 \end{bmatrix}$.
2. **Check feasibility:** $x^* = (0, 2)$ satisfies $0 \leq 0 \leq 1$, $0 \leq 2 \leq 2$ — on boundary!
3. **KKT for active constraints:** If $x_1=0$ active, multiplier $\lambda_1 \geq 0$ for $x_1 \geq 0$.
4. **Projected gradient step size:** $\alpha = 1/\lambda_{\max}(Q) = 1/3$ (since eig $Q$ are 3, 1).
5. **Expected:** PGD converges linearly to $(0, 2)$.

### Extension:
- Generalize to $n$ variables with random $Q \succ 0$ and box constraints.
- Implement active-set method for box constraints.

---

## Problem 4: Duality and SVM Formulation

**Derive the dual of the soft-margin SVM primal:**
$$\min_{w,b,\xi} \frac{1}{2}\|w\|^2 + C\sum_{i=1}^n \xi_i$$
$$\text{s.t. } y_i(w^T x_i + b) \geq 1 - \xi_i, \quad \xi_i \geq 0, \quad i=1,\ldots,n$$

**Then implement the dual QP solver for a small 2D dataset.**

### Requirements:
- Form Lagrangian with multipliers $\alpha_i \geq 0$ (margin) and $\mu_i \geq 0$ (slack)
- Derive dual: $\max_{\alpha} \sum \alpha_i - \frac{1}{2}\sum_{i,j} \alpha_i \alpha_j y_i y_j x_i^T x_j$
- Constraints: $0 \leq \alpha_i \leq C$, $\sum \alpha_i y_i = 0$
- Implement for 2D data: 4 points: $(1,1): +1$, $(2,2): +1$, $(-1,-1): -1$, $(-2,-2): -1$
- Use simple coordinate ascent (SMO-like) or CVXOPT-style solver

### Hints:
1. **Lagrangian:** $L = \frac{1}{2}\|w\|^2 + C\sum \xi_i - \sum \alpha_i[y_i(w^T x_i+b)-1+\xi_i] - \sum \mu_i \xi_i$.
2. **Stationarity:** $\frac{\partial L}{\partial w} = 0 \implies w = \sum \alpha_i y_i x_i$; $\frac{\partial L}{\partial b} = 0 \implies \sum \alpha_i y_i = 0$; $\frac{\partial L}{\partial \xi_i} = 0 \implies \alpha_i + \mu_i = C \implies 0 \leq \alpha_i \leq C$.
3. **Dual objective:** Substitute $w$: $\sum \alpha_i - \frac{1}{2}\sum \alpha_i \alpha_j y_i y_j x_i^T x_j$.
4. **Simple dataset:** Linearly separable with margin; expect $\alpha_i > 0$ for support vectors.
5. **Coordinate ascent:** Update one $\alpha_i$ at a time maintaining $\sum \alpha_i y_i = 0$.

### Extension:
- Add kernel trick (RBF kernel).
- Compare with libsvm on larger dataset.

---

## Problem 5: Conjugate Gradient for Linear System

**Implement Conjugate Gradient to solve $Ax = b$ where $A \in \mathbb{R}^{100 \times 100}$ is symmetric positive definite. Generate $A = Q^T Q + 0.1 I$ with random $Q$, and $b = A x_{true}$ with known $x_{true}$. Compare CG iterations vs. residual norm.**

### Requirements:
- CG algorithm for linear systems (equivalent to minimizing $f(x) = \frac{1}{2}x^T A x - b^T x$)
- Track $\|r_k\| = \|b - Ax_k\|$ at each iteration
- Stop when $\|r_k\| < 10^{-10} \|b\|$
- Compare with steepest descent (gradient descent on $f$)
- Plot convergence: $\log \|r_k\|$ vs. $k$

### Hints:
1. **CG for linear systems:**
   - $r_0 = b - Ax_0$, $p_0 = r_0$
   - $\alpha_k = \frac{r_k^T r_k}{p_k^T A p_k}$
   - $x_{k+1} = x_k + \alpha_k p_k$
   - $r_{k+1} = r_k - \alpha_k A p_k$
   - $\beta_k = \frac{r_{k+1}^T r_{k+1}}{r_k^T r_k}$
   - $p_{k+1} = r_{k+1} + \beta_k p_k$
2. **Exact convergence:** CG solves in at most $n=100$ steps (often much fewer).
3. **Condition number:** $\kappa(A) \approx$ ratio of max/min eigenvalues of $Q^T Q + 0.1I$.
4. **Steepest descent:** $x_{k+1} = x_k + \frac{r_k^T r_k}{r_k^T A r_k} r_k$; much slower (linear rate $\frac{\kappa-1}{\kappa+1}$).

### Extension:
- Add preconditioning (diagonal/Jacobi or incomplete Cholesky).
- Test on 2D Poisson matrix (5-point stencil, $A$ sparse).

---

*End of Exercises*