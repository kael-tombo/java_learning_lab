# Derivative Rules — Quiz (15 Questions with Worked Answers)

Most of these are about the *conditions* a rule needs. A rule applied outside its
hypotheses is not a small error — it silently produces a wrong number.

---

## Q1 — Chain rule on a nested composite
**Q.** Differentiate $y=\sin^3(\cos 2x)$, i.e. $y=(\sin(\cos 2x))^3$.

**A.** Three layers, three multiplications:
$y'=3\sin^2(u)\cos(u)\cdot(-2\sin 2x)$ where $u=\cos 2x$.
So $y'=-6\sin^2(\cos 2x)\cos(\cos 2x)\sin 2x$.
The common error is treating $\sin^3$ as $\sin(3x)$; that is a different
function. Chain rule counts **levels**, not factors.

---

## Q2 — Product rule against the quotient rule
**Q.** Differentiate $f(x)=\dfrac{x^2+1}{x-1}$ two ways and check they agree.

**A.** Quotient rule:
$f'=\dfrac{2x(x-1)-(x^2+1)\cdot1}{(x-1)^2}=\dfrac{x^2-2x-1}{(x-1)^2}$.
Product rule: $f=(x^2+1)(x-1)^{-1}$ gives
$f'=2x(x-1)^{-1}-(x^2+1)(x-1)^{-2}=\dfrac{2x(x-1)-(x^2+1)}{(x-1)^2}$ — identical.
Whenever you rewrite a quotient as a negative power, the two rules must agree;
disagreement means an algebra slip, not a conceptual difference. The quotient
rule is literally the product rule for $u\cdot v^{-1}$.

---

## Q3 — Logarithmic differentiation
**Q.** Find $d/dx$ of $y=x^x$ for $x>0$.

**A.** Neither power nor exponential rule applies directly. Take logs:
$\ln y = x\ln x$, so $y'/y=\ln x+1$, giving
$y'=x^x(\ln x+1)$.
Generalization: $u(x)^{v(x)}$ with $v$ variable uses
$\dfrac{d}{dx}u^{v}=u^{v}\left(v'\ln u+v\dfrac{u'}{u}\right)$. This is why
$2^x$ and $x^2$ have different derivative rules.

---

## Q4 — Implicit differentiation
**Q.** Differentiate $x^2+y^2=25$ and give the slope at $(3,4)$.

**A.** $2x+2y\dfrac{dy}{dx}=0$, so $\dfrac{dy}{dx}=-\dfrac{x}{y}$. At $(3,4)$:
$-\tfrac34$. The circle is not a function of $x$ globally, but each branch
is, and $\partial y/\partial x$ refers to that local branch. Note $y=0$
(vertical tangent) makes the formula blow up — correctly signalling a point
where $y$ is not locally a function of $x$.

---

## Q5 — Differentiation is not always valid
**Q.** Where is $f(x)=|x|$ differentiable, and what is $f'(0)$?

**A.** Differentiable everywhere except $0$. For $x>0$, $f'=1$; for $x<0$,
$f'=-1$. The left and right derivatives at 0 are $-1$ and $1$, so
$f'(0)$ does not exist — the graph has a corner. This is the cheapest
counter-example to "differentiability and continuity are the same thing":
differentiable ⇒ continuous (proved from the difference quotient), but not
conversely. Corner here, $|x|$; cusp like $x^{2/3}$ at 0; vertical tangent like
$x^{1/3}$ — three distinct failure shapes, all continuous.

---

## Q6 — Higher derivatives via logarithmic differentiation
**Q.** Compute $\dfrac{d^2}{dx^2}$ of $y=e^{2x}$ and of $y=\ln x$.

**A.** $y''=4e^{2x}$ and $y''=-x^{-2}$. For $\ln x$ the useful identity is
$(\ln x)'=1/x$ and its second derivative is $-1/x^2$: derivatives of logarithms
always land in rational functions, which is why $\int\ln x\,dx=x\ln x-x$.

---

## Q7 — Where is $f(x)=1/x$ differentiable?
**Q.** $f$ is undefined at 0. Does the derivative formula still apply "everywhere else", and does Darboux allow a jump?

**A.** $f'(x)=-1/x^2$ for $x\neq0$. By Darboux's theorem derivatives satisfy
the intermediate value property, so a derivative can never jump. Since
$f'<0$ on both sides of 0, the discontinuity in $f'$ itself is a vertical
asymptote, not a jump. Darboux also immediately kills any "derivative with
jump discontinuities" proposal, and it rules out pointwise-defined piecewise
derivatives whose pieces don't glue.

---

## Q8 — Derivative of an inverse function
**Q.** Given $f(1)=3$ and $f'(1)=2$, find $(f^{-1})'(3)$. More generally?

