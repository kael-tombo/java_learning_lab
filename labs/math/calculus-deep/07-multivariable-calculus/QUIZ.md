# Multivariable Calculus — Quiz (15 Questions with Worked Answers)

Partial derivatives, the chain rule in several variables, gradients,
constrained optimization, Jacobians and the Hessian. The failure modes are
interchange of limits and interchange of max with integration.

---

## Q1 — Partial vs total derivative
**Q.** $f(x,y)=x^2y$ at $(2,3)$, moving along the line $y=x$.

**A.** $f_x=2xy=12$, $f_y=x^2=4$, $\nabla f=(12,4)$. For the direction
$v=(1,1)/\sqrt2$ the rate is $\nabla f\cdot\hat v=16/\sqrt2=8\sqrt2\approx11.31$.
The common mistake is to substitute $y=x$ into $f$ and differentiate:
$g(x)=x^3$, $g'(2)=12$. That number is **not** a directional derivative at
$(2,3)$ — the point $(2,3)$ isn't on the curve $y=x$ at all. It is
$g'(2)$, the derivative of a *different* function's restriction. Always compute
$\nabla f\cdot\hat v$ at the stated point; the path method requires checking the
point lies on the path.

---

## Q2 — Chain rule, two independent variables
**Q.** $z=x^2+y^2$, $x=s\cos t$, $y=s\sin t$. Compute $\partial z/\partial t$ at $s=1$.

**A.** $\partial z/\partial t = z_x x_t+z_y y_t = 2x(-s\sin t)+2y(s\cos t)$. At $s=1$: $2\cos t(-\sin t)+2\sin t\cos t=0$. ✓
Geometrically $z=s^2$ is constant along circles, so $t$ is a tangential
direction with no radial component of change. A careless solver computes
$\partial z/\partial t=2x$ and gets a wrong answer — omitting that $x$ and $y$
*both* depend on $t$ is the universal chain-rule error in more than one variable.

---

## Q3 — Directional derivative maximized at the gradient
**Q.** Maximize the rate of change of $f=x^2+3y^2$ at $(1,2)$ over unit directions.

**A.** $\nabla f=(2x,6y)=(2,12)$, magnitude $\sqrt{4+144}=\sqrt{148}=2\sqrt{37}\approx12.17$.
Max rate is $|\nabla f|$, achieved along $\hat v=\nabla f/|\nabla f|=(1,6)/\sqrt{37}$.
The inequality $\nabla f\cdot v\le|\nabla f||v|=|\nabla f|$ (Cauchy–Schwarz)
is what pins it. The minimum rate over unit directions is $-|\nabla f|$.

---

## Q4 — Mixed partials need conditions
**Q.** Is $f_{xy}=f_{yx}$ always? Construct a counter-example.

**A.** No. Let
$f(x,y)=\frac{xy(x^2-y^2)}{x^2+y^2}$ for $(x,y)\ne(0,0)$, and $f(0,0)=0$.
Then $f_x(0,y)=-y$, $f_y(x,0)=x$, so $f_{xy}(0,0)=-1$ and $f_{yx}(0,0)=1$.
Continuity of the mixed partials in a neighbourhood of the point (Clairaut's
hypothesis) is what guarantees equality; mere existence is not enough.
Practically: any function defined by separate formulas on the axes or by
piecewise rules should be assumed to break this until continuity is verified.

---

## Q5 — Differentiating under the integral sign, and the trap
**Q.** $F(a)=\int_0^1\frac{e^{ax}}{x+2}dx$. Compute $F'(a)$. When is this legal?

**A.** $F'(a)=\int_0^1\frac{x e^{ax}}{x+2}dx$. Legality (Leibniz rule) needs
$\partial f/\partial a$ continuous on the closed rectangle and dominated there.
Counter-example where it fails: $F(a)=\int_0^1\frac{\sin(ax)}{x}dx$ at $a=0$ —
formally $F'(0)=\int_0^1\frac{1}{x}dx=\infty$, yet $F(a)=\arctan(a/a)=\frac\pi2$
for $a\ne0$ so $F'(0)=0$. The derivative exists and is 0; the integral formula
gives $\infty$. Differentiation under the integral is a theorem with
hypotheses, not a syntax rule.

