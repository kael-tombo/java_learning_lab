# Numerical Methods — Exercises (5 Problems with Hints)

---

## Problem 1: Bisection vs. Newton-Raphson Comparison

**Implement both bisection and Newton-Raphson to find the root of $f(x) = x^3 - 2x - 5$ on $[2, 3]$. Compare the number of iterations needed to achieve $|f(x)| < 10^{-10}$.**

### Requirements:
- Bisection: start with $[a,b] = [2, 3]$
- Newton: start with $x_0 = 2.5$
- Track iterations and $|f(x_n)|$ at each step
- Print convergence history for both

### Hints:
1. **Bisection:** Check sign change: $f(2) = -1$, $f(3) = 16$. Guaranteed root.
2. **Newton derivative:** $f'(x) = 3x^2 - 2$.
3. **Termination:** Stop when $|f(x_n)| < 10^{-10}$ or max iterations reached.
4. **Expected:** Newton should converge in ~5-6 iterations; bisection needs ~30.

### Extension:
- Modify Newton to handle the case where $f'(x_n) \approx 0$ (fallback to bisection step).
- Plot error vs. iteration on log scale for both methods.

---

## Problem 2: Secant Method with Order Verification

**Implement the secant method for $f(x) = \cos x - x$ (root ≈ 0.739085). Starting with $x_0 = 0.5$, $x_1 = 1.0$, compute the empirical convergence order from the error sequence.**

### Requirements:
- Implement secant iteration: $x_{n+1} = x_n - f(x_n)\frac{x_n - x_{n-1}}{f(x_n) - f(x_{n-1})}$
- Store all iterates, compute errors $e_n = |x_n - r|$ using known root $r$
- Estimate order: $p_n = \frac{\log|e_{n+1}/e_n|}{\log|e_n/e_{n-1}|}$
- Print $x_n$, $e_n$, $p_n$ for each iteration

### Hints:
1. **Known root:** $r \approx 0.7390851332151607$ (solve $\cos r = r$).
2. **Order estimation:** Need at least 3 iterates. Skip early pre-asymptotic values.
3. **Expected order:** Should approach $\phi \approx 1.618$ in the asymptotic regime.
3. **Edge case:** Handle division by near-zero in secant formula.

### Extension:
- Compare secant vs. Newton iteration counts for same tolerance.
- Test on $f(x) = e^{-x} - x$ (Lambert W root).

---

## Problem 3: Composite Simpson's Rule with Error Control

**Implement composite Simpson's rule for $\int_0^1 \frac{4}{1+x^2} dx = \pi$. Add adaptive step refinement: double $n$ until successive estimates differ by less than $\epsilon = 10^{-12}$.**

### Requirements:
- Function: $f(x) = \frac{4}{1+x^2}$ on $[0, 1]$
- Composite Simpson with even $n$: $S_n = \frac{h}{3}[f_0 + 4\sum_{\text{odd}} f_i + 2\sum_{\text{even}} f_i + f_n]$
- Start with $n = 2$, double $n$ each iteration
- Stop when $|S_{2n} - S_n| < 15\epsilon$ (Richardson error estimate)
- Output: approximation, error vs. $\pi$, $n$ used, order estimate

### Hints:
1. **Simpson weights:** Pattern 1, 4, 2, 4, 2, ..., 4, 1 for $n$ even.
2. **Error estimate:** $\text{error} \approx \frac{|S_{2n} - S_n|}{15}$ from Richardson extrapolation.
3. **Exact value:** $\pi = 3.141592653589793...$
4. **Efficiency:** Reuse function evaluations from previous $n$ when doubling.

### Extension:
- Implement full adaptive recursive Simpson (subdivide only where error large).
- Compare function evaluations vs. fixed composite Simpson for same accuracy.

---

## Problem 4: Numerical Differentiation with Richardson Extrapolation

