# Differential Equations — Quiz (15 Questions with Worked Answers)

First-order linear, separation of variables, exact equations, existence and
uniqueness. The recurring theme: which method applies depends on structure, and
each method's assumptions are testable.

---

## Q1 — Separability and lost solutions
**Q.** Solve $y'=y^2$ on $[0,1]$ with $y(0)=1$. Does a solution exist on the
whole interval?

**A.** Separating: $\frac{dy}{y^2}=dx$ ⇒ $-\frac1y=x+C$ ⇒ $y=\frac{1}{C-x}$.
$y(0)=1$ gives $C=1$, so $y=\frac{1}{1-x}$, which blows up at $x=1$. **No
solution on $[0,1]$**; the maximal interval containing 0 is $[0,1)$. The
division by $y^2$ discarded the solution $y\equiv0$, which is real and must be
listed separately. Both omissions — dividing out a factor and assuming global
existence — are the classic errors in separation of variables.

---

## Q2 — Picard–Lindelöf in action
**Q.** For $y'=\sqrt{|y|}$, $y(0)=0$, does a unique solution exist?

**A.** $f(y)=\sqrt{|y|}$ is **not** Lipschitz at $0$: $\frac{|f(y)-f(0)|}{|y-0|}=\frac1{\sqrt{|y|}}\to\infty$.
Peano's existence theorem still gives local existence; uniqueness fails. Two
solutions: $y\equiv0$, and the "waiting then departing" family that stays 0 until
$t=c$ then follows $\frac{dy}{dt}=\sqrt y$ giving $y=(t-c)^2/4$ for $t\ge c$.
Every $c\in[0,1]$ gives a distinct solution — the hallmark of non-uniqueness at
a non-Lipschitz point.

---

## Q3 — Integrating factor method
**Q.** Solve $y'+2y=e^{-x}$ by integrating factor. Verify.

**A.** $P(x)=2$, $\mu(x)=e^{\int 2dx}=e^{2x}$. Multiply:
$(e^{2x}y)'=e^{x}$. Integrate: $e^{2x}y=e^x+C$ ⇒ $y=e^{-x}+Ce^{-2x}$.
Check: $y'=-e^{-x}-2Ce^{-2x}$, so $y'+2y=-e^{-x}-2Ce^{-2x}+2e^{-x}+2Ce^{-2x}=e^{-x}$. ✓
The general solution is particular + homogeneous, and superposition holds
because the equation is linear — that fact, not the derivation, is why the
"add the two pieces" step is legitimate.

---

## Q4 — Why integrating factors aren't arbitrary
**Q.** Suppose $\mu y$ turns $y'+P(x)y=Q(x)$ into an exact equation. What must $\mu$ satisfy?

**A.** Differentiate: $(\mu y)'=\mu' y+\mu y'$. For this to equal
$\mu P y+\mu Q$, the coefficients of $y$ must match:
$\mu'=\mu P$, i.e. $\mu'/\mu=P$ ⇒ $\ln\mu=\int P$ ⇒ $\mu=e^{\int P}$.
The integrating factor is **not** a free choice — any $\mu$ satisfying
$\mu'=\mu P$ is a valid multiple. This also explains why the method fails for
nonlinear equations: there is no linear operator to annihilate.

---

## Q5 — Exact equation test
**Q.** $M(x,y)y'+N(x,y)=0$ with $M=2xy+\sin y$, $N=x^2$. Is it exact, and what is the general solution?

**A.** $M_y=2x+\cos y$ and $N_x=2x$. Not equal ⇒ **not exact**. Look for an
integrating factor depending on $x$ alone:
$\mu=\frac{M_y-N_x}{N}=\frac{\cos y}{x^2}$, which depends on $y$, so that route fails.
Try $\mu(y)$: the condition is $\frac{N_x-M_y}{M}=\frac{-\cos y}{2xy+\sin y}$, which is not a function of $y$ alone. Instead, spot the derivative directly:
$\frac{d}{dx}(x^2-\cos y)=2x+\sin y\cdot y'=0$, i.e. exactly our equation.
So $x^2-\cos y=C$.
General point: writing $M\,dx+N\,dy=0$ as $dF(x,y)=0$ collapses the problem to
the implicit answer. The test
$\partial M/\partial y=\partial N/\partial x$ decides whether such a potential
$F$ exists on a simply connected region — and when it fails, an integrating
factor $\mu$ is sought so that $\mu M\,dx+\mu N\,dy$ passes the test.

