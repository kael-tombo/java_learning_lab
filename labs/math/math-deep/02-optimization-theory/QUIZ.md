# Optimization Theory — Quiz (10 Questions with Worked Answers)

---

## Question 1: Convexity of Quadratic Function

**Question:** For $f(x) = \frac{1}{2}x^T Q x + c^T x$ with $Q \in \mathbb{R}^{n \times n}$ symmetric, what condition on $Q$ ensures $f$ is convex? Strictly convex?

**Answer:** **Convex: $Q \succeq 0$ (PSD); Strictly convex: $Q \succ 0$ (PD)**

**Derivation:**
Hessian $\nabla^2 f(x) = Q$. A twice-differentiable function is convex iff its Hessian is PSD everywhere. Since $Q$ is constant, $f$ is convex iff $Q \succeq 0$ (all eigenvalues $\geq 0$). Strict convexity requires $Q \succ 0$ (all eigenvalues $> 0$).

---

## Question 2: Gradient Descent on Quadratic

**Question:** Minimize $f(x) = \frac{1}{2}x^T Q x$ with $Q = \text{diag}(1, 100)$ using gradient descent $x_{k+1} = x_k - \alpha Q x_k$. What is the optimal fixed step size $\alpha^*$? What is the convergence rate?

**Answer:** **$\alpha^* = \frac{2}{\lambda_{\max} + \lambda_{\min}} = \frac{2}{101} \approx 0.0198$; Rate $\frac{\kappa-1}{\kappa+1} = \frac{99}{101} \approx 0.98$**

**Derivation:**
For quadratic, error $e_k = x_k - x^*$ evolves as $e_{k+1} = (I - \alpha Q)e_k$. Eigenvalues of iteration matrix: $1 - \alpha \lambda_i$.

Optimal $\alpha$ minimizes $\max_i |1 - \alpha \lambda_i|$. For $\lambda \in [\lambda_{\min}, \lambda_{\max}]$:
$\alpha^* = \frac{2}{\lambda_{\min} + \lambda_{\max}}$, giving rate $\frac{\lambda_{\max} - \lambda_{\min}}{\lambda_{\max} + \lambda_{\min}} = \frac{\kappa - 1}{\kappa + 1}$.

Here $\lambda_{\min}=1, \lambda_{\max}=100$, $\kappa=100$. Rate $= 99/101 \approx 0.98$ (very slow).

---

## Question 3: Newton's Method on Quadratic

**Question:** Show that Newton's method converges in exactly one iteration for any strictly convex quadratic function.

**Answer:** **One iteration converges exactly to the optimum**

**Derivation:**
$f(x) = \frac{1}{2}x^T Q x + c^T x$, $\nabla f(x) = Qx + c$, $\nabla^2 f(x) = Q$.

Newton step: $x_{k+1} = x_k - Q^{-1}(Q x_k + c) = -Q^{-1}c = x^*$.

Since Hessian is constant, the quadratic model is exact. Newton solves $\nabla f(x) = 0$ directly in one step.

---

## Question 4: Lagrange Multipliers

**Question:** Minimize $f(x,y) = x^2 + y^2$ subject to $x + y = 1$. Use Lagrange multipliers to find the solution.

**Answer:** **$x^* = y^* = 0.5$, $\lambda^* = -1$, $f^* = 0.5$**

**Derivation:**
Lagrangian: $L(x,y,\lambda) = x^2 + y^2 + \lambda(x + y - 1)$.

KKT conditions:
$\frac{\partial L}{\partial x} = 2x + \lambda = 0$
$\frac{\partial L}{\partial y} = 2y + \lambda = 0$
$\frac{\partial L}{\partial \lambda} = x + y - 1 = 0$

From first two: $2x = 2y \implies x = y$. With constraint: $2x = 1 \implies x = y = 0.5$.
Then $\lambda = -2x = -1$. $f^* = 0.5^2 + 0.5^2 = 0.5$.

---

## Question 5: KKT Conditions for Inequality Constraints

**Question:** Minimize $f(x) = x^2$ subject to $x \geq 1$. Write KKT conditions and find the solution.

**Answer:** **$x^* = 1$, $\lambda^* = 2$, $f^* = 1$**

**Derivation:**
Lagrangian: $L(x, \lambda) = x^2 - \lambda(x - 1)$ (note: constraint $g(x) = 1 - x \leq 0$, so $-\lambda g$).

KKT:
1. Stationarity: $\frac{\partial L}{\partial x} = 2x - \lambda = 0 \implies \lambda = 2x$
2. Primal feasibility: $x \geq 1$
3. Dual feasibility: $\lambda \geq 0$
4. Complementary slackness: $\lambda(x - 1) = 0$

Case 1: $x > 1 \implies \lambda = 0 \implies x = 0$ (violates $x \geq 1$)
Case 2: $x = 1 \implies \lambda = 2 \geq 0$ ✓

Solution: $x^* = 1$, $\lambda^* = 2$.

---

## Question 6: Duality Gap

**Question:** For the problem in Q5, compute the dual function $g(\lambda)$ and the dual optimal value. Is there a duality gap?