---

## Q6 — Hessian and critical point classification
**Q.** Classify the critical point of $f(x,y)=x^3-3xy^2$ at the origin.

**A.** $f_x=3x^2-3y^2=0$, $f_y=-6xy=0$ ⇒ origin is critical.
$f_{xx}=6x=0$, $f_{yy}=-6y=0$, $f_{xy}=-6y=0$; at 0 the Hessian is the zero
matrix — the $D^2$ test is **inconclusive** ($D=0$). Resolve with the leading
term: $x^3-3xy^2=\Re(x+iy)^3$ changes sign on every neighbourhood ($f(t,0)=t^3$),
so the origin is a **saddle point**. The degenerate case — where all second
derivatives vanish but $f\ne$ const — always needs a higher-order or direct
analysis.

---

## Q7 — Convexity from the Hessian
**Q.** For $f=xy^2-xy^2$… more usefully: what does a negative-definite Hessian at a critical point guarantee?

**A.** If the Hessian is negative definite at a critical point, it is a strict
local maximum; positive definite, a strict local minimum. Sylvester's criterion:
for a $2\times2$ symmetric matrix, negative definite iff $f_{xx}<0$ and
$D=f_{xx}f_{yy}-f_{xy}^2>0$. **Both** conditions are needed — checking only the
trace is a classic error. Example: $f=-x^2+y^2$ has $f_{xx}=-2<0$ but
$D=(-2)(2)<0$, giving a saddle despite $f_{xx}<0$.

---

## Q8 — Lagrange multipliers with two constraints
**Q.** Maximize $z=x^2+y^2$ subject to $x+y=1$ and $x-y=0$.

**A.** $\nabla z=(2x,2y)=\lambda(1,1)+\mu(1,-1)$. Equations: $2x=\lambda+\mu$,
$2y=\lambda-\mu$, plus $x+y=1$, $x-y=0$ ⇒ $x=y=\frac12$.
Then $\lambda=\frac12$, $\mu=0$, and $z=\frac12$. Check the constraint
qualification: $\nabla g_1=(1,1)$, $\nabla g_2=(1,-1)$ are linearly independent,
so the method applies. Had the two constraint gradients been parallel, the
corner-case check would be mandatory.

---

## Q9 — Max/min order does not commute with integration
**Q.** $\int_0^1\max(x,1-x)\,dx$ — compute directly and via
$\max_x\int_0^1$ over the convex hull.

**A.** Directly: $\max(x,1-x)=1-x$ for $x\le\frac12$, $=x$ for $x\ge\frac12$;
$\int_0^{1/2}(1-x)dx+\int_{1/2}^1 x\,dx = \frac38+\frac38=\frac34$.
By contrast $\max_x\int_0^1(x,1-x)dx = \max_x(1/2-x)=\frac12$ at $x=0$.
Since $\frac34\ne\frac12$, **the order does not commute** — in general
$\int\max\ge\max\int$ for finite measures, with equality only in degenerate cases.
The same inequality explains why you cannot swap a max over parameters with an
integral over data without care, which matters in optimisation.

---

## Q10 — The Jacobian and change of variables
**Q.** Evaluate $\iint_R xy\,dA$ over $R=\{1\le x\le2,\,1\le y\le2\}$ with
$u=xy$, $v=x/y$.

**A.** $\frac{\partial(u,v)}{\partial(x,y)}=\begin{vmatrix}y&x\\ x&-y\end{vmatrix}=-2y^2$,
so $|J|=2y^2$, and the inverse has
$\left|\frac{\partial(x,y)}{\partial(u,v)}\right|=\frac{1}{2y^2}$.
Domain: $u\in[1,4]$, $v\in[\frac12,2]$, and $y=\sqrt{u/v}$, so $2y^2=2u/v$:
$\iint\frac{u}{v}\cdot\frac{v}{2u}\,du\,dv=\frac12\cdot3\cdot\frac32=\frac94$.
Direct check: $\int_1^2x\,dx\int_1^2y\,dy=(\frac32)^2=\frac94$. ✓
The Jacobian determinant must vanish for a valid change of variables — that's
the non-degeneracy test.

