# Inner Products and Norms — Quiz (15 Questions with Worked Answers)

Cauchy–Schwarz, orthogonality, Gram–Schmidt, orthogonal projection, least
squares, and induced norms. The recurring theme: orthogonality makes
decomposition possible; non-orthogonality is what causes cancellation.

---

## Q1 — Cauchy–Schwarz and when equality holds
**Q.** State C–S and its equality condition.

**A.** $|\langle u,v\rangle|\le\|u\|\|v\|$; equality iff $u,v$ are linearly
dependent (one is a scalar multiple of the other, including a zero vector).
Equality means **maximum correlation** — the vectors point in exactly the same
(possibly opposite) direction. This is why nearly-parallel vectors give unstable
computations: the inner product nearly saturates the bound, so the *angle* estimate
$\cos\theta=\langle u,v\rangle/(\|u\|\|v\|)$ loses precision. In floating point,
Gram matrices are computed as inner products, so Gram–Schmidt on nearly-parallel
vectors loses orthogonality. That is the entire reason for Householder QR.

---

## Q2 — Positive semi-definite is not positive definite
**Q.** Is $\langle f,g\rangle=\int_{-1}^{1} f(x)g'(x)\,dx$ an inner product on
$C^1[-1,1]$? Is $\langle f,g\rangle=\int_{0}^{1}f(x)g(x)\,dx$ an inner product
on $P_2(\mathbb{R})$?

**A.** **First: no — it is a bilinear form, not even positive semi-definite.**
Take $f(x)=x$: $\langle f,f\rangle=\int_{-1}^1 x\cdot 1\,dx=[x^2/2]_{-1}^1=0$
with $f\not\equiv0$. Worse, take $f(x)=x^2$: $\int_{-1}^1x^2\cdot2x\,dx=2[x^4/4]_{-1}^1=0$ too, and
$f(x)=x^3$ gives $\int_{-1}^1 3x^4=6/5>0$ — so the form is indefinite (both
positive and negative values occur), which rules out any inner product.
**Second: yes, it is a valid inner product on $P_2(\mathbb{R})$.** If
$f\not\equiv0$ is a polynomial then $f^2>0$ on some subinterval of $[0,1]$, so
$\int_0^1f^2>0$; bilinearity and symmetry are immediate.
The lesson: to check "is this an inner product", verify all four properties, and
in particular test $\langle f,f\rangle$ on a vector you *expect* to fail —
isotropy ($\langle f,f\rangle=0$ for $f\ne0$) is the failure mode, and the
derivative in the integrand is what creates it. Compare the variant
$\langle f,g\rangle=\int_{-1}^{1}f'g'$ on $C^1[-1,1]$: that one *is* positive
semi-definite but degenerate (constants are null vectors), so it is a seminorm.

---

## Q2b — A cleaner version of Q2
**Q.** Give a concrete, unambiguous non-inner product of the form
$\langle f,g\rangle=\int fg\,dx$ on a natural space.

**A.** On $L^2(-1,1)$ with the functional
$\langle f,g\rangle=\int_{-1}^1 f(x)g(x)\,dx$, take $f=\text{sgn}(x)$.
Then $\langle f,f\rangle=\int_{-1}^1\text{sgn}^2=2>0$. Not that.
The clean counterexample uses a *signed* measure: on $C[-1,1]$ define
$\langle f,g\rangle=f(0)g(0)$. Then $\langle f,f\rangle=f(0)^2\ge0$ with
equality for every $f$ vanishing at 0, e.g. $f(x)=x$: $\langle x,x\rangle=0$
with $x\ne0$. Not positive definite ⇒ **seminorm**, not inner product.
Equally clean: $\langle f,g\rangle=\int_0^1 f'g'dx$ on $C^1[0,1]$ —
$f\equiv1$ is a nonzero null vector. And in the genuinely indefinite direction,
$\langle f,g\rangle=\int_{-1}^1 f g$ over $L^2$ *is* a valid inner product,
whereas $\int fg$ with $f,g$ real on a set of measure zero is degenerate.
The transferable lesson: before calling anything an inner product, check
**positive definiteness** ($\langle f,f\rangle>0$ for $f\ne0$), not just
positive semi-definiteness. Weighting $\int_{-1}^{1}fg$ by $1$ is fine; weighting
it by $\mathrm{sgn}$ or using only point evaluations is not.

---

## Q3 — Orthogonal vs orthonormal
**Q.** You project $v$ onto an orthogonal basis $\{u_1,u_2\}$. Must you normalise?

**A.** No, but you must divide by the norms:
$\text{proj}_{u}v=\frac{\langle v,u\rangle}{\langle u,u\rangle}u$.
The coefficients simplify to $\langle v,\hat u_i\rangle$ only when $\hat u_i=u_i/\|u_i\|$.
Getting this wrong is the classic least-squares bug: with a non-orthonormal
basis, coefficients are *not* the inner products. Rule: orthonormalise first,
then coefficients = inner products. This is why QR factorisation is written
$Q$ orthogonal, $R$ upper triangular rather than the other way round.

