# Integration Techniques — Quiz (15 Questions with Worked Answers)

Substitution, by parts, partial fractions, trig substitution. The exam-worthy
question is always "does this integral have an elementary antiderivative?" and
the reasoning behind each technique choice.

---

## Q1 — Recognizing when substitution will not work
**Q.** Why does $\int\frac{dx}{x^2+1}$ resist the $u$-substitution attempt while
$\int\frac{2x\,dx}{x^2+1}$ succeeds?

**A.** A substitution works when you can find an inner function whose derivative
appears as a factor: in the second, $u=x^2+1$, $du=2x\,dx$, giving $\ln(x^2+1)+C$.
In the first, $x^2+1$ is irreducible over $\mathbb{R}$ and no linear factor
$u'=g'$ pairs with it. The first instead needs a trig substitution
(Q3). The skill is recognizing the *degree/parity pattern* that predicts which
tool applies.

---

## Q2 — By parts with a recurrence
**Q.** Compute $I_n=\int_0^{\pi/2}\sin^n x\,dx$ and derive the recurrence
$I_n=(n-1)/n\cdot I_{n-2}$.

**A.** By parts with $u=\sin^{n-1}x$, $dv=\sin x\,dx$:
$I_n=\left[-\sin^{n-1}x\cos x\right]_0^{\pi/2}+(n-1)\int_0^{\pi/2}\sin^{n-2}x\cos^2x\,dx$
$=(n-1)\left(I_{n-2}-I_n\right)$ ⇒ $I_n=\frac{n-1}{n}I_{n-2}$.
Base cases: $I_0=\frac{\pi}{2}$, $I_1=1$. So $I_{2k}=\frac{(2k-1)!!}{(2k)!!}\frac{\pi}{2}$ and
$I_{2k+1}=\frac{(2k)!!}{(2k+1)!!}$. Each recurrence step *lowers* the exponent —
that is what makes by parts viable on otherwise stubborn integrals.

---

## Q3 — Trig substitution map
**Q.** Which substitution for (a) $\sqrt{a^2-x^2}$, (b) $\sqrt{x^2-a^2}$, (c) $\sqrt{a^2+x^2}$?

**A.** (a) $x=a\sin\theta$, (b) $x=a\sec\theta$, (c) $x=a\tan\theta$.
The mnemonic: recall the right triangle whose side ratios are the relevant
identity. $\int\frac{dx}{\sqrt{a^2-x^2}}=\arcsin(x/a)+C$ — check with $a=1$.
The substitution is worth it only when the radical survives; if after
substitution the radical cancels trivially, an $u$-substitution was the
cheaper route.

---

## Q4 — Partial fractions: setup matters
**Q.** Decompose $\dfrac{1}{x(x+1)(x+2)}$ over the reals.

**A.** $\dfrac{A}{x}+\dfrac{B}{x+1}+\dfrac{C}{x+2}$. Cover-up: $x\to0$ gives
$A=\frac{1}{1\cdot2}=\frac12$; $x\to-1$ gives $B=\frac{1}{(-1)(1)}=-1$;
$x\to-2$ gives $C=\frac{1}{(-2)(-1)}=\frac12$.
So $\frac{1}{x(x+1)(x+2)}=\frac{1}{2x}-\frac{1}{x+1}+\frac{1}{2(x+2)}$,
which integrates to $\frac12\ln|x|-\ln|x+1|+\frac12\ln|x+2|+C$.
The cover-up method is only valid for *linear* factors; irreducible quadratics
need the undetermined-coefficients method.

---

## Q5 — Repeated roots change the partial-fraction template
**Q.** Decompose $\dfrac{5}{(x+1)^2(x+2)}$.

**A.** A repeated linear factor contributes a term for each power up to the
multiplicity: $\frac{A}{x+1}+\frac{B}{(x+1)^2}+\frac{C}{x+2}$.
Clear denominators: $5=A(x+1)(x+2)+B(x+2)+C(x+1)^2$.
$x=-1$: $5=B(1)$ ⇒ $B=5$. $x=-2$: $5=C(1)$ ⇒ $C=5$.
$x=0$: $5=2A+10+A$ ⇒ $3A=-5$ ⇒ $A=-\frac53$.
So $\int\!\frac{5\,dx}{(x+1)^2(x+2)}=-\frac53\ln|x+1|-\frac{5}{x+1}+5\ln|x+2|+C$.
Forgetting the $(x+1)^{-2}$ term is the single most common partial-fraction error.

