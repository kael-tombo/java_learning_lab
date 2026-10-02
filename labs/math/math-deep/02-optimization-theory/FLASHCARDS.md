# Optimization Theory — Flashcards

---

## Convexity

### Convex Sets
**Q:** Definition of convex set?
**A:** $S$ is convex if $\forall x,y \in S, \forall t \in [0,1]: tx + (1-t)y \in S$.

**Q:** Intersection of convex sets?
**A:** Always convex.

**Q:** Convex hull?
**A:** Smallest convex set containing a given set; set of all convex combinations.

---

### Convex Functions
**Q:** Definition of convex function?
**A:** $f(tx + (1-t)y) \leq tf(x) + (1-t)f(y)$ for all $x,y \in \text{dom}(f), t \in [0,1]$.

**Q:** First-order condition (differentiable)?
**A:** $f(y) \geq f(x) + \nabla f(x)^T(y-x)$ for all $x,y$.

**Q:** Second-order condition (twice differentiable)?
**A:** $\nabla^2 f(x) \succeq 0$ for all $x \in \text{dom}(f)$.

**Q:** Strict convexity?
**A:** $f(tx + (1-t)y) < tf(x) + (1-t)f(y)$ for $x \neq y, t \in (0,1)$; equivalent to $\nabla^2 f(x) \succ 0$.

**Q:** Strong convexity?
**A:** $f(x) - \frac{m}{2}\|x\|^2$ is convex for some $m > 0$; $\nabla^2 f(x) \succeq m I$.

---

### Operations Preserving Convexity
**Q:** Nonnegative weighted sum?
**A:** $\sum \alpha_i f_i$ convex if $\alpha_i \geq 0$ and $f_i$ convex.

**Q:** Affine composition?
**A:** $f(Ax+b)$ convex if $f$ convex.

**Q:** Pointwise maximum?
**A:** $\max_i f_i(x)$ convex if each $f_i$ convex.

**Q:** Perspective function?
**A:** $g(x,t) = t f(x/t)$ convex if $f$ convex.

---

## Unconstrained Optimization

### Optimality Conditions
**Q:** First-order necessary (stationary point)?
**A:** $\nabla f(x^*) = 0$.

**Q:** Second-order necessary (local minimum)?
**A:** $\nabla f(x^*) = 0$ and $\nabla^2 f(x^*) \succeq 0$.

**Q:** Second-order sufficient (strict local minimum)?
**A:** $\nabla f(x^*) = 0$ and $\nabla^2 f(x^*) \succ 0$.

**Q:** For convex functions?
**A:** $\nabla f(x^*) = 0$ is necessary and sufficient for global minimum.

---

### Gradient Descent
**Q:** Update rule?
**A:** $x_{k+1} = x_k - \alpha_k \nabla f(x_k)$.

**Q:** Fixed step size convergence (L-smooth, m-strongly convex)?
**A:** Linear rate: $\|x_k - x^*\| \leq \left(\frac{L-m}{L+m}\right)^k \|x_0 - x^*\|$ with $\alpha = \frac{2}{L+m}$.

**Q:** Optimal step for quadratic?
**A:** $\alpha^* = \frac{2}{\lambda_{\max} + \lambda_{\min}}$, rate $\frac{\kappa-1}{\kappa+1}$.

**Q:** Armijo backtracking?
**A:** Start with $\alpha_0$, reduce by $\beta \in (0,1)$ until $f(x - \alpha \nabla f) \leq f(x) - c \alpha \|\nabla f\|^2$ ($c \in (0,0.5)$).

**Q:** Wolfe conditions?
**A:** Sufficient decrease + curvature condition: $\nabla f(x_{new})^T p \geq c_2 \nabla f(x)^T p$.

---

### Newton's Method
**Q:** Update rule?
**A:** $x_{k+1} = x_k - [\nabla^2 f(x_k)]^{-1} \nabla f(x_k)$.

**Q:** Convergence near optimum?
**A:** Quadratic if $\nabla^2 f(x^*) \succ 0$ and $x_0$ close enough.

**Q:** Damped Newton?
**A:** $x_{k+1} = x_k - \alpha_k [\nabla^2 f(x_k)]^{-1} \nabla f(x_k)$ with line search.

**Q:** For quadratic?
**A:** Exact solution in 1 iteration (Hessian constant).

**Q:** Quasi-Newton (BFGS)?
**A:** Approximate Hessian inverse $H_k$ updated using $s_k = x_{k+1}-x_k$, $y_k = \nabla f_{k+1} - \nabla f_k$.

---

