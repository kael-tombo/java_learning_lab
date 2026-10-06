# Vector Calculus — Quiz (15 Questions with Worked Answers)

Line and surface integrals, Green's theorem, Stokes' theorem, the divergence
theorem, and conservative fields. The recurring theme: orientation signs, and
the fact that "closed" is doing real work.

---

## Q1 — Line integral of a scalar vs a vector field
**Q.** Distinguish $\int_C f\,ds$ from $\int_C \mathbf{F}\cdot d\mathbf{r}$ for
$\mathbf{F}=P\,dx+Q\,dy$.

**A.** $\int_C f\,ds=\int f(\mathbf{r}(t))\|\mathbf{r}'(t)\|dt$: arc-length
weighted, sign-free, **independent of the parametrization's orientation**.
$\int_C P\,dx+Q\,dy$ is a circulation: orientation-dependent, and flipping the
direction flips the sign. Example $f=1$ over the unit circle: the scalar integral
is the circumference $2\pi$ either way; $\oint(x\,dy-y\,dx)=2\pi$ CCW and
$-2\pi$ CW. Confusing these two is the most common conceptual error in the lab.

---

## Q2 — Green's theorem applied
**Q.** Evaluate $\oint_C (x\,dy-y\,dx)$ over the unit circle, CCW.

**A.** By Green's theorem with $P=-y$, $Q=x$:
$\oint_C P\,dx+Q\,dy=\iint_D\left(\frac{\partial Q}{\partial x}-\frac{\partial
P}{\partial y}\right)dA=\iint_D(1+1)dA=2\cdot\pi=2\pi$.
Directly: parametrize $x=\cos t$, $y=\sin t$, $0\le t\le2\pi$; then
$x\,dy-y\,dx=2\,dt$, giving $2\pi$.
**Orientation is built into the theorem**: for CW traversal the answer is $-2\pi$.

---

## Q3 — Green's theorem has hypotheses
**Q.** Green's theorem needs $C$ positively oriented and $D$ simply connected.
Give a concrete counterexample.

**A.** On the annulus $1\le r\le2$ with a hole, the curve is not the boundary of
a simply connected region, so Green's theorem can fail. Explicitly,
$\oint_C\left(-\frac{y}{r^2}dx+\frac{x}{r^2}dy\right)$ around the annulus
boundary: the corresponding field is the gradient of $\arctan(y/x)$ (up to
sign), so on each component of the boundary the integral is $2\pi$ — total $0$
for the whole boundary, whereas computing the two "curl" values over the region
gives $\iint(\ldots)$ that does not reproduce it. Practical rule: cut the region
along a slit so it becomes simply connected, apply the theorem, and let the
contributions on the two sides of the slit cancel. This is the standard
"cut-and-sew" trick for multiply connected domains.

---

## Q4 — Conservative fields
**Q.** Is $\mathbf{F}=(2xy+\cos y,\ x^2+x\sin y)$ conservative on $\mathbb{R}^2$?

**A.** $P_y=2x-\sin y$, $Q_x=2x+\sin y$: not equal ⇒ **not conservative**.
Comparison with Q5 of the differential-equations lab is instructive: there the
equation was $M y' + N = 0$ with $M=2xy+\sin y$, $N=x^2$. Here the $y$ in the
second component is $x^2$, and the roles of the $\sin$ and $\cos$ terms are
swapped. Contrast the conservative field $(2xy+\sin y,\ x^2+\cos y\cdot 1)$:
$P_y=2x+\cos y=Q_x$, and it is exactly $\nabla(x^2y+\sin y)$. Same function
grammar, different answer — check the mixed-partial condition every time.

---

## Q5 — The test requires simple connectivity
**Q.** Is $\mathbf{F}=(-y/r^2,\ x/r^2)$ conservative on $\mathbb{R}^2\setminus\{0\}$?
On $\mathbb{R}^2$?

**A.** On the punctured plane: $P_y=\partial_y(-y/r^2)=(y^2-x^2)/r^4$ and
$Q_x=\partial_x(x/r^2)=(y^2-x^2)/r^4$, equal away from the origin, so the
curl-free test **passes** — yet the field is not conservative, because
$\oint_{|r|=1}(x\,dy-y\,dx)/r^2=\oint d\theta=2\pi\ne0$. The test only
guarantees a potential on **simply connected** domains; $\mathbb{R}^2\setminus\{0\}$ is not.
On $\mathbb{R}^2$ the field isn't even defined, so the question is moot there.
This is the canonical example: curl-free $\nRightarrow$ conservative without
simple connectivity.