---

## Q6 — Long division first
**Q.** A student tries partial fractions on
$\dfrac{x^3+1}{x^2+1}$. What's wrong and what's the fix?

**A.** The degree of the numerator exceeds the denominator, so the algorithm
fails. Do polynomial long division first:
$\frac{x^3+1}{x^2+1}=x+\frac{1-x}{x^2+1}$. The remaining proper fraction splits
over the irreducible quadratic — and over $\mathbb{R}$ an irreducible quadratic
contributes the form $\frac{Ax+B}{x^2+1}$, not $\frac{A}{x^2+1}$, because the
numerator must be linear. Rule: **divide first, then decompose.**

---

## Q7 — A rational integral with no elementary form
**Q.** Is $\int\frac{dx}{x^4+1}$ elementary? If yes, what type of technique applies?

**A.** Yes, elementary — and this is the classic demonstration that partial
fractions over $\mathbb{R}$ handles quartics. Factor
$x^4+1=(x^2+\sqrt2x+1)(x^2-\sqrt2x+1)$, then partial-fraction each irreducible
quadratic with linear numerators. The result combines
$\ln$ and $\arctan$ terms, e.g. the standard closed form involves
$\frac{1}{4\sqrt2}\ln\frac{x^2+\sqrt2x+1}{x^2-\sqrt2x+1}+\frac{1}{2\sqrt2}\arctan\frac{x^2-1}{\sqrt2x}$ up to constants.
Contrast $\int e^{-x^2}dx$ (Q3 of the fundamentals lab) which is provably not
elementary — rational functions always are.

---

## Q8 — Completing the square
**Q.** Evaluate $\int\frac{dx}{x^2+6x+13}$.

**A.** Denominator $=(x+3)^2+4$. Substitute $u=(x+3)/2$, $du=dx/2$, $dx=2\,du$:
$\int\frac{2\,du}{4(u^2+1)}=\frac12\arctan u+C=\frac12\arctan\frac{x+3}{2}+C$.
The quadratic formula tells you when a trig substitution is needed: positive
leading coefficient with negative discriminant ⇒ complete the square ⇒
arctangent. Negative discriminant and negative leading coefficient ⇒
artanh/log.

---

## Q9 — Integration by parts in a definite integral
**Q.** Evaluate $I=\int_0^1 x e^x dx$ two ways. Why is the definite form cleaner?

**A.** By parts: $I=[xe^x]_0^1-\int_0^1 e^x dx=e-(e-1)=1$.
Directly $xe^x=\frac{d}{dx}[(x-1)e^x]$, so $I=[(x-1)e^x]_0^1=1$.
The definite version absorbs the $+C$ and the boundary term, avoiding the
"evaluate then substitute then combine" bookkeeping. Also: if the indefinite
answer for $\int xe^xdx$ were missing $+C$, the definite answer would still be
unique — a good sanity check that the antiderivative is right.

---

## Q10 — Hermite reduction: repeated quadratic factors
**Q.** A rational integrand has denominator $(x^2+1)^2$. Outline the strategy.

**A.** Hermite reduction: write the rational function as
$R(x)=\frac{Ax+B}{x^2+1}+\frac{d}{dx}\left(\frac{Cx+D}{x^2+1}\right)+S(x)$
where $S$ has square-free denominator. The first piece integrates by
log + arctan; the second reduces to $\int\frac{C-Dx^2}{(x^2+1)^2}$, handled by
$x=\tan\theta$ giving $\int\sin^2\theta\cos\theta\,d\theta$-style
expressions. Used by CAS (SymPy, Mathematica) to produce compact output; knowing
it lets you verify their output.

---

## Q11 — Improper integral with an internal singularity
**Q.** Evaluate $\int_{-1}^1\frac{dx}{x^3}$ in the Cauchy principal value sense
versus as an improper integral.

