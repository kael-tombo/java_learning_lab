# Limits and Continuity — Quiz (15 Questions with Worked Answers)

Questions 1–4 check computation. The rest are about *why* a limit exists and which
hypotheses an argument actually needs — the place where real errors happen.

---

## Q1 — Why direct substitution fails but factorization saves you
**Q.** Evaluate $\lim_{x\to 2}\frac{x^2-4}{x-2}$. Why is the answer not "undefined"?

**A.** $4$. Substitution gives $0/0$, an *indeterminate form*, not a value. The
limit laws only pass limits through a quotient when the denominator limit is
non-zero; here it is $0$, so the laws are silent. But
$x^2-4=(x-2)(x+2)$, and for $x\neq 2$ the quotient equals $x+2$. Since
$\lim_{x\to2}(x+2)=4$, the squeeze of the punctured function gives 4. $0/0$
signals "simplify, then substitute" — it never means the limit fails.

---

## Q2 — Limit exists, value does not
**Q.** $f(x)=\frac{\sin x}{x}$ for $x\neq0$, $f(0)=0$. Is $f$ continuous at 0?

**A.** $\lim_{x\to0}\frac{\sin x}{x}=1$ but $f(0)=0$, so $f$ is **not**
continuous at 0; it has a removable discontinuity. A function can have a finite
limit at a point while being undefined or differently defined there. Continuity
at $a$ is a three-part claim: $f(a)$ exists, $\lim_{x\to a}f(x)$ exists, and
they are equal. Failing any part breaks continuity.

---

## Q3 — Proving $\lim_{x\to0}\sin x/x = 1$ without assuming it
**Q.** Give the squeeze-theorem argument, and name the geometric inequality that carries it.

**A.** For $0<x<\pi/2$ the unit circle gives $\sin x < x < \tan x$. Dividing:
$\cos x < \frac{\sin x}{x} < 1$. Both bounds tend to 1, so by squeeze the middle
term tends to 1. For $x<0$ use oddness. The one-sided squeeze is the whole
proof; no series and no L'Hôpital. Crucially the *unit-circle inequality is
assumed*, not derived from the limit — deriving it from $\sin x/x\to1$ and
using it to prove the limit is circular.

---

## Q4 — One-sided limits
**Q.** Evaluate $\lim_{x\to0^+}\frac{\sin x}{x}$ and $\lim_{x\to0^-}\frac{\sin x}{x}$.

**A.** Both are $1$. The one-sided limits agree even though $f$ is discontinuous
at 0 (Q2). One-sided limits are **never** equal to the two-sided limit by
definition; they coincide whenever the two-sided limit exists. $f(x)=1/x$ shows
the contrast: left limit $-\infty$, right $+\infty$, so no two-sided limit
exists even though each side is perfectly well behaved.

---

## Q5 — Counter-example: IVT without continuity
**Q.** Does $f(x)=1/x$ on $[-1,1]$ take the value $1/2$? $f(-1)=-1$, $f(1)=1$, and $1/2$ lies between. Why no contradiction?

**A.** It does take the value $1/2$ — at $x=2$, which is outside $[-1,1]$. On
$[-1,1]$ the function is not defined at 0 and its image is two disjoint pieces,
so no intermediate value is attained. The Intermediate Value Theorem needs
continuity on the closed interval precisely to prevent this "jump past" of
values. Sign change at the endpoints alone proves nothing.

---

## Q6 — Continuity is not uniform continuity
**Q.** Both $f(x)=x^2$ and $f(x)=\sin x$ are continuous on $\mathbb{R}$. Which is uniformly continuous?

**A.** $\sin x$ is, $x^2$ is not. Uniform continuity demands one $\delta$ that
works for *all* $x,y$. For $x^2$ fix $\varepsilon=1$ and take $x=n$,
$y=n+\delta/n^2$: then $|x-y|=\delta/n^2<\delta$ for every $\delta>0$ and every
$n$, yet $|(n+\delta/n^2)^2-n^2|=2\delta+\delta^2/n^4\to$ stays above 1 by
picking $\delta>1/2$. $x^2$ escapes to infinity, so the local slope grows without
bound. On a compact interval every continuous function is uniformly continuous
(Heine–Cantor) — the failure is purely about unbounded domains.

---

## Q7 — The sequential criterion
**Q.** A function $f$ has $\lim_{x\to a}f(x)=L$ if and only if $\lim_{n\to\infty}f(x_n)=L$ for **every** sequence $x_n\to a$ with $x_n\neq a$. What does this buy you?

**A.** It converts a $\forall\varepsilon>0\,\exists\delta$ definition into a
statement about sequences, which is how you *disprove* things: to show the limit
is not $L$, exhibit one sequence $x_n\to a$ whose images fail to tend to $L$.
For $f(x)=\sin(1/x)$, take $x_n=1/(\pi/2+2\pi n)$ — images are 1 — and
$y_n=1/(3\pi/2+2\pi n)$ — images are $-1$. Two sequences, two limits, so the
limit does not exist. No $\varepsilon$–$\delta$ fiddling needed.

---

## Q8 — Continuity of composite and reciprocal
**Q.** If $g$ is continuous at $a$ and $f$ at $g(a)$, is $f\circ g$ continuous at $a$? Give a case where $f$ is continuous but $f\circ g$ is not.