### Conjugate Gradient
**Q:** For quadratic $f(x) = \frac{1}{2}x^T Q x - b^T x$?
**A:** Generates $Q$-conjugate directions $p_i^T Q p_j = 0$ for $i \neq j$.

**Q:** Convergence?
**A:** Exact in at most $n$ iterations for $n \times n$ SPD $Q$; typically much faster.

**Q:** No line search needed?
**A:** For exact quadratic, step size $\alpha_k = \frac{r_k^T r_k}{p_k^T Q p_k}$ with residual $r_k = Qx_k - b$.

**Q:** Nonlinear CG?
**A:** Polak-Ribière: $\beta_k = \frac{r_{k+1}^T (r_{k+1} - r_k)}{\|r_k\|^2}$; Fletcher-Reeves: $\beta_k = \frac{\|r_{k+1}\|^2}{\|r_k\|^2}$.

---

## Constrained Optimization

### Equality Constraints
**Q:** Lagrangian for $\min f(x)$ s.t. $h(x) = 0$?
**A:** $L(x, \nu) = f(x) + \nu^T h(x)$.

**Q:** KKT conditions (equality only)?
**A:** $\nabla_x L = 0$, $h(x) = 0$.

**Q:** Lagrange multiplier meaning?
**A:** $\nu_i = \frac{\partial p^*}{\partial b_i}$ — sensitivity of optimal value to constraint RHS.

---

### Inequality Constraints
**Q:** Lagrangian for $\min f(x)$ s.t. $g(x) \leq 0, h(x) = 0$?
**A:** $L(x, \lambda, \nu) = f(x) + \lambda^T g(x) + \nu^T h(x)$.

**Q:** KKT conditions?
**A:**
1. Stationarity: $\nabla f + \sum \lambda_i \nabla g_i + \sum \nu_i \nabla h_i = 0$
2. Primal feasibility: $g(x) \leq 0, h(x) = 0$
3. Dual feasibility: $\lambda \geq 0$
4. Complementary slackness: $\lambda_i g_i(x) = 0$

**Q:** Complementary slackness meaning?
**A:** For each inequality: either $\lambda_i = 0$ (inactive) or $g_i(x) = 0$ (active/binding).

**Q:** Constraint qualification?
**A:** Regularity condition for KKT to be necessary (e.g., LICQ, Slater's condition).

**Q:** Slater's condition?
**A:** $\exists x$ strictly feasible: $g(x) < 0, h(x) = 0$ (for convex problems).

---

### Duality
**Q:** Dual function?
**A:** $g(\lambda, \nu) = \inf_x L(x, \lambda, \nu)$.

**Q:** Dual problem?
**A:** $\max_{\lambda \geq 0, \nu} g(\lambda, \nu)$.

**Q:** Weak duality?
**A:** $d^* \leq p^*$ always (dual opt $\leq$ primal opt).

**Q:** Strong duality?
**A:** $d^* = p^*$; holds for convex problems with Slater's condition.

**Q:** Duality gap?
**A:** $p^* - d^* \geq 0$; zero at optimum if strong duality holds.

**Q:** Complementary slackness in duality?
**A:** $\lambda_i^* g_i(x^*) = 0$ at optimal primal/dual pair.

---

### Special Problems
**Q:** Linear programming duality?
**A:** Primal: $\min c^T x$ s.t. $Ax \geq b, x \geq 0$; Dual: $\max b^T y$ s.t. $A^T y \leq c, y \geq 0$.

**Q:** Quadratic programming?
**A:** $\min \frac{1}{2}x^T Q x + c^T x$ s.t. $Ax \leq b$; KKT gives linear system.

**Q:** Projection onto convex set?
**A:** $\Pi_C(x) = \arg\min_{y \in C} \|y - x\|$; firmly nonexpansive.

**Q:** Projected gradient descent?
**A:** $x_{k+1} = \Pi_C(x_k - \alpha \nabla f(x_k))$; converges for convex $f$, $C$.

---

## Algorithms Summary

| Algorithm | Convergence | Per Iteration | Best For |
|-----------|-------------|---------------|----------|
| Gradient Descent | Linear ($O(1/k)$) | $O(n)$ | Large scale, simple |
| Newton | Quadratic | $O(n^3)$ | Small/medium, high accuracy |
| Quasi-Newton (BFGS) | Superlinear | $O(n^2)$ | Medium, no Hessian |
| Conjugate Gradient | Linear (quadratic exact in n) | $O(n^2)$ or $O(n)$ | Large sparse quadratic |
| Projected Gradient | Sublinear | $O(n) + \text{proj}$ | Simple constraints |
| Interior Point | Polynomial | $O(n^3)$ | LP/QP/SDP, high accuracy |

---

*End of Flashcards*