**Implement central difference differentiation with Richardson extrapolation for $f(x) = e^{\sin x}$ at $x = 1$. Compute $f'(1)$ and compare errors for $h = 0.1, 0.05, 0.025, 0.0125$ with and without extrapolation.**

### Requirements:
- $f(x) = e^{\sin x}$, exact derivative: $f'(x) = \cos x \cdot e^{\sin x}$, so $f'(1) = \cos(1) \cdot e^{\sin(1)} \approx 1.2727$
- Central difference: $D(h) = \frac{f(1+h) - f(1-h)}{2h}$
- Richardson extrapolated: $D_{extrap}(h) = \frac{4D(h/2) - D(h)}{3}$
- Table: $h$, $D(h)$, error $|D(h) - f'(1)|$, $D_{extrap}(h)$, extrapolated error
- Find optimal $h$ for both methods

### Hints:
1. **Error behavior:** Central difference error $\approx c_2 h^2 + c_4 h^4 + \cdots$
2. **Richardson eliminates $h^2$ term**, leaving $O(h^4)$ error.
3. **Optimal $h$:** Without extrapolation: $h_{opt} \sim \epsilon^{1/3} \approx 10^{-5}$; with extrapolation: $h_{opt} \sim \epsilon^{1/5} \approx 10^{-3}$ (larger $h$ OK).
4. **Cancellation:** Watch for catastrophic cancellation when $h$ too small.

### Extension:
- Derive $O(h^6)$ extrapolation using $h, h/2, h/4$.
- Test on $f(x) = \frac{1}{1+x^2}$ near $x=0$ (Runge phenomenon).

---

## Problem 5: Newton-Raphson for Systems (2D)

**Extend Newton-Raphson to solve the 2D system:**
$$
\begin{cases}
f_1(x, y) = x^2 + y^2 - 4 = 0 \\
f_2(x, y) = x^2 - y - 1 = 0
\end{cases}
$$
**Starting from $(x_0, y_0) = (1, 1)$, implement the multivariate Newton method with Jacobian matrix.**

### Requirements:
- System: $F(\mathbf{x}) = \mathbf{0}$ where $\mathbf{x} = [x, y]^T$
- Jacobian: $J = \begin{bmatrix} 2x & 2y \\ 2x & -1 \end{bmatrix}$
- Newton step: Solve $J \Delta \mathbf{x} = -F$, then $\mathbf{x}_{n+1} = \mathbf{x}_n + \Delta \mathbf{x}$
- Use Gaussian elimination or matrix inverse for $2\times 2$ system
- Iterate until $\|F(\mathbf{x}_n)\| < 10^{-12}$
- Print iterates and errors

### Hints:
1. **Exact solutions:** Intersection of circle $x^2+y^2=4$ and parabola $y=x^2-1$.
   - Substitute: $x^2 + (x^2-1)^2 = 4 \implies x^4 - x^2 - 3 = 0$
   - $x^2 = \frac{1+\sqrt{13}}{2} \approx 2.3028$, so $x \approx \pm 1.5175$, $y \approx 1.3028$
   - Starting at $(1,1)$ should converge to $(1.5175, 1.3028)$.
2. **2×2 linear solve:** For $J = \begin{bmatrix} a & b \\ c & d \end{bmatrix}$, $\det = ad-bc$.
   - $\Delta x = (-d F_1 + b F_2)/\det$, $\Delta y = (c F_1 - a F_2)/\det$
3. **Singular Jacobian:** Check $\det \neq 0$; if near zero, perturb or use damping.
4. **Convergence:** Quadratic near root; 4-5 iterations expected.

### Extension:
- Add backtracking line search: try $\mathbf{x} + \alpha \Delta \mathbf{x}$ with $\alpha = 1, 0.5, 0.25, \ldots$ until $\|F\|$ decreases.
- Generalize to $n \times n$ using LU decomposition.
- Test on $f_1 = e^x + y - 1$, $f_2 = x + e^y - 1$.

---

*End of Exercises*