---

## Q6 — Potential function, both directions
**Q.** Given $F=P\,dx+Q\,dy$ with $P=2x$, $Q=2y$, find the potential and the
work along the path $x=t^2,y=t$, $0\le t\le1$.

**A.** $\phi=x^2+y^2$. The path $(t^2,t)$ runs from $(0,0)$ to $(1,1)$, so
work $=\phi(1,1)-\phi(0,0)=2$. Direct verification: $dx=2t\,dt$, $dy=dt$,
$\int_0^1\left(2t^2\cdot2t+2t\cdot1\right)dt=\int_0^1(4t^3+2t)dt=1+1=2$.
Exact match — path-independence holds, so any other path gives 2 as well.

---

## Q7 — Surface integral via projection
**Q.** Flux of $\mathbf{F}=(x,y,0)$ through the hemisphere $z=\sqrt{1-x^2-y^2}$,
outward.

**A.** Divergence theorem: $\nabla\cdot\mathbf{F}=\partial_xx+\partial_yy+0=2$,
so the total flux through the closed surface (curved hemisphere + base disk) is
$2\cdot\mathrm{Vol}(\text{half unit ball})=2\cdot\frac{2\pi}{3}=\frac{4\pi}{3}$.
On the disk $z=0$ the outward normal is $-\hat z$ and
$\mathbf{F}\cdot\hat n=(x,y,0)\cdot(0,0,-1)=0$, so the hemisphere alone carries
the full $\frac{4\pi}{3}$.
Direct check with the graph formula $\hat n\,dS=(x/z,y/z,1)\,dx\,dy$:
$\mathbf{F}\cdot\hat n=r^2/z$, hence
$2\pi\int_0^1\frac{r^3}{\sqrt{1-r^2}}\,dr$. With $u=1-r^2$, $r\,dr=-\frac{du}{2}$:
$\frac12\int_0^1(1-u)u^{-1/2}du=\frac12\left(2-\frac23\right)=\frac23$, giving
$2\pi\cdot\frac23=\frac{4\pi}{3}$. ✓
The graph route needs a substitution to handle the integrable blow-up at $r=1$;
the closed-surface route has no such term. That is the practical argument for
the divergence theorem whenever a surface is difficult to parametrise.

---

## Q8 — Divergence theorem with an excluded ball
**Q.** Flux of $\mathbf{F}=\frac{\mathbf{r}}{r^3}=\frac{(x,y,z)}{r^3}$ through a
closed surface enclosing the origin.