**A.** As an improper integral: $\int_{-1}^{0}x^{-3}dx$ and $\int_0^1x^{-3}dx$
both diverge ($\pm\infty$ with opposite signs), so the improper integral
**does not exist**. In the Cauchy principal value sense, taking symmetric
exclusions:
$2\lim_{\epsilon\to0}\int_\epsilon^1x^{-3}dx=2\lim[-\tfrac{1}{2x^2}]_\epsilon^1=2(-\frac12+\frac{1}{2\epsilon^2})=\infty$.
For $x^{-1}$ the PV is finite ($=0$); for $x^{-3}$ it is not. The PV convention
is order-dependent for higher-order poles — a real physical hazard, not a
formality.

---

## Q12 — The substitution that changes the bounds direction
**Q.** Evaluate $\int_0^{2\ln 2} e^x dx$ by substitution. What is the general rule?

**A.** Let $u=e^x$, $du=e^x dx$; bounds: $x=0\Rightarrow u=1$,
$x=2\ln2\Rightarrow u=4$. So $\int_1^4 du=3$.
Generally $u=g(x)$ is a *monotone* bijection on the interval if you want a
single definite integral in $u$; if $g$ folds back, you must split the interval
and add the pieces. For $u=x^2$ on $[-1,1]$ the correct treatment is
$2\int_0^1(\cdots)\,du$, not $\int_0^1(\cdots)\,du$ — a classic dropped factor
of 2.

---

## Q13 — Trigonometric integrals: the power reduction
**Q.** Compute $\int\sin^4x\,dx$ and $\int\sin^2x\cos^3x\,dx$.

**A.** First: use $\sin^2x=\frac{1-\cos2x}{2}$ repeatedly:
$\sin^4x=\left(\frac{1-\cos2x}{2}\right)^2=\frac{1}{4}\left(1-2\cos2x+\frac{1+\cos4x}{2}\right)$
$=\frac38-\frac12\cos2x+\frac18\cos4x$, so
$\int\sin^4x\,dx=\frac{3x}{8}-\frac{\sin2x}{4}+\frac{\sin4x}{32}+C$.
Second: save one $\cos$: $u=\sin x$, $\cos^3x=\cos x(1-\sin^2x)$ gives
$\int u(1-u^2)du=\frac{u^2}{2}-\frac{u^4}{4}+C$. Rule: if any power of
$\cos x$ is odd, reserve one and substitute; otherwise use power reduction.

---

## Q14 — Definite integration as a proposition
**Q.** State a proposition that characterizes when a rational function has an
elementary antiderivative.

**A.** Liouville's theorem (for the rational case): a rational function $R(x)$
has an elementary antiderivative over $\mathbb{Q}(x)$ **iff** its partial-fraction
decomposition contains no irreducible quadratic factor raised to a power $\ge2$
beyond what log/arctan can absorb — concretely, iff the denominator is a product
of powers of distinct linear factors over $\mathbb{Q}$, or equivalently iff
Hermite reduction leaves no "hard" part. $\frac{1}{x}$ integrates to $\ln x$,
$\frac{1}{x^2+1}$ to $\arctan x$, but $\frac{1}{x^2+1)^2}$ requires a
non-elementary-looking extra step (it is elementary, but needs the reduction of
Q10), while $e^{-x^2}$ is non-elementary.

---

## Q15 — Numerical integration sanity checks
**Q.** You compute $\int_0^1\frac{dx}{x^2+1}$ numerically and get $0.9999999$.
Is that plausible?

**A.** The exact value is $\arctan(1)=\frac{\pi}{4}=0.785398\ldots$, so
$0.9999999$ is wrong by ~0.21 — a bug, not rounding. Good sanity checks:
(a) compare with an independent method (Simpson vs Gauss–Legendre);
(b) verify the result against a closed form when one is known;
(c) check integrand signs — if $f\ge0$ the integral must be in
$[0,\max f]$; (d) halve the step and confirm convergence rather than a
plateau. Numerical integration without a known-value cross-check is where
silent bugs survive longest.

---

*Self-check: Q5, Q6 and Q14 all test the same underlying skill — knowing the
exact template each rational integral requires, including when to divide first.*