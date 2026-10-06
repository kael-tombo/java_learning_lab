# Integral Fundamentals — Quiz (15 Questions with Worked Answers)

Focus on the Fundamental Theorem, definite vs indefinite integrals, improper
integrals and the conditions each one needs.

---

## Q1 — FTC part 1: derivative of an accumulator
**Q.** Let $F(x)=\int_0^x t^2e^{-t}\,dt$. Find $F'(x)$.

**A.** $F'(x)=x^2e^{-x}$. This is the whole of FTC-I: if $F$ is continuous on
$[a,b]$ and $f$ continuous, then $\frac{d}{dx}\int_a^x f(t)\,dt=f(x)$.
Two points students miss: (i) the variable of integration is a *dummy* — the
upper limit is where the evaluation happens; (ii) the derivative picks up
$f(\text{upper limit})$, which is why $\int_a^x$ gives no chain-rule factor.

---

## Q2 — FTC part 2: the derivative of an antiderivative
**Q.** If $F'(x)=x^2e^{-x}$ everywhere and $F(0)=3$, express $F$.

**A.** $F(x)=3+\int_0^x t^2e^{-t}\,dt$. Integration and differentiation are
inverse operations *up to a constant*, and the initial condition fixes that
constant. The definite integral and the indefinite antiderivative differ only
in that the definite form carries the constant for you — which is why
engineering work is done with definite integrals of the form $\int_{t_0}^{t}$.

---

## Q3 — Non-elementary but perfectly computable
**Q.** Is there an elementary antiderivative for $e^{-x^2}$? How is
$\int_0^1 e^{-x^2}dx$ evaluated then?

**A.** No — it has no antiderivative in elementary functions (Liouville's
theorem). It is $\frac{\sqrt\pi}{2}\operatorname{erf}(1)\approx0.7468$, with
$\operatorname{erf}$ a special function, or it is computed numerically
(Simpson/Gauss–Legendre). The lesson: existence of the definite integral never
depends on elementary antiderivatives. FTC still applies — $F(x)=\int_0^x
e^{-t^2}dt$ is differentiable with $F'(x)=e^{-x^2}$.

---

## Q4 — Improper integral that converges to infinity
**Q.** Does $\int_1^\infty \frac{1}{x^p}dx$ converge? Find the threshold.

**A.** $\int_1^\infty x^{-p}dx=\lim_{R\to\infty}\frac{R^{1-p}-1}{1-p}$ for
$p\ne1$, and $\ln R\to\infty$ for $p=1$. So it converges iff $p>1$, with value
$\frac{1}{p-1}$. Convergence depends on the *rate of decay vs the tail length*,
not on the integrand's magnitude near the lower limit. The same threshold appears
in the zeta function at $s=1$.

---

## Q5 — Both endpoints improper
**Q.** Evaluate $\int_0^2\frac{dx}{\sqrt{x}}$ treating it correctly.

**A.** $\int_0^2 x^{-1/2}dx=2\sqrt{x}\big|_0^2=2\sqrt2$. Though the integrand
is unbounded at 0, the improper integral converges because $p=\tfrac12<1$ in
$x^{-p}$. Generally $\int_0^\epsilon x^{-p}dx$ converges iff $p<1$; $p=1$ gives
$\ln\epsilon\to-\infty$, $p>1$ diverges to $+\infty$. Substituting an endpoint
where $f$ is undefined is exactly the "plug in and get a finite answer" trap.

---

## Q6 — The $\tfrac{1}{2}\ln x$ error
**Q.** A student computes $\int_1^4\frac{1}{2x}dx$ as $\tfrac12\ln 4$. Where is the error?

**A.** Missing $\ln x$. The integral is $\tfrac12\int_1^4\frac{1}{x}dx=\tfrac12\ln4=\ln2$.
More importantly: substituting the limits into an *antiderivative* is valid
only because FTC part 2 guarantees a continuous antiderivative of a continuous
integrand. For $\int_{-1}^1 x^3 dx$ the antiderivative $x^4/4$ evaluated
endpoint-wise gives 0, but the *oriented* (signed) area is indeed 0 — the
nonnegativity assumption is needed for the "area under the curve" reading, not
for the signed integral.

---

## Q7 — Average value of a function
**Q.** What is the average value of $f(x)=\sin x$ on $[0,\pi]$?

**A.** $\frac1\pi\int_0^\pi \sin x\,dx=\frac1\pi\cdot2=\frac2\pi$.
Note this is not the integral divided by $\pi-0$ by accident — the formula is
$\frac1{b-a}\int_a^b f$. For a non-negative continuous $f$ the average value
lies between $\min f$ and $\max f$ (integral mean value theorem), which for
$\sin$ on $[0,\pi]$ gives the useful bound $2/\pi\in[0,1]$.

---

## Q8 — Signed vs geometric area
**Q.** Compute the actual area between $y=x^2$ and $y=1$ on $[-1,1]$.