**A.** $(f^{-1})'(y)=\dfrac{1}{f'(f^{-1}(y))}$, so $(f^{-1})'(3)=1/2$. Derivation:
$f(f^{-1}(y))=y$, so $f'(\cdot)\cdot(f^{-1})'=1$. Requires $f$ locally
invertible, i.e. $f'(a)\neq0$ — the inverse function theorem. Concretely:
$f(x)=x^2$ on $x>0$ has $f'(1)=2$ ⇒ inverse derivative $1/2$ at $y=1$;
on $x<0$ the sign flips. Same $f'$, different branch, different inverse slope.

---

## Q9 — Leibniz rule for repeated differentiation
**Q.** Compute the second derivative of $h(x)=x^2\sin x$.

**A.** Product rule twice. $h'=2x\sin x+x^2\cos x$.
$h''=2\sin x+2x\cos x+2x\cos x-x^2\sin x = 2\sin x+4x\cos x-x^2\sin x$.
Leibniz generalizes this: $D^n(uv)=\sum_k\binom{n}{k}(u^{(k)})(v^{(n-k)})$.
The binomial coefficients appearing here are exactly why Leibniz is the natural
rule for product-type generating functions.

---

## Q10 — Differentiate a piecewise function that hides a jump
**Q.** $f(x)=x^2$ for $x\le1$, and $f(x)=3x-2$ for $x>1$. Differentiate at $x=1$.

**A.** $f(1)=1$ from the first branch; right-hand limit $3(1)-2=1$, so $f$ is
continuous. But $f'_-(1)=2$ and $f'_+(1)=3$: not differentiable. Continuity is
necessary but not sufficient — you must check the value at the join *and* both
slopes. The point of the check is that a continuous piecewise function whose
branches disagree in slope is differentiable exactly when both the values and
the slopes match.

---

## Q11 — The chain rule and the derivative of $e^{-x}$
**Q.** Compute $\dfrac{d}{dx}e^{-x}$ and $\dfrac{d}{dx}\ln(\sin x)$.

**A.** $e^{-x}\cdot(-1)=-e^{-x}$. For $\ln(\sin x)$:
$\dfrac{\cos x}{\sin x}=\cot x$. The two identities worth memorizing:
$\dfrac{d}{dx}e^{g}=e^{g}g'$ and $\dfrac{d}{dx}\ln g=\dfrac{g'}{g}$.
$\ln(\sin x)$ is only defined where $\sin x>0$; on intervals where $\sin x<0$
the real function is undefined, which the formula's domain reflects.

---

## Q12 — Implicit differentiation where $y$ appears twice
**Q.** Differentiate $x^2+y^2=2xy$ and identify the curve.

**A.** $2x+2yy'=2y+2xy'$, so $y'(y-x)=y-x$ and $y'=1$ wherever $y\neq x$.
The curve is $y=x$ (a straight line) together with the isolated point $(0,0)$.
At $(0,0)$ the division by $y-x$ is illegal — the implicit function theorem
fails there, and that single point is exactly the extra component.

---

## Q13 — Differentiating $x^{1/3}$ at 0
**Q.** Compute $f'(x)=x^{1/3}$ for $x\neq0$. Is $f$ differentiable at 0?

**A.** $f'(x)=\tfrac13x^{-2/3}$, which blows up as $x\to0$ from both sides.
Directly: $\lim_{h\to0}\frac{h^{1/3}-0}{h}=\lim h^{-2/3}=+\infty$. So $f$ is
continuous at 0 with an infinite derivative — a vertical tangent, not a cusp.
Compare $x^{2/3}$ at 0: $\lim h^{-1/3}$ has opposite signs on the two sides, so
that is a cusp. Both are continuous; only one has a corner.

---

## Q14 — Verify the product rule from first principles
**Q.** Using $\lim_{h\to0}\frac{(f+h)(g+h)-fg}{h}$, recover $f'g+fg'$.

**A.** Expand numerator: $f(x+h)g(x+h)-f(x)g(x) = f(x+h)[g(x+h)-g(x)]+g(x)[f(x+h)-f(x)]$.
Divide by $h$ and take the limit:
$f(x)\lim\frac{g(x+h)-g(x)}{h}+g(x)\lim\frac{f(x+h)-f(x)}{h}=fg'+gf'$.
The algebraic trick is writing the cross term $h\,g(x)$ on one side so it can be
separated — proof by splitting, the standard route to every differentiation rule.

---

## Q15 — Differentiability on a domain with no interior
**Q.** $f:[0,\infty)\to\mathbb{R}$, $f(x)=\sqrt x$. What is $f'$ at 0?

**A.** Under the standard two-sided definition $f'$ does not exist at 0, since the
domain has nothing to the left. With the endpoint convention (one-sided
derivative) the limit is $\lim_{h\to0^+}\frac{\sqrt h}{h}=h^{-1/2}=\infty$: no
finite derivative, so not differentiable even one-sided, though it is
continuous. The endpoint case is a real gap in the naive
"left derivative = right derivative" test — on a closed interval, endpoints must
be handled separately.

---

*Self-check: Q5, Q7 and Q15 each ask for a counter-example or a hypothesis, not a
computation. If you can produce a second counter-example for each, you understand
the rules rather than memorizing them.*