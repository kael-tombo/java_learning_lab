# Derivative Applications — Quiz (15 Questions with Worked Answers)

Optimization, convexity, asymptotes, related rates and L'Hôpital. Several
questions are traps: the standard recipe applied without checking hypotheses
gives the wrong answer.

---

## Q1 — Absolute extrema on a closed interval
**Q.** Find the absolute max and min of $f(x)=x^3-3x$ on $[-2,2]$.

**A.** $f'=3x^2-3=3(x-1)(x+1)$ ⇒ critical points $x=\pm1$; endpoints $\pm2$.
$f(-2)=-2$, $f(-1)=2$, $f(1)=-2$, $f(2)=2$.
Absolute max $=2$ at $x=-1$ and $x=2$; absolute min $=-2$ at $x=-2$ and $x=1$.
The absolute-extrema theorem requires continuity on the closed interval and a
*finite* critical set. If $f'$ is undefined at some interior point (like $|x|$ at
0) it must be added to the candidate list — a very common omission.

---

## Q2 — A local max that is not absolute
**Q.** Where does $f(x)=-x^3$ have a local extremum, and what is its type?

**A.** $f'=-3x^2\le0$ everywhere and $f'(0)=0$. $f$ decreases on all of
$\mathbb{R}$, so $x=0$ is a **stationary point but not an extremum** —
$(-1)^3=1>-1$ and $1^3=-1$, so values rise to the left and fall to the right.
Local max/min require the sign of $f'$ to change; $f'(0)=0$ alone is not
sufficient. This is the "second derivative test inconclusive" case, and it is
where most student solutions go wrong.

---

## Q3 — Second derivative test, inconclusive
**Q.** Apply the second-derivative test to $f(x)=x^4$ at $x=0$.

**A.** $f'=4x^3$, $f'=0$ at 0; $f''=12x^2$, $f''(0)=0$ ⇒ test inconclusive.
But $x^4\ge0$ with equality only at 0, so 0 is an absolute **minimum**.
The $D^2$ test fails because the first nonzero Taylor term here is the *fourth*
order, not the second. Use the sign-change test on $f'$ when $f''=0$.

---

## Q4 — Newton's method and its failure mode
**Q.** Newton's method $x_{n+1}=x_n-\frac{f(x_n)}{f'(x_n)}$ for $f(x)=x^3-2x$,
starting from $x_0=1$. What happens?

**A.** $x_1=1-\frac{-1}{1}=2$, $x_2=2-\frac{4}{10}=1.6$, $x_3\approx1.3254$,
and it converges to $\sqrt2$. Newton converges only to roots bracketed by
$x_n$ where $f(x_n)f'(x_n)>0$; starting on the wrong side walks *away* from the
root. Start instead at $x_0=1.9$ and you can watch it overshoot away to
$x_1\approx-0.9$. If $f'(x_0)=0$ the iteration divides by zero.

---

## Q5 — L'Hôpital misused
**Q.** A student computes $\lim_{x\to0}\frac{x}{x}$ as $1/1=1$. Correct?

**A.** The answer happens to be 1 but the *reasoning* is invalid as a limit law.
L'Hôpital requires $\frac00$ or $\frac\infty\infty$ form. Here numerator and
denominator are identical, so it is $1$ by cancellation, not by derivative.
The genuine failure case: $\lim_{x\to\infty}\frac{x}{x}=1$, but
$\lim_{x\to\infty}\frac{x+\sin x}{x}=1$ while
$\lim_{x\to\infty}\frac{x-\sin x}{x}=1$ as well — but for
$f=\frac{x}{\sqrt{x^2+1}}$ vs $\frac{\sqrt{x^2+1}}{x}$ you get $1$ and $1$,
while $\lim\frac{x^2}{x^2+1}=1$ with L'Hôpital giving $\frac{2x}{2x}=1$. The
clean counter-example to blind L'Hôpital: $\lim_{x\to\infty}\frac{x-\sin x}{x}$
is $1$, but differentiating the *numerator* alone ($1-\cos x$) without the
quotient form loses the point — always differentiate the whole quotient.

---

## Q6 — Convexity and the second derivative
**Q.** Is $f(x)=e^{-x^2}$ convex or concave on $\mathbb{R}$? Where is the inflection?

**A.** $f'=-2xe^{-x^2}$, $f''=(4x^2-2)e^{-x^2}$. Concave down where
$4x^2-2<0$, i.e. $|x|<1/\sqrt2$; concave up outside; inflection points at
$\pm 1/\sqrt2$. The bell curve is concave up in the tails — surprising only if
you assume "peaked = concave down everywhere". The exponential factor is always
positive, so the sign of $f''$ is the sign of $4x^2-2$ alone.

---

## Q7 — Tangent line, computed properly
**Q.** Find the tangent to $y=\ln x$ at $x=1$. What is the approximation near 1?

**A.** $y'=1/x$, so $y'=1$ at $1$ and $y=\ln1+1(x-1)=x-1$. Hence
$\ln x\approx x-1$ for $x$ near 1. The tangent line to a **concave** function
lies above it, so $\ln x\le x-1$ for all $x>0$, with equality only at 1 —
the tangent-line inequality is a global consequence of concavity, not just a
local approximation.

---

## Q8 — Linearization error
**Q.** Use linearization to approximate $\sqrt{4.1}$.