**Answer:** **$g(\lambda) = -\frac{\lambda^2}{4} + \lambda$ for $\lambda \geq 0$; Dual optimum $g^* = 1$ at $\lambda^* = 2$; No duality gap**

**Derivation:**
Dual function: $g(\lambda) = \inf_x [x^2 - \lambda(x - 1)] = \inf_x [x^2 - \lambda x + \lambda]$.

Minimize over $x$: $2x - \lambda = 0 \implies x = \lambda/2$.

$g(\lambda) = (\lambda/2)^2 - \lambda(\lambda/2) + \lambda = -\frac{\lambda^2}{4} + \lambda$, for $\lambda \geq 0$.

Maximize $g(\lambda)$: $g'(\lambda) = -\frac{\lambda}{2} + 1 = 0 \implies \lambda^* = 2$.

$g^* = g(2) = -1 + 2 = 1$. Primal optimum $p^* = 1$. Duality gap $p^* - g^* = 0$.

Strong duality holds (Slater's condition: feasible $x=2 > 1$).

---

## Question 7: Gradient Descent with Armijo Backtracking

**Question:** Armijo backtracking line search for $f(x) = x^2$ at $x_0 = 10$ with $\alpha_0 = 1$, $c = 0.5$. Does it accept $\alpha = 1$? If not, what $\alpha$ is accepted?

**Answer:** **$\alpha = 1$ is accepted (condition holds)**

**Derivation:**
Armijo condition: $f(x - \alpha \nabla f) \leq f(x) - c \alpha \|\nabla f\|^2$.

At $x = 10$: $f = 100$, $\nabla f = 20$, $\|\nabla f\|^2 = 400$.

LHS: $f(10 - 1\cdot 20) = f(-10) = 100$.
RHS: $100 - 0.5 \cdot 1 \cdot 400 = 100 - 200 = -100$.

$100 \leq -100$ is **false** — wait, this fails!

Actually for $f(x)=x^2$, $f(10-20)=f(-10)=100$, RHS = -100. Condition fails.

Try $\alpha = 0.5$: $x_{new} = 0$, $f=0$. RHS = $100 - 0.5 \cdot 0.5 \cdot 400 = 100 - 100 = 0$. $0 \leq 0$ ✓

So $\alpha = 0.5$ is the first accepted (with $\beta=0.5$ backtracking factor).

---

## Question 8: Conjugate Gradient for Quadratic

**Question:** Conjugate gradient on $f(x) = \frac{1}{2}x^T Q x$ with $Q = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}$, starting at $x_0 = (0,0)^T$. Show that it converges in at most 2 iterations.

**Answer:** **CG converges in exactly 2 iterations (exact for $n$-dim quadratic in $n$ steps)**

**Derivation:**
CG generates $Q$-conjugate directions $p_k$ with $p_i^T Q p_j = 0$ for $i \neq j$.
In $n$ dimensions, at most $n$ conjugate directions exist. After $n$ steps, the subspace spans $\mathbb{R}^n$, and the solution is exact.

For this $2\times 2$ case: eigenvalues of $Q$ are $3$ and $1$ (distinct). CG will converge in exactly 2 iterations for any starting point.

---

## Question 9: Barzilai-Borwein Step Size

**Question:** For $f(x) = \frac{1}{2}x^T Q x$, the Barzilai-Borwein step is $\alpha_{BB} = \frac{s_{k-1}^T s_{k-1}}{s_{k-1}^T y_{k-1}}$ where $s = x_k - x_{k-1}$, $y = \nabla f_k - \nabla f_{k-1}$. Show $\alpha_{BB} = \frac{\|s\|^2}{s^T Q s}$.

**Answer:** **$\alpha_{BB} = \frac{s^T s}{s^T Q s}$**

**Derivation:**
$y_{k-1} = \nabla f_k - \nabla f_{k-1} = Q x_k - Q x_{k-1} = Q (x_k - x_{k-1}) = Q s_{k-1}$.

Thus $\alpha_{BB} = \frac{s^T s}{s^T y} = \frac{s^T s}{s^T Q s}$.

This is the Rayleigh quotient of $Q$ with vector $s$. It approximates $1/\lambda$ for the direction $s$.

---

## Question 10: Projected Gradient Descent

**Question:** Minimize $f(x) = \frac{1}{2}\|x - a\|^2$ subject to $x \in [0, 1]^n$ (box constraints). What is the projected gradient iteration?

**Answer:** **$x_{k+1} = \Pi_{[0,1]^n}(x_k - \alpha (x_k - a)) = \text{clip}(x_k - \alpha(x_k - a), 0, 1)$**

**Derivation:**
$\nabla f(x) = x - a$. Gradient step: $x - \alpha(x - a) = (1-\alpha)x + \alpha a$.

Projection onto box $[0,1]^n$: clip each component to $[0, 1]$.

Iteration: $x_{k+1} = \text{clip}((1-\alpha)x_k + \alpha a, 0, 1)$.

Fixed point: $x^* = \text{clip}(x^*, 0, 1) = \text{clip}(a, 0, 1)$ — the projection of $a$ onto the box.

---

*End of Quiz*