# Matrix Calculus — Quiz (15 Questions with Worked Answers)

Gradients of scalar functions of matrices, Jacobians, Hessian and trace
identities, differentiation of inverses and traces, and the vectorisation
identities that make automatic differentiation work.

---

## Q1 — Gradient of a matrix-valued map
**Q.** $f:\mathbb{R}^{n\times m}\to\mathbb{R}$, $f(A)=\operatorname{tr}(AB)$ for
fixed $B$. What is $\nabla_A f$?

**A.** $B^T$. In index form $f=\sum_{ij}A_{ij}B_{ji}$, so
$\frac{\partial f}{\partial A_{ij}}=B_{ji}$, which is the transpose. Rule of
thumb: $\nabla_A\operatorname{tr}(AB)=B^T$, $\nabla_A\operatorname{tr}(A^TB)=B$.
The matrix-calculator convention: $\nabla_Af$ has the same shape as $A$ and
satisfies $df=\operatorname{tr}((\nabla_Af)^T\,dA)$. Fixing that convention is
the only way to avoid sign errors — the alternative convention drops the
transpose and shifts the error elsewhere.

---

## Q2 — Derivative of an inverse
**Q.** Differentiate $A^{-1}$.

**A.** $d(A^{-1})=-A^{-1}(dA)A^{-1}$. Proof: differentiate $AA^{-1}=I$ and
$dI=0$: $(dA)A^{-1}+A\,d(A^{-1})=0$, solve for $d(A^{-1})$.
Generalises: for a matrix function $f$ of $A$ with $f$ analytic and
$\lambda-f'(\lambda)$ invertible on the spectrum,
$d\,f(A)=U\Lambda'[H]U^T$ (Fréchet derivative), and the special case
$f(A)=A^{-1}$ reduces to the identity above via
$\Lambda'[\lambda^{-1}][H]_{ij}=\frac{-H_{ij}\lambda^{-1}\delta_{ij}}{\lambda\lambda}$.
Practical use: this identity is the basis of sparse-matrix condition number
estimation, of iterative linear solvers, and of ODE solvers for the flow
$\dot A=-A^{-1}$.

---

## Q3 — Derivative of a trace
**Q.** $f(A)=\operatorname{tr}(A^k)$. Give $\nabla_Af$.

**A.** $\nabla f=k\,A^{k-1}$ (matrix power series; trace is linear).
$\frac{d}{dt}\operatorname{tr}(A+tB)^k=\sum_{j=0}^{k-1}\operatorname{tr}(A^jBA^{k-1-j})=k\operatorname{tr}(BA^{k-1})$.
**No transpose** appears (compare $\nabla\operatorname{tr}(A^TB)=B$). This
asymmetry trips people up: $\operatorname{tr}(AB)=\langle A,B^T\rangle_F$,
and the coefficient sits inside the trace either way.

---

## Q4 — Cyclicity of trace is a computational tool
**Q.** How do you compute $\nabla_AA^k$ by cycling the trace?

**A.** $\operatorname{tr}(A^k)=\operatorname{tr}(A^{k-1}A)$, so
$df=\operatorname{tr}(A^{k-1}dA)=k\operatorname{tr}(A^{k-1}dA)$, giving
$\nabla=kA^{k-1}$. Then $\operatorname{tr}(X^TY)=\sum X_{ij}Y_{ij}$ is the
Frobenius pairing, which "pulls out" any factor that appears exactly once.
This trick is used to compute, e.g., the gradient of $\log\det A$ via the
Jacobi formula without any matrix inversion beyond the adjoint.

---

## Q5 — Jacobi's formula
**Q.** Differentiate $\log\det A$ and $\det A$.

**A.** $\nabla\log\det A=(A^{-1})^T$ (valid for nonsingular $A$, possibly complex);
$\nabla\det A=\det A\,(A^{-1})^T$.
Proof uses Jacobi: $d(\log\det A)=\operatorname{tr}(A^{-1}dA)=\operatorname{tr}((A^{-1})^TdA)$.
Fails when $A$ is singular — the derivative genuinely doesn't exist (the
function is $-\infty$ or has a kink). This is why log-determinant
parameterisations require positive definiteness, and why one uses Cholesky
factorisation (then $\log\det A=2\sum\log L_{ii}$) rather than an explicit
determinant.

