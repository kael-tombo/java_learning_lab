# Numerical Methods — Flashcards

---

## Root Finding

### Bisection Method
**Q:** What is the bisection method's convergence rate?
**A:** Linear. Interval width halves each iteration: $w_n = \frac{b-a}{2^n}$.

**Q:** What are the requirements for bisection to work?
**A:** $f$ continuous on $[a,b]$ and $f(a)f(b) < 0$ (sign change).

**Q:** How many iterations to achieve tolerance $\epsilon$?
**A:** $n \geq \log_2\left(\frac{b-a}{\epsilon}\right)$.

---

### Newton-Raphson Method
**Q:** What is the Newton-Raphson iteration formula?
**A:** $x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$.

**Q:** What is the convergence order for a simple root?
**A:** Quadratic ($p=2$): $|e_{n+1}| \approx C|e_n|^2$ where $C = \frac{|f''(r)|}{2|f'(r)|}$.

**Q:** What happens at a multiple root of multiplicity $m$?
**A:** Convergence becomes linear with factor $\frac{m-1}{m}$. Use modified Newton: $x_{n+1} = x_n - m\frac{f(x_n)}{f'(x_n)}$ to restore quadratic convergence.

**Q:** When does Newton-Raphson fail?
**A:** 1) $f'(x_n) \approx 0$ (horizontal tangent), 2) Poor initial guess (divergence/cycles), 3) Multiple roots without modification, 4) Non-differentiable $f$.

---

### Secant Method
**Q:** What is the secant method iteration?
**A:** $x_{n+1} = x_n - f(x_n)\frac{x_n - x_{n-1}}{f(x_n) - f(x_{n-1})}$.

**Q:** What is its convergence order?
**A:** Superlinear, $p = \frac{1+\sqrt{5}}{2} \approx 1.618$ (golden ratio $\phi$).

**Q:** Advantage over Newton?
**A:** No derivative required; only one function evaluation per iteration (after first).

---

### Fixed-Point Iteration
**Q:** What is fixed-point iteration?
**A:** $x_{n+1} = g(x_n)$ to solve $x = g(x)$.

**Q:** Convergence condition?
**A:** $|g'(x^*)| < 1$ at the fixed point $x^*$.

**Q:** How to accelerate?
**A:** Aitken's $\Delta^2$ method or Steffensen's method (achieves quadratic convergence).

---

## Numerical Integration

### Trapezoidal Rule
**Q:** Formula for single interval $[a,b]$?
**A:** $\int_a^b f(x)dx \approx \frac{b-a}{2}[f(a) + f(b)]$.

**Q:** Composite trapezoidal rule with $n$ subintervals?
**A:** $T_n = h\left[\frac{f(a)}{2} + \sum_{i=1}^{n-1} f(a+ih) + \frac{f(b)}{2}\right]$, $h = \frac{b-a}{n}$.

**Q:** Error term?
**A:** $E = -\frac{(b-a)h^2}{12}f''(\xi)$, $O(h^2)$ global error.

---

### Simpson's Rule
**Q:** Formula for single interval $[a,b]$?
**A:** $S = \frac{b-a}{6}[f(a) + 4f(\frac{a+b}{2}) + f(b)]$.

**Q:** Composite Simpson's rule ($n$ even)?
**A:** $S_n = \frac{h}{3}[f(a) + 4\sum_{i \text{ odd}} f_i + 2\sum_{i \text{ even}} f_i + f(b)]$.

**Q:** Error term?
**A:** $E = -\frac{(b-a)h^4}{180}f^{(4)}(\xi)$, $O(h^4)$ global error.

**Q:** For what polynomials is Simpson exact?
**A:** Degree $\leq 3$.

---

### Adaptive Quadrature
**Q:** Basic idea of adaptive Simpson?
**A:** Compare $S(a,b)$ with $S(a,m)+S(m,b)$; if difference > $15\epsilon$, recurse on subintervals.

**Q:** Error estimate for adaptive Simpson?
**A:** $\text{error} \approx \frac{|S(a,m) + S(m,b) - S(a,b)|}{15}$.

---

### Gaussian Quadrature
**Q:** What is Gauss-Legendre quadrature?
**A:** $\int_{-1}^1 f(x)dx \approx \sum_{i=1}^n w_i f(x_i)$ with optimal nodes $x_i$ (roots of Legendre polynomial) and weights $w_i$.

**Q:** Degree of exactness for $n$ points?
**A:** $2n-1$ (exact for polynomials up to degree $2n-1$).

---

## Numerical Differentiation

### Finite Differences
**Q:** Forward difference formula?
**A:** $f'(x) \approx \frac{f(x+h) - f(x)}{h}$, error $O(h)$.

**Q:** Backward difference formula?
**A:** $f'(x) \approx \frac{f(x) - f(x-h)}{h}$, error $O(h)$.

**Q:** Central difference formula?
**A:** $f'(x) \approx \frac{f(x+h) - f(x-h)}{2h}$, error $O(h^2)$.

**Q:** Second derivative central difference?
**A:** $f''(x) \approx \frac{f(x+h) - 2f(x) + f(x-h)}{h^2}$, error $O(h^2)$.

---

### Richardson Extrapolation
**Q:** Idea of Richardson extrapolation?
**A:** Combine approximations at different step sizes to cancel leading error terms.

**Q:** Central difference with Richardson ($h$ and $h/2$)?
**A:** $D_{extrap} = \frac{4D(h/2) - D(h)}{3}$, achieves $O(h^4)$.

**Q:** General pattern for error $c h^p$?
**A:** $\frac{2^p D(h/2) - D(h)}{2^p - 1}$.

---

### Optimal Step Size
**Q:** Why not use $h \to 0$?
**A:** Roundoff error $\frac{\epsilon}{h}$ dominates as $h \to 0$ (catastrophic cancellation).

**Q:** Optimal $h$ for central difference?
**A:** $h_{opt} \approx (3\epsilon)^{1/3} \approx 2.7 \times 10^{-6}$ (for double precision).

---

## Error Analysis

### Error Types
**Q:** Truncation error?
**A:** Error from approximating a mathematical procedure (e.g., Taylor series truncation).

**Q:** Roundoff error?
**A:** Error from finite-precision floating-point arithmetic.

**Q:** Total error?
**A:** Sum of truncation and roundoff errors; has a minimum at optimal $h$.

---

### Condition Number
**Q:** Condition number of root finding?
**A:** $\kappa = \frac{1}{|f'(r)|}$ — sensitivity of root to perturbations in $f$.

**Q:** Ill-conditioned problem?
**A:** Small $|f'(r)|$ (root near extremum) $\to$ large condition number $\to$ sensitive to errors.

---

### Stability
**Q:** Forward stable algorithm?
**A:** Computed result equals exact result for slightly perturbed input.

**Q:** Backward stable algorithm?
**A:** Computed result is exact solution to a nearby problem.

---

## Convergence Theory

### Order of Convergence
**Q:** Definition of order $p$?
**A:** $\lim_{n\to\infty} \frac{|e_{n+1}|}{|e_n|^p} = C > 0$ (finite).

**Q:** Linear convergence ($p=1$)?
**A:** $|e_{n+1}| \leq C|e_n|$ with $C < 1$. Error decreases by constant factor.

**Q:** Quadratic convergence ($p=2$)?
**A:** $|e_{n+1}| \leq C|e_n|^2$. Correct digits roughly double each iteration.

**Q:** Superlinear ($1 < p < 2$)?
**A:** Faster than linear, slower than quadratic (e.g., secant: $p \approx 1.618$).

---

### Convergence Tests
**Q:** Aitken's $\Delta^2$ acceleration?
**A:** Given sequence $x_n$, compute $\hat{x}_n = x_n - \frac{(\Delta x_n)^2}{\Delta^2 x_n}$ where $\Delta x_n = x_{n+1} - x_n$.

**Q:** Estimating order from errors?
**A:** $p \approx \frac{\log|e_{n+1}/e_n|}{\log|e_n/e_{n-1}|}$ for three consecutive errors.

---

*End of Flashcards*