---

## Q6 — Homogeneous substitution
**Q.** Solve $y'=\frac{x^2+y^2}{xy}$ for $x,y>0$.

**A.** Let $v=y/x$, so $y=vx$, $y'=v+xv'$. Substituting:
$v+xv'=\frac{x^2(1+v^2)}{x\cdot vx}=\frac{1+v^2}{v}$.
So $xv'=\frac{1+v^2-v^2}{v}=\frac1v$ ⇒ $xv'=1/v$ ⇒ $v\,dv=\frac{dx}{x}$
⇒ $\frac{v^2}{2}=\ln x+C$ ⇒ $v^2=2\ln x+C'$ ⇒
$y=x\sqrt{2\ln x+C'}$. The domain restriction $\ln x+C'\ge0$ is real: solutions
can terminate at finite $x$, never reaching an arbitrary initial condition.

---

## Q7 — Second-order homogeneous with repeated roots
**Q.** Solve $y''-4y'+4y=0$ and explain why the root 2 appears once.

**A.** Characteristic: $r^2-4r+4=(r-2)^2$, a double root $r=2$, giving
$y=(C_1+C_2x)e^{2x}$. Repeated roots get an extra factor of $x$ because the
general theory builds a solution space of dimension 2 and $e^{2x}$ alone spans
only 1. This is exactly the resonance case: the forcing would need to be $e^{2x}$
to produce $x^2$ growth. Distinct roots $r_1\ne r_2$ give $C_1e^{r_1x}+C_2e^{r_2x}$.

---

## Q8 — Forced oscillator and resonance
**Q.** Solve $y''+y=\cos x$ and describe the solution's growth.

**A.** Trial $y_p=A\cos x+B\sin x$. Then $y_p''+y_p=B\cos x-A\sin x$ (the
double cancellation reflects that $\cos x$ is a homogeneous solution, forcing
$A,B$ to match). LHS $=B\cos x-A\sin x=\cos x$ gives $B=1$, $-A=0$ ⇒ $A=0$,
but then $y_p''+y_p=0\ne\cos x$ — inconsistent. So the trial must be
multiplied by $x$: $y_p=\tfrac12 x\sin x$. General solution
$y=C_1\cos x+C_2\sin x+\frac12x\sin x$: **amplitude grows linearly**, resonance.
Detuning to $\cos(\omega x)$ with $\omega\ne1$ removes the growth and gives a
bounded steady state — the engineering reason to detune.

---

## Q9 — Reduction of order
**Q.** Given one solution of $y''+p(x)y'+q(x)y=0$, find a second without the
characteristic equation.

**A.** With $y_1$ known, set $y_2=v y_1$. Then $y_2''+py_2'+qy_2=v(y_1''+py_1'+qy_1)
+y_1v''+(2y_1'+py_1)v'=0$, so $v''+\left(2\frac{y_1'}{y_1}+p\right)v'=0$.
Let $w=v'$: $w'+(2y_1'/y_1+p)w=0$ ⇒
$w=C e^{-\int p\,dx}/y_1^2$, then $v=\int \frac{C e^{-\int p}}{y_1^2}dx$.
Useful when the coefficients are non-constant so the characteristic polynomial
doesn't apply — exactly the general non-constant-coefficient case where closed
forms are scarce.

---

## Q10 — Numerical method: Euler's error behaviour
**Q.** For $y'=y$, $y(0)=1$, step $h=0.1$, what does forward Euler give after one step?

**A.** $y_1=y_0+h\,y_0=1+0.1=1.1$ against the exact $e^{0.1}=1.10517$.
The local truncation error is $\frac{h^2}{2}y''(\xi)=\frac{0.01}{2}\cdot1.105\approx0.0055$,
matching the observed gap. Euler is **first-order**: halving $h$ halves the
error, so 10x speedup costs only 2x accuracy. RK4 is fourth-order: error
$\propto h^4$, so 10x speedup costs 10,000x accuracy. That trade is the whole
reason to bother with higher-order methods.

---

## Q11 — Stiff systems
**Q.** $y'=-1000(y-\cos x)+\sin x$, $y(0)=0$. What happens with explicit Euler, $h=0.1$?

**A.** The homogeneous mode decays like $e^{-1000t}$, timescale $10^{-3}$, far
faster than the step $h=10^{-1}$. Euler's amplification factor is
$1-1000h=-99$, whose magnitude $99>1$: the numerical solution **grows
explosively** even though the true solution decays. Stiffness requires either
an implicit scheme (backward Euler: $1/(1+1000h)=10^{-3}$, stable) or explicit
with $h\ll10^{-3}$. Stability, not accuracy, is the binding constraint here.

---

## Q12 — Existence vs uniqueness for a non-Lipschitz case
**Q.** $y'=y^{2/3}$, $y(0)=0$. Is the solution unique?

**A.** $f(y)=y^{2/3}$ has $f'(y)=\frac23y^{-1/3}$, unbounded at 0 ⇒ not
Lipschitz there, so uniqueness fails. Separating: $3y^{1/3}=x+C$ gives
$y=(\frac{x+C}{3})^3$, and the waiting-time solutions
$y=0$ for $x\le c$ then $y=((x-c)/3)^3$ for $x>c$ are all solutions through
$(0,0)$. Each is $C^1$ at $x=c$ (slope $\to0$), so $C^1$-smoothness of the
solution is *not* sufficient for uniqueness — Lipschitz in $y$ is the real
hypothesis.

---

## Q13 — Equilibrium solutions
**Q.** How do you avoid losing constant solutions when applying existence and
uniqueness to $y'=f(t,y)$?

**A.** Constant solutions satisfy $f(t,c)=0$ for all $t$; they are lost whenever
you divide by $f$ or by $y$. Algorithmically: solve $f(t,y^*)=0$ for
equilibria first, then apply existence–uniqueness locally *away* from roots of
$f$. E.g. $y'=y(1-y/t^2)$ has equilibria $y=0$ and $y=t^2$, both valid
nontrivial solutions invisible to separation of variables.

---

## Q14 — Linearization about a fixed point
**Q.** Linearize $y'=-y+y^3$ near $y=0$. Is the equilibrium stable?

**A.** $f(y)=-y+y^3$, $f'(0)=-1$. Perturbation $\eta$ obeys $\eta'=-\eta$, so
$\eta=\eta_0e^{-t}$: decaying. **Asymptotically stable.** Near $y=\pm1$,
$f'(1)=-1+3=2>0$ ⇒ perturbations grow ⇒ both are **unstable equilibria**.
The eigenvalue sign is the whole story — and note $y=0$ is locally attracting
but there are escape routes (for $|y|>1$ the cubic wins), so local stability
does not imply global stability.

---

## Q15 — Order reduction
**Q.** Why does a second-order equation need two initial conditions, and what
happens numerically if you supply only one?

**A.** The solution space is 2-dimensional: general solution has two constants.
Linearization produces a $2\times2$ system, and for IVP solvability you need the
vector $(y_0,y_0')$. The boundary value problem $y''+q(x)y=0$, $y(0)=a$, $y(1)=b$
instead needs a **shooting** parameter $y'(0)$ tuned until $y(1)=b$ —
that is the boundary value formulation, where a single initial condition cannot
determine the solution.

---

*Self-check: Q1, Q2, Q11 and Q12 all feature an existing-but-not-unique or
exploding solution. Recognising those three failure signatures (lost constants,
non-Lipschitz, stiffness) is the real skill.*