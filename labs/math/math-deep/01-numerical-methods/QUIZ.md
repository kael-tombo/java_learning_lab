# Numerical Methods — Quiz (10 Questions with Worked Answers)

---

## Question 1: Bisection Method Convergence

**Question:** The bisection method is applied to find a root of $f(x) = x^3 - 2$ on the interval $[1, 2]$. After how many iterations is the interval width guaranteed to be less than $10^{-6}$?

**Answer:** **20 iterations**

**Derivation:**
The bisection method halves the interval width each iteration. Starting width: $b - a = 2 - 1 = 1$.

After $n$ iterations, width $= \frac{1}{2^n}$. We need $\frac{1}{2^n} < 10^{-6}$.

Taking $\log_2$: $n > \log_2(10^6) = 6 \log_2(10) \approx 6 \times 3.3219 = 19.93$

Thus $n \geq 20$ iterations.

---

## Question 2: Newton-Raphson Quadratic Convergence

**Question:** For $f(x) = x^2 - 2$ with root $r = \sqrt{2}$, Newton-Raphson iteration is $x_{n+1} = \frac{1}{2}(x_n + \frac{2}{x_n})$. If $x_0 = 1.5$, show that the error $e_n = x_n - r$ satisfies $e_{n+1} \approx \frac{1}{2\sqrt{2}} e_n^2$ asymptotically.

**Answer:** **$C = \frac{1}{2\sqrt{2}} \approx 0.3536$**