**A.** Curves cross at $x=\pm1$; $1\ge x^2$ throughout. Area $=\int_{-1}^1(1-x^2)dx=[x-x^3/3]_{-1}^1=4/3$.
The integral of the *difference* with the upper curve minus the lower is
already the area here. Had the curves crossed twice inside the interval you
would have to split the integral at each crossing point — a routine step that is
routinely skipped.

---

## Q9 — Substitution and the direction of the change
**Q.** Evaluate $\int_0^1 2x\cos(x^2)\,dx$ using substitution.

**A.** Let $u=x^2$, $du=2x\,dx$; limits $0\to0$, $1\to1$:
$\int_0^1 \cos u\,du=\sin 1$. Two structural requirements: the substituted
integrand must be present as a product including the differential, and the
limits must be converted in the direction of the substitution. Changing the
function without changing the limits to match is the standard slip.

---

## Q10 — Integration by parts, choosing $u$ and $dv$
**Q.** Evaluate $\int_0^1 x\ln x\,dx$ and explain the $u$ choice.

**A.** Take $u=\ln x$, $dv=x\,dx$ ⇒ $du=\frac{dx}{x}$, $v=\frac{x^2}{2}$:
$\left[\frac{x^2}{2}\ln x\right]_0^1-\frac12\int_0^1 x\,dx=-\frac14$.
The boundary term vanishes because $x^2\ln x\to0$ as $x\to0^+$. The choice rule
(liar: logarithms and inverse trigs go to $u$; algebraic goes to $dv$) exists so
that $v$ stays elementary — assigning $u=x$ would leave $\int\frac{1}{x}\cdot
x^2\,dx$-type loops that never terminate.

---

## Q11 — The p-test at the boundary
**Q.** $\int_0^1\frac{1}{x}\,dx$ — diverges to $+\infty$. Contrast with
$\int_0^1\frac{1}{\ln x}dx$. What happens there?

**A.** The second is ill-defined near $x=1$: $\ln x\to0^-$ as $x\to1^-$, so
the integrand $\to-\infty$ there. $\int_0^{1-\epsilon}\frac{dx}{\ln x}$ tends to
a *finite* value as $\epsilon\to0$, which is why people wrongly conclude the
improper integral "converges".

---

## Q12 — Integrability conditions
**Q.** $f(x)=x^{-1/2}$ on $(0,1]$ is unbounded at 0. Can FTC apply?

**A.** Yes, in the improper form: $F(x)=\int_0^x t^{-1/2}dt=2\sqrt x$ is
well-defined and $F'(x)=x^{-1/2}$ for $x>0$. FTC requires continuity on the
interval; if the singularity is *inside* $[a,b]$ you must split and take the
limits separately, and if both improper pieces converge the total converges.
Unboundedness at one point does not prevent integrability.

---

## Q13 — Orientation of the definite integral
**Q.** Show $\int_a^b f = -\int_b^a f$, and evaluate $\int_1^3 x\,dx$ and $\int_3^1 x\,dx$.

**A.** Reversing limits reverses orientation: $\frac{1}{4}(3^2-1^2)=2$ versus
$\frac{1}{4}(1^2-3^2)=-2$. Orientation is what makes $\int_a^b f+\int_b^a f=0$,
and it is why "area" always needs $\left|\int\right|$ or a positive/negative
split. In physics, $\int_a^b \vec F\cdot d\vec r$ depends critically on the
direction of traversal.

---

## Q14 — Antiderivative families
**Q.** Verify that $F(x)=x^2e^{-x}$ and $G(x)=x^2e^{-x}+C$ both antiderivative
$xe^{-x}$… careful, verify the correct integrand.

**A.** $\frac{d}{dx}\left(x^2e^{-x}\right)=2xe^{-x}-x^2e^{-x}=(2x-x^2)e^{-x}$.
Since any two antiderivatives of the same continuous function differ by a
constant on an interval, $\{(2x-x^2)e^{-x}+C\}$ is the complete family. This is
why an indefinite integral must always be written $+C$: the constant encodes
the initial condition you haven't applied yet.

---

## Q15 — Detecting a false claim by symmetry
**Q.** Is $\int_0^\infty\frac{\sin x}{x}dx$ integrable as an improper integral?

**A.** It converges only in the **Cauchy principal value** sense, not as an
ordinary improper integral: $\int_0^R$ has a limit ($\pi/2$) because the
oscillation damps the tail like $1/x$ by Dirichlet's test, but $\int_0^\infty$
defined as $\lim_{R\to\infty}\int_0^R$ does exist here. Contrast
$\int_1^\infty\frac{1}{x}dx$ which diverges. The practical lesson for numerics:
oscillatory cancellation can look like convergence; check with a rigorous test
(Dirichlet for monotonic $\to0$ amplitudes) rather than eyeballing.

---

*Self-check: Q4, Q5, Q11 are all about the boundary cases of the p-test. Getting
$p>1$ vs $p<1$ correct with the direction of the inequality is the skill being
tested.*