---

## Q4 — Projection is the closest point
**Q.** Why is orthogonal projection the minimiser of $\|v-w\|^2$ over $w\in S$?

**A.** Write $w=w_\parallel+w_\perp$ with $w_\parallel\in S$, $w_\perp\perp S$.
Then $\|v-w\|^2=\|v-w_\parallel-w_\perp\|^2=\|v-w_\parallel\|^2+\|w_\perp\|^2$
(the cross term vanishes by orthogonality), minimised at $w_\perp=0$.
The Pythagorean splitting is why "residual orthogonal to the space" is the
defining property, and why least squares fits have uncorrelated residuals —
a fact worth stating as a diagnostic when a least-squares fit looks wrong.

---

## Q5 — Least squares and normal equations
**Q.** For $A\in\mathbb{R}^{m\times n}$ with full column rank $A^TA$
invertible, solve $\min_x\|Ax-b\|_2$.

**A.** Normal equations $A^TAx=A^Tb$, so $x=(A^TA)^{-1}A^Tb$. But $\kappa(A^TA)=\kappa(A)^2$:
forming $A^TA$ squares the condition number and roughly halves the available
precision. Prefer QR: $Ax\approx b$ ⇔ $Rx\approx Q^Tb$, then
$x=R^{-1}Q^Tb$. Residual: $r=b-Ax$ with $A^Tr=0$; if $r=0$ the system is
consistent, otherwise it's an overdetermined system being fitted. The
"predictable $x$" of normal-equation least squares is a red flag: it suggests
you've fitted an interpolation, not a signal.

---

## Q6 — Gram–Schmidt failure and reorthogonalisation
**Q.** Orthogonalise $v_1=(1,1)$, $v_2=(1,1.01)$ by classical Gram–Schmidt. Then?

**A.** $u_1=(1,1)$, $\|u_1\|^2=2$, $\langle v_2,u_1\rangle=2.01$, so
$u_2=(1,1.01)-1.005(1,1)=(-0.005,\,0.005)$. $\cos\theta=2.01/(\sqrt2\sqrt{2.0201})\approx0.9999$:
nearly parallel. In floating point, the normalised $u_2$ retains only $\sqrt{1-0.9998}\approx0.014$
of a "correct" component — relative error $\sim\epsilon/0.014\approx10^{-14}$, so
orthogonality is lost. One re-orthogonalisation pass ($u_2\mathrel{-}=
\operatorname{proj}_{u_1}u_2$) fixes it: modified Gram–Schmidt, or Householder
(unconditionally stable, $O(\epsilon)$). Never use classical Gram–Schmidt on
nearly dependent vectors.

---

## Q7 — Induced vs abstract norms
**Q.** Is $\|A\|_F$ induced by a vector norm? Is $\|A\|_2$?

**A.** $\|A\|_F=\sqrt{\sum_{ij}A_{ij}^2}$ is **not** an induced operator norm —
it's the Frobenius inner-product norm on the vector space of matrices, which
satisfies $\|AB\|_F\le\|A\|_F\|B\|_F$ (submultiplicative) but isn't
$\max_{\|x\|=1}\|Ax\|$ (which gives $\|A\|_2$). $\|A\|_2$, $\|A\|_1$,
$\|A\|_\infty$ are induced/operator norms from a vector norm. The distinction
matters: mixing them up in a proof (e.g. claiming $\|Ax\|_\infty\le\|A\|_F\|x\|_\infty$
via Cauchy–Schwarz) produces wrong constants. Induced norms satisfy
$\|I\|=1$ for all standard vector norms; the Frobenius norm does too for $\|I\|_F=\sqrt n$.

---

## Q8 — Equivalence of norms
**Q.** Does norm-equivalence mean $\|A\|_2\le\|A\|_F$?

**A.** $\|A\|_2\le\|A\|_F\le\sqrt{\operatorname{rank}A}\,\|A\|_2\le\sqrt n\,\|A\|_2$.
All norms on $\mathbb{R}^n$ are equivalent up to constants, but the *constants
matter*: $\|A\|_2\le\|A\|_F$ is sharp (equality iff rank 1), while
$\|A\|_F\le\sqrt n\|A\|_2$ is worst case for dense matrices but hugely pessimistic
for random ones ($\approx\|A\|_F$). Corollary: comparing $\|A\|_F$ and $\|A\|_2$
across different matrices of different ranks is meaningless without normalising.

---

## Q9 — Reproducing kernels
**Q.** In $\mathcal{H}$ with kernel $k(\cdot,\cdot)$, the representer theorem says
$f^\ast$ minimises $f(y)+\lambda\|f\|^2$. What is the value?

**A.** $f^\ast(y)=-\frac{1}{\lambda}\sum_i\alpha_i k(y,x_i)$ with
$\boldsymbol\alpha=(K+\lambda I)^{-1}\mathbf y$ where $K_{ij}=k(x_i,x_j)$.
Everything reduces to linear algebra in coefficient space — this is why kernel
ridge regression is $\mathcal{O}(n^3)$ in the number of points rather than the
dimension of the feature space. In RKHS terms the kernel is a PSD Gram matrix
(an inner product), and the "dimension" of the feature space is irrelevant.