**Derivation:**
General Newton error formula for simple root: $e_{n+1} \approx \frac{f''(r)}{2f'(r)} e_n^2$.

Here $f(x) = x^2 - 2$, so $f'(x) = 2x$, $f''(x) = 2$.
At $r = \sqrt{2}$: $f'(r) = 2\sqrt{2}$, $f''(r) = 2$.

Thus $C = \frac{2}{2 \cdot 2\sqrt{2}} = \frac{1}{2\sqrt{2}}$.

---

## Question 3: Secant Method Order

**Question:** The secant method uses $x_{n+1} = x_n - f(x_n)\frac{x_n - x_{n-1}}{f(x_n) - f(x_{n-1})}$. Its convergence order $p$ satisfies $p^2 = p + 1$. What is $p$?

**Answer:** **$p = \frac{1+\sqrt{5}}{2} \approx 1.618$ (golden ratio $\phi$)**

**Derivation:**
The order $p$ comes from the error recurrence $e_{n+1} \approx C e_n^p$. For secant method, the characteristic equation is $p^2 - p - 1 = 0$.

Solving: $p = \frac{1 \pm \sqrt{5}}{2}$. Taking positive root: $p = \frac{1+\sqrt{5}}{2} = \phi \approx 1.618$.

---

## Question 4: Trapezoidal Rule Error

**Question:** Estimate the error in approximating $\int_0^1 e^x dx$ using the composite trapezoidal rule with $n=4$ subintervals. The exact integral is $e - 1 \approx 1.71828$.

**Answer:** **Error $\approx -0.004$**

**Derivation:**
Composite trapezoidal error: $E = -\frac{(b-a)h^2}{12} f''(\xi)$ for some $\xi \in [a,b]$.

Here $a=0, b=1, h=0.25$, $f(x)=e^x$, $f''(x)=e^x$. Max $|f''|$ on $[0,1]$ is $e \approx 2.718$.

$|E| \leq \frac{1 \cdot 0.25^2}{12} \cdot e = \frac{0.0625}{12} \cdot 2.718 \approx 0.0142$.

Actual composite trapezoidal with $n=4$:
$x = [0, 0.25, 0.5, 0.75, 1]$, $f(x) = [1, e^{0.25}, e^{0.5}, e^{0.75}, e] \approx [1, 1.284, 1.649, 2.117, 2.718]$

$T = 0.25 \times [0.5(1) + 1.284 + 1.649 + 2.117 + 0.5(2.718)] = 0.25 \times 7.978 = 1.7145$

Error $= 1.7145 - 1.71828 = -0.0038 \approx -0.004$

---

## Question 5: Simpson's Rule Exactness

**Question:** Simpson's rule is exact for polynomials of degree $\leq 3$. Prove it integrates $f(x) = x^3$ exactly on $[0, 1]$.

**Answer:** **Simpson's rule gives exactly $\frac{1}{4}$**

**Derivation:**
Simpson's rule on $[0,1]$: $S = \frac{1}{6}[f(0) + 4f(0.5) + f(1)]$

For $f(x) = x^3$: $f(0)=0$, $f(0.5)=0.125$, $f(1)=1$

$S = \frac{1}{6}[0 + 4(0.125) + 1] = \frac{1}{6}[0.5 + 1] = \frac{1.5}{6} = \frac{1}{4}$

Exact integral: $\int_0^1 x^3 dx = [\frac{x^4}{4}]_0^1 = \frac{1}{4}$. Matches exactly.

---

## Question 6: Central Difference Error

**Question:** The central difference formula $f'(x) \approx \frac{f(x+h) - f(x-h)}{2h}$ has truncation error $O(h^2)$. For $f(x) = \sin x$ at $x = \pi/4$, find the optimal $h$ that balances truncation and roundoff error (machine epsilon $\epsilon \approx 2.2 \times 10^{-16}$).

**Answer:** **$h_{opt} \approx 2.7 \times 10^{-6}$**

**Derivation:**
Total error $\approx \frac{h^2}{6}|f'''(\xi)| + \frac{\epsilon}{h}|f(\eta)|$

For $f(x) = \sin x$, $f'''(x) = -\cos x$, $|f'''| \leq 1$, $|f| \leq 1$.

Error $\approx \frac{h^2}{6} + \frac{\epsilon}{h}$

Minimize: $\frac{d}{dh}(\frac{h^2}{6} + \frac{\epsilon}{h}) = \frac{h}{3} - \frac{\epsilon}{h^2} = 0$

$\frac{h}{3} = \frac{\epsilon}{h^2} \implies h^3 = 3\epsilon \implies h = (3\epsilon)^{1/3}$

$h = (3 \times 2.2 \times 10^{-16})^{1/3} = (6.6 \times 10^{-16})^{1/3} \approx 2.7 \times 10^{-6}$

---

## Question 7: Richardson Extrapolation

**Question:** Given $D(h) = f'(x) + c h^2 + O(h^4)$ (central difference), use Richardson extrapolation with $h$ and $h/2$ to eliminate the $h^2$ term. What is the extrapolated formula?

**Answer:** **$D_{extrap} = \frac{4D(h/2) - D(h)}{3}$**

**Derivation:**
$D(h) = f'(x) + c h^2 + O(h^4)$
$D(h/2) = f'(x) + c (h/2)^2 + O(h^4) = f'(x) + \frac{c h^2}{4} + O(h^4)$

Multiply second by 4: $4D(h/2) = 4f'(x) + c h^2 + O(h^4)$

Subtract: $4D(h/2) - D(h) = 3f'(x) + O(h^4)$

Thus $f'(x) \approx \frac{4D(h/2) - D(h)}{3}$

---

## Question 8: Newton-Raphson on Multiple Root

**Question:** For $f(x) = (x-1)^2$ with double root at $x=1$, standard Newton converges linearly with factor $\frac{1}{2}$. Modified Newton with known multiplicity $m=2$ uses $x_{n+1} = x_n - 2\frac{f(x_n)}{f'(x_n)}$. Show this restores quadratic convergence.

**Answer:** **Modified Newton error: $e_{n+1} \approx \frac{1}{2} \frac{f''(r)}{f'(r)} e_n^2$ (quadratic)**

**Derivation:**
Standard Newton for multiplicity $m$: $e_{n+1} \approx \frac{m-1}{m} e_n$ (linear).

Modified Newton: $x_{n+1} = x_n - m \frac{f(x_n)}{f'(x_n)}$

For $f(x) = (x-r)^m g(x)$ with $g(r) \neq 0$:
$\frac{f}{f'} = \frac{(x-r)^m g}{m(x-r)^{m-1}g + (x-r)^m g'} = \frac{x-r}{m} \cdot \frac{1}{1 + \frac{(x-r)g'}{mg}}$

Taylor expand: $\frac{f}{f'} = \frac{e_n}{m}(1 - \frac{e_n g'}{mg} + \cdots)$

Then $e_{n+1} = e_n - m \frac{f}{f'} = e_n - e_n(1 - \frac{e_n g'}{mg} + \cdots) = \frac{g'(r)}{g(r)} e_n^2 + \cdots$

For $f(x) = (x-1)^2$, $g(x)=1$, $g'=0$, so $e_{n+1} = O(e_n^2)$ — quadratic!

---

## Question 9: Adaptive Quadrature

**Question:** Adaptive Simpson's rule recursively subdivides intervals where the error estimate exceeds tolerance. If $S(a,b)$ is Simpson on $[a,b]$, $S(a,m)$ and $S(m,b)$ on halves with $m=\frac{a+b}{2}$, what is the error estimate used?

**Answer:** **Error estimate $\approx \frac{1}{15}[S(a,m) + S(m,b) - S(a,b)]$**

**Derivation:**
For smooth $f$, Simpson's rule has error $E = -\frac{(b-a)h^4}{180} f^{(4)}(\xi)$.

Let $S_2 = S(a,m) + S(m,b)$ (composite on two halves, step $h/2$).
$S_1 = S(a,b)$ (single step $h$).

Error in $S_1$: $E_1 = C h^4$
Error in $S_2$: $E_2 = 2 \cdot C (h/2)^4 = \frac{C h^4}{8}$

True integral $I = S_1 + E_1 = S_2 + E_2$

$E_1 = \frac{1}{7}(S_2 - S_1)$ approximately (since $E_2 = E_1/8$ and $S_2 - S_1 = E_1 - E_2 = 7/8 E_1$)

Better estimate: $|I - S_2| \approx \frac{|S_2 - S_1|}{15}$

---

## Question 10: Fixed Point Iteration

**Question:** Solve $x = g(x)$ with $g(x) = \cos x$ using fixed-point iteration $x_{n+1} = g(x_n)$ starting at $x_0 = 0.5$. Does it converge? If so, to what?

**Answer:** **Converges to $x^* \approx 0.739085$ (Dottie number)**

**Derivation:**
Fixed point requires $x = \cos x$. This is the Dottie number.

Convergence condition: $|g'(x^*)| < 1$. Here $g'(x) = -\sin x$, $|g'(x^*)| = |\sin(0.739)| \approx 0.67 < 1$. Converges.

Iteration: $x_0 = 0.5$
$x_1 = \cos(0.5) \approx 0.8776$
$x_2 = \cos(0.8776) \approx 0.6390$
$x_3 = \cos(0.6390) \approx 0.8027$
$x_4 = \cos(0.8027) \approx 0.6948$
... converges to $\approx 0.739085$

---

*End of Quiz*