---

## Q6 — Jacobians: shapes and gotchas
**Q.** For $f:\mathbb{R}^m\to\mathbb{R}^n$, $A:\mathbb{R}^n\to\mathbb{R}^p$, what
shape is $Df\cdot DA$, and what's a classic mistake?

**A.** $\frac{\partial f_i}{\partial x_j}\frac{\partial A_{jk}}{\partial x_\ell}$
sums over the shared index $j$. The classic mistake: writing the Jacobian of a
vector function as a single matrix when it's a 3-tensor
$J_{ijk}=\partial f_i/\partial x_j\partial x_k/\partial x_\ell$ — you cannot
"multiply Jacobians" without contracting an index first. (See Q15.)
Second classic: transposing by convention mismatch between row-major and
column-major layouts.

---

## Q7 — Hessian of a quadratic
**Q.** Hessian of $f(x)=\frac12x^TAx - b^Tx$ for symmetric $A$.

**A.** $\nabla f=Ax-b$ (only because $A$ symmetric); $\nabla^2f=A$.
For general $A$: $\nabla f=\frac12(A+A^T)x-b$, Hessian $=A^{\text{sym}}=\frac12(A+A^T)$.
So only the symmetric part matters for the quadratic form and gradient — a fact
you can exploit to symmetrise and improve numerical conditioning.

---

## Q8 — Hessian need not be symmetric for vector fields
**Q.** $f:\mathbb{R}^n\to\mathbb{R}$. Is its Hessian always symmetric?

**A.** For a **scalar-valued** $f:\mathbb{R}^n\to\mathbb{R}$ that is $C^2$ on an
open set, yes: Clairaut–Schwarz gives $\partial^2f/\partial x_i\partial x_j
=\partial^2f/\partial x_j\partial x_i$, so $\nabla^2f$ is symmetric.
For **vector-valued** maps $f:\mathbb{R}^2\to\mathbb{R}^2$ it fails: with
$F(x_1,x_2)=(x_1^2x_2,\ x_1^2x_2^2)$ we get
$J_F=\begin{pmatrix}2x_1x_2 & x_1^2\\ 2x_1x_2^2 & 2x_1x_2^2\end{pmatrix}$,
so $\partial J_{12}/\partial x_1=2x_2$ but $\partial J_{21}/\partial x_1=2x_2^2$ —
non-symmetric. Consequence for autodiff: for scalar outputs you may symmetrise
the Hessian safely and save half the work; for vector outputs you may not.

---

## Q9 — Scalar/vector/Jacobian conventions
**Q.** Give the chain rule with correct tensor index placement for $y=f(Ax)$.

**A.** $dy=\operatorname{tr}((J_f)^T J_A\,dx)$ where $J_f$ is $p\times m$
($\partial f_i/\partial z_j$) and $J_A$ is $m\times n$.
In indices: $dy_i=\sum_{j,k}J_{f,ij}\,J_{A,jk}\,dx_k$ — the $j$-sum is the
"contraction". In vectorised form,
$\mathrm{vec}(J_fJ_A)=((J_fJ_A)\otimes I)\,\mathrm{vec}(J_A)$.
Q10 and Q15 make the index bookkeeping explicit; the wrong answer here is a
matmul in the wrong order ($J_AJ_f$), which is dimension-compatible only when
$p=n$ — so it compiles but is wrong.

---

## Q10 — Vectorisation and Kronecker
**Q.** Express $J_fJ_A$ in vec form.

**A.** $\mathrm{vec}(XY)=(Y^T\otimes I)\mathrm{vec}(X)$ for compatible sizes. So
$\mathrm{vec}(J_fJ_A)=((J_A)^T\otimes I_{p})\mathrm{vec}(J_f)$.
The conjugate identity: $\mathrm{vec}(AXB)=(B^T\otimes A)\mathrm{vec}(X)$.
These are the workhorses of AD frameworks and of backprop implementations
layer by layer.

---

## Q11 — Backprop as reverse-mode AD
**Q.** Backprop computes gradient of $f(W)=\sum_i\ell_i$ over data. Write the
gradient of a single $\ell_i$ w.r.t. a layer output.