**A.** Yes, by the composition theorem. Counter-example: $f(t)=t^2$ continuous
everywhere, $g(x)=1/x$ continuous on $\mathbb{R}\setminus\{0\}$; but
$f\circ g=1/x^2$ is not even defined at 0, so it cannot be continuous there. The
theorem requires $g$ continuous at $a$ — including $g(a)$ existing. The subtle
variant: $f(t)=\sqrt t$ continuous on $[0,\infty)$, $g(x)=x^2$ continuous, but
$\sqrt{x^2}=|x|$ is continuous everywhere, while $\sqrt{\phantom{x}}$ composition
preserves *relative* continuity only when $f$'s domain stays fixed.

---

## Q9 — Infinite limits and horizontal asymptotes
**Q.** $\lim_{x\to\infty}\frac{3x^2-x}{x^2+5x-7}$. A student divides by $x$ instead of $x^2$ and gets "infinity". What went wrong?

**A.** The limit is $3$, so $y=3$ is a horizontal asymptote. Dividing by $x$ gives
$\frac{3-1/x}{1+5/x-7/x^2}$, which still diverges — but the correct scaling is
by the highest power of $x$ in the denominator. The rule: divide by the dominant
term of the denominator. "Infinity" is never a real answer to a limit; it
describes unbounded growth, and a limit that equals infinity means the function
grows without bound, not that the limit is a number.

---

## Q10 — $\varepsilon$–$\delta$ for a genuinely tricky limit
**Q.** Prove $\lim_{x\to3}\frac{x^2-9}{x-3}=6$ using the $\varepsilon$–$\delta$ definition.

**A.** $\left|\frac{x^2-9}{x-3}-6\right| = |x+3-6| = |x-3|$. Given $\varepsilon$,
choose $\delta=\varepsilon$; then $0<|x-3|<\delta$ forces the difference
$<varepsilon$. Note how trivial the $\varepsilon$–$\delta$ proof is once the
function is simplified — which is why order of operations matters. Attempting the
proof on the unsimplified fraction forces you to bound $x$ itself (say
$\delta\le1$) and the algebra gets worse for no benefit.

---

## Q11 — Limits commute with continuous operations
**Q.** If $f,g\to L,M$ and $h=f+g$, does $h\to L+M$? What if only $f\to L$ exists?

**A.** Yes: limit laws hold for all limit types (finite, infinite, one-sided)
provided the *premises* are meaningful. If only $f\to L$ exists and $g$ is
oscillating, $f+g$ generally has no limit. Concrete case: $f(x)=x\to0$ and
$g(x)=\sin(1/x)$, then $f+g=\sin(1/x)+\varepsilon$ still fails to converge.
Law of sum: "$\infty-\infty$" is an **indeterminate form**, not infinity —
$3x-x$ and $x-x^2$ both diverge but in opposite directions.

---

## Q12 — Fixed points
**Q.** Compute $\lim_{n\to\infty}x_n$ for $x_{n+1}=(1+x_n)/2$, $x_0=0$.

**A.** If the sequence converges to $L$, then $L=(1+L)/2$, so $L=1$. This is a
*necessary* condition, not a proof of convergence — many sequences fail to
converge while satisfying the fixed-point equation (e.g. $x_{n+1}=2x_n$ has only
fixed point 0 but diverges). Verify convergence separately: write
$x_{n+1}-1=\frac{x_n-1}{2}$, so $x_n-1=(x_0-1)2^{-n}=-\tfrac{1}{2^n}$, giving
$x_n=1-2^{-n}\to1$. Contraction mapping: $|g'(x)|=1/2<1$ also certifies it.

---

## Q13 — Where the product law needs a nonzero limit
**Q.** $f(x)=x$, $g(x)=\sin(1/x)$. Compute $\lim_{x\to0}f(x)g(x)$. Why can't you just use the product law?

**A.** The product is $x\sin(1/x)\to0$, by squeeze: $|x\sin(1/x)|\le|x|\to0$.
The product law cannot be applied because $\lim g(x)$ does not exist at all, so
the premise fails. This is the general lesson: algebraic limit rules are
*conditional* on the constituent limits existing. When one factor tends to 0 and
the other is bounded, squeeze replaces the product law.

---

## Q14 — Continuity of a piecewise function
**Q.** $f(x)=\begin{cases}x^2 & x<2\\ 8 & x\ge2\end{cases}$. Is $f$ continuous at $x=2$?

**A.** Yes. $\lim_{x\to2^-}x^2=4$, $\lim_{x\to2^+}8=8$, both equal $f(2)=8$,
and the two-sided limit exists and equals the function value. Change one
constant to 9 and continuity fails on the right. A common student error is to
evaluate only the left branch — continuity requires **both** one-sided limits to
agree with $f(a)$.

---

## Q15 — Continuity of a rational function
**Q.** $r(x)=p(x)/q(x)$. Precisely where is $r$ continuous, and what is the
"hole" phenomenon?

**A.** Continuous at every $a$ with $q(a)\neq0$ (quotient law applied to
polynomials). At a root of $q$, $r$ is undefined; if $a$ is a common root of $p$
and $q$ the hole is *removable* (cancel first, then extend — Q2), and otherwise
it is a vertical asymptote. Distinguish by evaluating the limit of the reduced
expression: finite ⇒ hole, infinite ⇒ asymptote. For $p=x^2-4$, $q=x-2$ the
hole is at 2; for $p=1$, $q=x-2$ the asymptote is at 2.

---

*Self-check: you should be able to justify Q3, Q5, Q7, and Q12 without writing
anything down beyond the key inequality.*