**A.** $f(x)=\sqrt x$, $f(4)=2$, $f'(4)=1/4$, so
$\sqrt{4.1}\approx 2+\tfrac14(0.1)=2.025$ (true value $2.024845\ldots$).
The error is second order, $\approx \tfrac{f''(4)}{2}(0.1)^2$ with
$f''=-1/(4x^{3/2})$, giving $2.5\cdot10^{-3}$ — the observed error. For a convex
function the tangent is a *lower* bound, so $2.025$ is an upper bound too.

---

## Q9 — Related rates
**Q.** A spherical balloon's radius grows at $3$ cm/s. How fast is the volume
growing when $r=10$?

**A.** $V=\frac43\pi r^3$, so $\frac{dV}{dt}=4\pi r^2\frac{dr}{dt}=4\pi(10)^2(3)=1200\pi$.
The trap is treating $r$ as constant and computing $4\pi r^2\frac{d}{dt}$, which
silently assumes zero growth. The rule: differentiate *everything* that varies
with time, then substitute values at the instant of interest.

---

## Q10 — Vertical asymptotes of a rational function
**Q.** Vertical and horizontal asymptotes of $g(x)=\dfrac{x^2-1}{x^2+2x+1}$?

**A.** Denominator $=(x+1)^2$, numerator $=(x-1)(x+1)$, so $g=\frac{x-1}{x+1}$ for
$x\neq-1$. After cancellation the limit at $-1$ is $\frac{-2}{0}$, so
$x=-1$ is a **vertical asymptote**, not a removable hole: the sign of the
denominator is the same on both sides. Original function value is undefined
there and the reduced expression also diverges. Confusing this with Q15 in the
limits lab — deciding hole vs asymptote requires evaluating the *reduced*
expression's limit.

---

## Q11 — Optimization with a constraint
**Q.** Minimize $x^2+y^2$ subject to $x+y=3$. Compare Lagrange multipliers to direct substitution.

**A.** Substitute $y=3-x$: minimize $x^2+(3-x)^2=2x^2-6x+9$, derivative
$4x-6=0$ ⇒ $x=y=3/2$, value $9/2$.
Lagrange: $\nabla f=\lambda\nabla g$ gives $2x=\lambda$, $2y=\lambda$ ⇒ $x=y$,
and $x+y=3$ forces $3/2$. Same answer, but the multiplier method generalizes to
constraints where substitution is impossible. Check the constraint qualification:
$\nabla g=(1,1)\neq0$, and on a circle constraint the compactness assumption
guarantees the extremum exists.

---

## Q12 — Rolle's theorem and its converse
**Q.** Does the converse of Rolle's theorem hold? If $f'(c)=0$ for some interior
$c$, must $f$ have a horizontal tangent crossing?

**A.** The converse fails. Rolle's theorem is $f(a)=f(b)$ ⇒ $\exists c$,
$f'(c)=0$. The reverse direction would say $f'(c)=0$ ⇒ $f(a)=f(b)$, which is
false: $f(x)=x^2$ on $[-1,2]$ has $f'(0)=0$ but $f(-1)=1\neq4=f(2)$.
What is true is that an interior extremum requires $f'(c)=0$ (Fermat), which
is the *weaker* one-directional statement people mistakenly treat as an
equivalence.

---

## Q13 — Marginal analysis
**Q.** Cost $C(q)=1000+5q+q^2$, revenue $R(q)=pq$. What $p$ maximizes profit?

**A.** $P(q)=pq-C(q)=-q^2+(p-5)q-1000$. $P'=p-5-2q$, so $q^*=\frac{p-5}{2}$.
Second derivative $P''=-2<0$: max. Requires $p>5$, otherwise the optimum is
$q=0$ (boundary) — and once $p\le5$ the firm should not operate at all, since
the fixed cost $1000$ is sunk. Ignoring the boundary is the standard error.

---

## Q14 — Sign chart and multiplicities
**Q.** At what roots does the sign of $f(x)=x^2(x-1)$ change?

**A.** $x^2$ has a root of even multiplicity 2 ⇒ no sign change at 0 (touches the
axis); $x-1$ has multiplicity 1 ⇒ sign change at 1. Generally the sign changes
exactly at roots of **odd** multiplicity. A graph drawn from this must touch at 0
and cross at 1 — a cheap check that catches most sign-chart errors.

---

## Q15 — Describing asymptotes end-to-end
**Q.** Sketch $f(x)=\dfrac{2x}{x^2-4}$: give vertical, horizontal and oblique asymptotes.

**A.** Vertical: roots of denominator $x=\pm2$, both genuine (numerator
$2x=\pm4\neq0$ there). Horizontal: degrees equal-ish (1 vs 2) ⇒
$y=0$ as $x\to\pm\infty$. Oblique: none, since $\deg\text{num}<\deg\text{den}$.
Behavior: $f(x)\approx \frac{1}{2x}$ near infinity so it approaches $0$ from
$+\infty$ on the right and from $-\infty$ on the left. Full sketch: two
branches, vertical blow-ups at $\pm2$, and $\lim_{x\to2^-}=-\infty$,
$\lim_{x\to2^+}=+\infty$, $\lim_{x\to-2^-}=+\infty$, $\lim_{x\to-2^-}=-\infty$.

---

*Self-check: Q2, Q5 and Q12 are all "the standard procedure gives the wrong
answer" cases. Being able to name the failed hypothesis in each is the point of
the lab.*