**A.** For $\ell=\ell(y^{(L)})$, $\bar y^{(L-1)}=J^{(L)T}\bar y^{(L)}$ where
$\bar y^{(L)}=\partial\ell/\partial y^{(L)}$ — gradient flows backwards as
transpose-Jacobian-vector products, at one pass per layer,
$\mathcal{O}(\text{params})$. Forward mode computes $Jv$ instead, which is
cheap when the number of inputs is much smaller than the number of outputs
(the "fan-out vs fan-in" argument).
Since only the transpose is ever needed, and the Hessian of a scalar loss is
symmetric, you may symmetrise where valid. The practical bug class: forgetting
the transpose in a recurrent or attention block, whose Jacobians are not
symmetric — the code still compiles and still runs, just with wrong gradients.

---

## Q12 — Vector-Jacobian product is what you need
**Q.** Why compute $Jv$ instead of $J$?

**A.** Cost: forming $J$ is $O(\text{rows}\cdot\text{cols})$ per input; $Jv$
costs $O(\text{cost of one forward pass})$. Memory similar. In autodiff,
reverse mode gives $J^Tv$ for free-ish, so we never need the full Jacobian.
Gradient checking: compare analytic vs numerical gradient — error
$\le\frac{\epsilon}{6}\max|f'''|$, so with $\epsilon\approx1.49\cdot10^{-8}$
in 64-bit you expect agreement $\approx10^{-11}$ — anything worse indicates a
bug in the analytic gradient, not floating point noise.

---

## Q13 — Rank of the empirical Hessian
**Q.** The Hessian of an empirical loss over $n$ points with $p$ parameters has
rank bounded by what? Why does this matter for optimisation?

**A.** $\frac1n\sum_i\nabla^2\ell_i(x)$ is a sum of $n$ outer products
$\nabla\ell_i\nabla\ell_i^T$, so its rank is at most $\min(n,p)$. With $n<p$
the Hessian is structurally singular: gradient descent then has $p-n$ flat
directions and convergence is governed by the $n$ non-flat ones. Least squares
makes this explicit: $\nabla^2f=J_f^TJ_f+\sum_ir_i\nabla^2r_i$, and
Gauss–Newton keeps only $J_f^TJ_f$, exact for linear least squares and accurate
near a minimum. For GLMs, Fisher scoring uses $X^TWX$ with
$W=\operatorname{diag}(p_i(1-p_i))$, positive semi-definite by construction —
which is why Newton/Fisher dominates GLM fitting: the Hessian is never
indefinite, unlike raw Hessian descent on a logistic loss under separation.

---

## Q14 — Symmetric vs antisymmetric decomposition
**Q.** Why replace $A$ by $\frac12(A+A^T)$?

**A.** For a symmetric function $s(A)=s(A^T)$, we can symmetrise without loss.
Benefit: guaranteed symmetry/PSD ($H=\frac12(J^TJ)$) and about half the
work (only one triangle matters). Also numerically stable: $\frac12(A+A^T)$
cancels the antisymmetric roundoff error.
In code: only compute/store the lower (or upper) triangle — saves memory and
flops, and guarantees consistency (the "packed" storage).

---

## Q15 — Reconstruct the full Hessian-vector product
**Q.** In reverse mode you get $J^T\bar y$. How to get $\nabla^2f\cdot v$?

**A.** Trick: if $A=(x+\epsilon v)$ is a dual pair, then forward mode gives
$A^TA$ and reverse gives $A^TA_\text{fwd}^T$, so both can be assembled.
The cheapest practical answer: **forward-over-reverse** gives the Hessian-vector
product in one forward and one reverse pass (Griewank). Concretely, for a
layer with $z$ as input, $y=f(z)$, $J$ the Jacobian:
$\nabla^2f\cdot v = J^T(\nabla_z J\,v)$ — and for a generic $f$, $\nabla_zJ$
is a 3-tensor of size $|y|\times|z|\times|z|$, computed by $n$ reverse passes or
one hyper-dual forward pass (forward-over-forward). Practical implication:
**Hessian-vector products are cheap (2x forward cost) even though the full
Hessian is expensive ($n$ passes)** — this is exactly what Newton's
CG/interior-point methods exploit.

---

*Self-check: Q2, Q5, Q10 and Q11 are the practical core: differentiating
inverses, log-dets, vectorisation, and the VJP that powers autodiff. Q6 and Q15
target the index-juggling mistakes.*