---

## Q10 — Conditions and norms
**Q.** Why do different norms give different condition numbers for the same
matrix?

**A.** $\kappa_p(A)=\|A\|_p\|A^{-1}\|_p$ depends on $p$; for a symmetric positive
definite $A$, $\kappa_2(A)=\lambda_{\max}/\lambda_{\min}$ exactly. For
nonsymmetric or indefinite $A$ the conditioning depends on the norm used,
since eigenvectors aren't orthogonal and cancellation differs. Practical
consequence: never report "condition number" without the norm and the matrix
class; $\kappa_1$ and $\kappa_\infty$ can differ by orders of magnitude, and for
some matrices $\kappa_2$ isn't even the relevant one.

---

## Q11 — Inner product structure matters for conditioning
**Q.** If $A$'s rows are nearly parallel, why does $A^TA$ blow up?

**A.** Gram matrix $A^TA$ measures inner products of columns; nearly parallel
columns have inner products close to $\|a_i\|\|a_j\|$, and $A^TA$ becomes
near-singular with condition number $\kappa(A)^2$. Symmetrically, the row Gram
matrix is equally ill-conditioned. So the projection of one row onto another is
nearly the whole row — the least-squares system can't distinguish the two
predictors. This is why collinearity among features (a data-science issue) shows
up as ill-conditioning, and why regularisation (ridge) stabilises it by
adding $\lambda I$ to the Gram matrix.

---

## Q12 — Bessel's inequality and frame theory
**Q.** State Bessel's inequality and when it becomes equality.

**A.** For an orthonormal set $\{e_i\}$: $\sum_i|\langle v,e_i\rangle|^2\le\|v\|^2$.
Equality iff $v$ lies in the closed span. Bessel gives a *lower* bound on
$\|v\|^2$, hence an upper bound on the error of the projection, and vice versa.
Frames (generalisations of orthonormal bases, $\sum|\langle v,e_i\rangle|^2\le A\|v\|^2$
with $\sum|\langle v,e_i\rangle|^2\ge B\|v\|^2$) generalize this to redundant
families. Engineering content: in frame theory, sampling and reconstruction from
over-complete dictionaries (wavelets, compressed sensing) are analyzed with
these bounds rather than with basis sizes.

---

## Q13 — Cosine similarity and its trap
**Q.** Two documents with vectors $u=(1,0)$, $v=(1,0.01)$. Cosine similarity?

**A.** $\frac{\langle u,v\rangle}{\|u\|\|v\|}=\frac{1}{1\cdot\sqrt{1.0001}}\approx0.99995$.
Near 1, they look "nearly identical" — but if your use is detecting near-duplicates
this is right, and if it's measuring *magnitude* information it is wrong: cosine
ignores magnitude entirely, so $u$ and $100u$ have similarity 1.
Also note: with sparse high-dimensional vectors (bag of words), cosines cluster near
$1$ for almost everything, so raw cosine is nearly useless — TF-IDF weighting exists
partly to fix that. Recognizing when a metric is degenerate in your data regime
is a first-order modelling concern.

---

## Q14 — Orthogonality under the right inner product
**Q.** For $A$ symmetric positive definite, "orthogonal" should mean which?

**A.** $A$-orthogonal: $\langle x,y\rangle_A=x^TAy$, not $x^Ty$. In this inner
product $A^{1/2}$ is orthogonal (a whitening transform) and
$\kappa_2$ becomes the condition number of the whitening
($\kappa_2(A^{1/2})=\sqrt{\kappa(A)}$). So $A$-orthogonality is achieved by
pre-multiplying by $A^{-1/2}$ (Cholesky). In variational formulations this is
essential: the weak form of an elliptic PDE, $a(u,v)=\int\nabla u\cdot\nabla v$,
defines an inner product on $H^1_0$, and "orthogonal" means with respect to $a$,
not the $L^2$ inner product.

---

## Q15 — A diagnostic you can actually use
**Q.** A least-squares fit has huge residuals orthogonal to the design matrix.
What does that tell you?

**A.** The residuals satisfy $A^Tr=0$ exactly — that's a *theorem*, so it's a
check, not a diagnosis. If the residuals are orthogonal but large, the model is
simply a poor fit (underfitting or wrong features). If the residuals are *not*
orthogonal, something is numerically wrong (bad conditioning, an unstable
factorisation, or a bug). Practical checklist: (1) is $\|A^TA\|$ well scaled —
compute via QR, not $A^TA$; (2) do you have full column rank; (3) does your
design matrix have wildly different column scales (fix by standardising); (4) do
residuals show structure (non-linearity ⇒ add features, heteroscedasticity ⇒
weighted least squares)? Diagnosing before re-fitting is the whole skill.

---

*Self-check: Q1, Q6 and Q11 are all about loss of orthogonality in floating point.
Q2b is the exercise on checking positive definiteness — the one most often
skipped.*