---

## Q11 — Non-degeneracy check
**Q.** When is a change of variables admissible at all?

**A.** The map must be one-to-one on $D$ and the Jacobian determinant must be
nonzero on $D$. Violations: $u=x^2$ folds $\mathbb{R}\to[0,\infty)$ (hence
$2\int_0^1$ rather than $\int_{-1}^1$, Q12 of the integration lab);
$u=x+y,\ v=x-y$ has $J=-2$, fine; but $u=x,\ v=x+y$ has $J=0$ — the two new
coordinates carry the same information, so no area element can be recovered.
$J=0$ is the geometric statement "the map collapses a direction".

---

## Q12 — Double integral by iterated integration and Fubini
**Q.** $\int_0^1\int_0^1 x y^2 e^{x y}\,dx\,dy$ has no elementary closed form.
What can you say without evaluating it?

**A.** The integrand is continuous and nonnegative on $[0,1]^2$, so Fubini and
Tonelli both apply and iterated integrals agree in either order:
$\int_0^1\int_0^1 \cdots = \int_0^1\int_0^1\cdots$. Positivity is the
hypothesis that makes this safe — without it you need *absolute* integrability
$\int\int|f|<\infty$, and a conditionally convergent double integral can change
value with the order of integration. Then compute
$\int_0^1 y^2\int_0^1 x e^{xy}dx\,dy$: the inner integral gives
$\frac{1}{y}\left[(y-1)e^y+1\right]$, giving a single integral in $y$ —
the practical use of Fubini is reducing dimension, not just swapping.

---

## Q13 — Gradient field and the meaning of the gradient
**Q.** If $\nabla f\cdot v=0$ for all $v$ in a set $S$, what can you conclude?

**A.** If $S$ spans $\mathbb{R}^n$, then $\nabla f=0$ everywhere on the
component, so $f$ is constant — this is the standard proof that a function
with vanishing gradient on a convex region is constant. If $S$ is only a
proper subspace (e.g. only horizontal directions), $f$ may still vary along the
orthogonal complement: for $f(x,y)=y$ and $S=\{(v,0)\}$, $\nabla f\cdot v=0$
always, yet $f$ is not constant. Directional derivatives in one family of
directions only constrain the complementary components of the gradient.

---

## Q14 — Local extrema on an open domain
**Q.** Does $f(x,y)=x^2+y^2$ attain its infimum on $\mathbb{R}^2$?

**A.** The infimum is 0, approached as $(x,y)\to0$, but not attained off the
origin. On an **open** (unbounded or not) domain the extreme value theorem does
not apply; you must check the boundary (none here) and the behaviour at infinity.
Conversely $e^{-(x^2+y^2)}$ attains its maximum but has infimum 0 not attained
in the finite plane, yet the infimum $0$ is approached at infinity. Two distinct
failure modes: missing boundary, and behaviour at infinity.

---

## Q15 — Saddle vs local min without a critical point
**Q.** Can a global minimum occur at a point where the gradient does not exist?

**A.** Yes: $|x|+|y|$ has its global minimum 0 at the origin, where $\nabla$
does not exist (the kink in $x$ and in $y$). Fermat's condition "interior local
extremum ⇒ $\nabla f=0$" assumes differentiability. The correct practical
check for a constrained or non-smooth problem: enumerate all critical points
*plus* all points where the gradient is undefined *plus* all boundary
points *plus* the limits at infinity.

---

*Self-check: Q1, Q4 and Q5 are all "the textbook manipulation gives a wrong
answer" cases. Naming the failed hypothesis in each is the mastery check.*