**A.** $\nabla\cdot\frac{\mathbf{r}}{r^3}=0$ everywhere except $r=0$, so
divergence theorem applied naively gives flux $0$ — wrong, since the real flux is
$4\pi$ (Gauss's law). Fix: excise a small ball $B_\varepsilon$, whose flux is
$4\pi$ (outward from the small ball, inward from the big one). Then
$\oint_{\text{outer}}=\oint_{\text{small}}=4\pi$. Deleting a measure-zero
singularity is not free: the field is not defined there, so the theorem's
hypothesis ($C^1$ on a neighbourhood of $V$) fails. Same family of error as Q3.

---

## Q9 — Stokes' theorem, orientation
**Q.** Compute $\oint_{\partial S}\mathbf{F}\cdot d\mathbf{r}$ for
$\mathbf{F}=(-y,x,0)$ over the unit disk $S$, with $\hat n=+\hat z$.

**A.** $\nabla\times\mathbf{F}=(0,0,2)$ ⇒
$\iint_S 2\,dA=2\pi$. Direct: $\oint(-y\,dx+x\,dy)=2\oint d\theta=2\pi$.
For $\hat n=-\hat z$ both sides flip sign. Stokes ties "boundary of boundary =
0" to $\nabla\cdot(\nabla\times F)=0$ — the algebraic-topological fact that
the curl's divergence vanishes.

---

## Q10 — Stokes in a nontrivial case
**Q.** $\mathbf{F}=(y z,\ x z,\ x^2+y^2)$ over the paraboloid $z=x^2+y^2\le1$
with upward normal.

**A.** Curl: $\partial_y F_z-\partial_z F_y=2y-z$; $\partial_z F_x-\partial_x F_z=y-2x$;
$\partial_x F_y-\partial_y F_x=x-(-x)=2x$.
Using Stokes, replace $S$ by the flat disk $z=0$ with the same boundary — the
flux there is $\iint(2y-0)\,dx\,dy+\iint(0-2x)\,dx\,dy=0$ by symmetry.
So $\oint\mathbf{F}\cdot d\mathbf{r}=0$. The *substitution of a simpler surface*
with identical boundary is the single most useful practical move in Stokes.

---

## Q11 — Parameterised surface integrals
**Q.** Surface area of the Möbius strip parametrised
$\mathbf{r}(u,v)=(1+v\cos\frac u2,\ v\sin\frac u2,\ u)$, $0\le u<2\pi$, $-\!1\le v\le1$.

**A.** $\mathbf{r}_u=(-\frac v2\sin\frac u2,\ \frac v2\cos\frac u2,\ 1)$,
$\mathbf{r}_v=(\cos\frac u2,\ \sin\frac u2,\ 0)$.
$|\mathbf{r}_u\times\mathbf{r}_v|=|\mathbf{r}_v|=1$, so area $=2\pi\cdot2=4\pi$ —
the famous single-sided property showing the "width" parameter wraps twice.
Note $|u|<2\pi$ must be enforced: at $u=2\pi$ the strip closes with a twist and
the parameterisation is not injective there, so the area formula would
double-count the boundary.

---

## Q12 — The divergence-free / curl-free distinction
**Q.** If $\nabla\cdot\mathbf{F}=0$ everywhere, is flux through every closed
surface zero? If $\nabla\times\mathbf{F}=0$, is the line integral around every
closed curve zero?

**A.** $\nabla\cdot F=0$ ⇒ flux zero through every closed surface **provided the
field is $C^1$ on a neighbourhood of the enclosed region** (Q8 is the failure
case). $\nabla\times F=0$ ⇒ line integrals zero **only on simply connected
domains** (Q5). Both theorems have hypotheses that are silently dropped in
practice; both failures are topology, not calculus.

---

## Q13 — Circulation, flux, and physical meaning
**Q.** For the ideal fluid velocity field $\mathbf{v}$, what do $\nabla\times
\mathbf{v}$ and $\nabla\cdot\mathbf{v}$ physically represent?

**A.** $\nabla\times\mathbf{v}=2\boldsymbol\omega$ is twice the local angular
velocity (vorticity): it measures circulation, and nonzero curl in an
irrotational ideal fluid means boundary layers must form somewhere to satisfy
no-slip — D'Alembert's paradox. $\nabla\cdot\mathbf{v}$ is the local rate of
volume expansion (compressibility); zero divergence plus no-slip is what makes
the drag paradox possible. Both are gauge-invariant local quantities and
together with boundary conditions determine the flow uniquely (Kelvin's
theorem, Helmholtz's vortex theorems).

---

## Q14 — Signs, orientations, and unit normals
**Q.** State the two orientation conventions precisely.

**A.** For a closed surface $S=\partial V$, the outward normal points away from
$V$; divergence theorem then gives positive flux for a source field (Q7, Q8).
For an open surface $S$ with boundary $\partial S$, Stokes' induced orientation is
given by the right-hand rule: fingers follow $\partial S$, thumb gives $\hat n$.
Changing $\hat n$ changes the sign of the resulting integral, never its magnitude.
Mixing the two conventions produces a minus sign that is very hard to spot later
— fix one convention and state it.

---

## Q15 — When all three theorems are unavailable
**Q.** $\mathbf{F}=(x e^{y},\, y e^{x},\, z^2)$ on the torus
$x=(2+\cos u)\cos v$, $y=(2+\cos u)\sin v$, $z=\sin u$. Is the flux zero?

**A.** No reason to expect zero. $\nabla\cdot\mathbf{F}=e^y+e^y+2z=2e^y+2z$, and
under the torus symmetry $z\mapsto -z$ (achieved by $u\mapsto -u$) the $2z$
term cancels while the $e^y$ terms double — so the flux is not zero. The point
of the question: the divergence theorem *does* apply (the field is $C^1$ on a
neighbourhood of the solid torus), it just does not evaluate to $0$. When a
surface is too hard to parameterise, the theorem converts the computation into
a volume integral — which is what finite-element and finite-volume methods are
built on.

---

*Self-check: Q3, Q5, Q8 and Q12 all hinge on a hypothesis that is silently
dropped in the textbook version. Being able to state each hypothesis out loud is
the difference between applying these theorems and guessing.*