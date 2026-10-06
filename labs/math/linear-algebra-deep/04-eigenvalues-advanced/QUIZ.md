# Eigenvalues and Eigenvectors (Advanced) — Quiz (15 Questions with Worked Answers)

Diagonalisability, multiplicity bookkeeping, spectral theorems, Perron–Frobenius
and the limits of eigenvalue-based reasoning.

---

## Q1 — Diagonalisable vs merely having eigenvalues
**Q.** $A=\begin{pmatrix}1&1\\0&1\end{pmatrix}$ has eigenvalue 1 with algebraic
multiplicity 2. Is it diagonalisable?

**A.** No: $\ker(A-I)=\{x:x_2=0\}$ is 1-dimensional, so geometric multiplicity
1 < 2. Criterion: diagonalisable iff geometric multiplicity equals algebraic
multiplicity for **every** eigenvalue (over an algebraically closed field; over
$\mathbb{R}$ also need all eigenvalues real, or use the real canonical form).
And $A^k=I+k(A-I)$ grows linearly in $k$ while a diagonal matrix with the same
spectrum would be constant — the sharpest evidence that spectrum ≠ behaviour.

---

## Q2 — Eigenvectors are never unique
**Q.** What is wrong with "the eigenvector for $\lambda=2$ is $(1,2)$"?

**A.** It is *an* eigenvector; the eigenvector is the entire eigenspace
$\ker(A-2I)$, here $\text{span}((1,2))$. Any nonzero scalar multiple works, so
$\phi$ is not even well defined as a function of $\lambda$. To make eigenvectors
comparable across matrices you must fix a normalisation (unit length) *and* an
orientation convention (first nonzero component positive), otherwise sign
flips make eigenvectors incomparable and Jacobi rotations produce wildly
different-looking results for the same problem.

---

## Q3 — Spectral theorem for symmetric matrices
**Q.** State the symmetric spectral theorem and why it matters numerically.

**A.** $A=A^T$ real ⇒ orthonormal basis of eigenvectors and real eigenvalues:
$A=Q\Lambda Q^T$ with $Q^TQ=I$. (Complex Hermitian version: $A=Q\Lambda Q^*$.)
Consequences: $\kappa_2(A)=|\lambda_{\max}|/|\lambda_{\min}|$ exactly;
there is no defective Jordan behaviour, so $A^k$ behaves exactly as its
spectrum suggests; and the QR algorithm converges to it directly (tridiagonalise,
implicit QR) without shift-selection heuristics. This is why symmetric problems
(Spring systems, least squares, diffusion operators) are formulated as symmetric
whenever possible.

---

## Q4 — Cyclic vectors and minimal polynomials
**Q.** What's the minimum polynomial of $A=\begin{pmatrix}0&1\\0&0\end{pmatrix}$?

**A.** $m_A(t)=t^2$: $A\ne0$ so $t$ doesn't work; $A^2=0$. Characteristic
polynomial is also $t^2$ (only eigenvalue 0, alg mult 2). Degree of the minimal
polynomial = size of the largest Jordan block per eigenvalue = the number of
vectors needed in a Jordan chain. $\deg m_A\le n$ with equality iff $A$ is
non-derogatory (one Jordan block per eigenvalue). $A^k=0$ for $k\ge2$ — nilpotent,
transients killed in finite time, the strongest possible stability.

---

## Q5 — Spectral radius vs norm
**Q.** For $A=\begin{pmatrix}1&1\\-1&1\end{pmatrix}$, compare $\rho(A)$ and $\|A\|_2$.

**A.** Eigenvalues $1\pm i$, modulus $\sqrt2$ each, so $\rho=\sqrt2\approx1.414$.
$A^TA=2I$, so $\|A\|_2=\sqrt2$ too — because $A$ is **normal**
($A^TA=AA^T=2I$). Try instead $A=\begin{pmatrix}1&10\\0&1\end{pmatrix}$:
$\rho=1$ but $\|A\|_2\approx10.05$. So $\rho\le\|A\|_2$ always, with equality
for normal matrices. **This gap is the entire reason to use norms rather than
spectral radius in error analysis**: transient amplification, $\|A^k\|$ peaking
at $k\approx\frac{1}{2}\log(\epsilon)/\log(\rho/\|A\|)$, is real and can be
enormous. Non-normal matrices have pseudospectra, and eigenvalue-based reasoning
fails on them.

---

## Q6 — Perron–Frobenius for non-negative matrices
**Q.** $A=\begin{pmatrix}1&2\\3&4\end{pmatrix}$. Where is $\rho(A)$ and what
else follows?

**A.** Characteristic $\lambda^2-5\lambda-2$; roots $\frac{5\pm\sqrt{33}}2$,
so $\rho\approx5.372$. The other eigenvalue is $\approx-0.372$, with
$|\lambda_2|<\lambda_1$ — the theorem (for non-negative $A$ with $\rho>0$)
guarantees $\rho(A)$ is a *real positive simple* eigenvalue, and $A^k\approx
\rho^k v w^T/(w^Tv)$ whenever all other eigenvalues have strictly smaller modulus.
That's the convergence theorem for power iteration. Note the negative second
eigenvalue: for a Markov chain (row-stochastic, non-negative), eigenvalues live
in the unit disc, and $|\lambda_2|$ near 1 means slow mixing (bipartiteness forces
$\lambda=-1$).

---

## Q7 — Why the eigenvector direction is right and the value is wrong
**Q.** Power iteration on $A$ converges; what exactly converges?

**A.** If $\lambda_1$ is simple, $|\lambda_2|<\lambda_1$, and the start has a
nonzero component along $v_1$, then $x_k=A^kx_0/\|A^kx_0\|\to\pm v_1/\|\cdot\|$
(direction; sign may flip). The Rayleigh quotient instead converges *quadratically*:
$\rho_k=\frac{x_k^TAx_k}{x_k^Tx_k}\to\lambda_1$. Using the power-iteration value
$x_k^TAx_k$ after normalising gives only linear convergence. The practical rule:
iterate vectors, extract values by Rayleigh quotient (or inverse iteration).
Convergence rate is governed by $|\lambda_2/\lambda_1|$ — clustered eigenvalues
make power iteration slow, which motivates Krylov methods (Lanczos, Arnoldi).

---

## Q8 — Defective matrices: powers grow polynomially
**Q.** $A=J_2(1)=\begin{pmatrix}1&1\\0&1\end{pmatrix}$. What is $A^k$?

**A.** $A^k=I+k(A-I)=\begin{pmatrix}1&k\\0&1\end{pmatrix}$, growing linearly
in $k$. In general a Jordan block of size $m$ for eigenvalue $\lambda$ gives
terms like $k^{m-1}\lambda^k$: eigenvalues determine exponential growth,
Jordan structure determines the polynomial prefactor. Practical significance: the
stability of a linear recurrence or a discretised PDE depends on the Jordan
blocks, not just the eigenvalues — a "stable" spectrum with a large block
transiently amplifies. And numerically, computing Jordan form is unstable
(discontinuous function of the matrix); compute Schur instead.

---

## Q9 — Characteristic polynomial computation
**Q.** Is $\det(\lambda I - A)$ numerically advisable to find eigenvalues?

**A.** No: forming $\lambda I - A$ and computing its determinant is
catastrophically ill-conditioned as a root-finding procedure — small coefficient
errors in the determinant evaluation shift roots by $O(\|A\|\epsilon)$ relative,
and for defective matrices the "eigenvalue" is a hypersurface (ill-posed).
Use the Hessenberg reduction $Q^TAQ=H$ then (implicit QR for symmetric, shifted
QR generally) — these are backward stable, $O(\epsilon\|A\|)$ perturbations.
Better still for a few eigenvalues: power iteration for the dominant one, or
inverse iteration $x_{k+1}=(A-\sigma I)^{-1}x_k$ with a shift $\sigma$ near the
target, which converges cubically and quadratically respectively.

---

## Q10 — Eigenvalues of a symmetric rank-one update
**Q.** $A=\text{diag}(d_1,\dots,d_n)$, and we add $\sigma uu^T$. What structure
does the result have?

**A.** The eigenvalues interlace with the $d_i$ (Cauchy interlacing), so exactly
one eigenvalue lands in each gap $(d_i,d_{i+1})$ plus one outside — you can bracket
each and run independent bisection. Rank-one updates are the basis of many
algorithms: Lanczos (tridiagonal plus rank-one), preconditioned conjugate
gradients (where the eigenvalues bound convergence via Kantorovich), and the
Sherman–Morrison formula. This "one eigenvalue per gap" bracketing is why low-rank
updates are numerically tractable.

---

## Q11 — Graph Laplacian spectrum
**Q.** Spectrum of the Laplacian $L=D-A$ of a connected graph with $n$ vertices?

**A.** One eigenvalue $0$ (constant functions in the kernel, i.e. $D$ and $A$
agree on constants), and $n-1$ positive ones, all real (symmetric). Multiplicity
of $0$ = number of connected components. The second-smallest eigenvalue
$\lambda_2$ (the **algebraic connectivity**) controls how fast heat diffuses on
the graph and how fast Markov chains mix. Cheeger's inequality:
$h_G\ge\lambda_2/2$, so a small $\lambda_2$ means a bottleneck. This is the
spectral fact behind graph partitioning, spectral clustering, and resistance
estimates.

---

## Q12 — Symmetric positive definite implies real positive eigenvalues
**Q.** $A$ is $2\times2$ with $A_{11}=1$, $A_{22}=1$, $A_{12}=A_{21}=2$. Is it
SPD? What are the eigenvalues?

**A.** $\det A=1-4=-3<0$: **indefinite**, not SPD, eigenvalues $1\pm\sqrt3$, one
positive, one negative. SPD requires $\det>0$ and $A_{11}>0$ for $2\times2$
(equivalently all leading principal minors positive — Sylvester). This is the
check that catches a sign error or a non-Symmetric "inner product" long before
you try to Cholesky it. SPD also guarantees: real positive eigenvalues, $x^TAx>0$
for all $x\ne0$, monotone $x^TAx$ in $x$, and (for symmetric $A$) $x^TA^{-1}y$
well-behaved. **Never assume a matrix you think is SPD is SPD — verify.**

---

## Q13 — Eigenvalues under perturbation
**Q.** Bauer–Fike: if $A$ has distinct eigenvalues and $\tilde A = A+E$, where
can $\tilde\lambda$ be?

**A.** Bauer–Fike (for normal $A$): $|\tilde\lambda-\lambda|\le\kappa(A)\|E\|$.
For non-normal $A$ the correct bound involves the eigenvector matrix
condition number (and can be infinite — defective). Elsner's theorem gives
$|\tilde\lambda-\lambda|\le\|E\|+|E|\cdot\text{something}$ — always valid,
independent of normality.
Practically: for symmetric $A$ this is why eigenvalue-based early termination in
iterative solvers works, and why eigenvalue problems are backward stable under
symmetric perturbation but not general perturbation.

---

## Q14 — Eigenvalues tell you about asymptotic rank
**Q.** Why do low-rank algorithms like Lanczos work at all?

**A.** If the significant part of $A$ lives in a $k$-dimensional invariant
subspace, Krylov iteration finds it in $k$ steps exactly (in exact arithmetic).
Randomised methods (randomised range finders, Halko–Martinsson–Tropp) formalise
this: a Gaussian test matrix with $O(\log k/\epsilon^2)$ columns suffices to
recover a $k$-dimensional subspace. This is the basis of randomised SVD,
low-rank matrix factorisation for matrix completion, and randomised numerical
linear algebra generally. The underlying theorem is about the decay of singular
values, not eigenvalues — non-normal matrices can have tiny singular values
despite all $|\lambda_i|=1$.

---

## Q15 — The misuse to avoid
**Q.** An engineer sees $\|A\|_2=2$, so claims iterations converge "twice as
fast" by a spectral argument. When is this valid?

**A.** Only when $A$ is **normal** (symmetric in the usual cases). For normal $A$,
$\|A^k\|_2=\rho(A)^k$ exactly. For non-normal $A$ (and even symmetric-looking
algorithms with non-symmetric iteration matrices), $\|A^k\|$ can grow far beyond
$\rho^k$ transiently before decaying. Worse, many iterative methods apply a
*polynomial* of $A$ (Chebyshev, conjugate gradients) specifically to tame this
non-normality. The correct practice: bound convergence via norms and
non-normality measures (departure from normality, eigenvector condition number,
pseudospectrum), not eigenvalues alone. For a symmetric positive definite problem,
CG has a clean guarantee ($k$ iterations for $k$ distinct eigenvalues — see the
other lab file for this lab) precisely because the operator is normal and the
polynomial can be made optimal.

---

*Self-check: Q5, Q8, Q9 and Q15 all show that eigenvalues alone are not a
sufficient analysis tool. Q1 and Q3 are the classical criteria you must be able
to apply without hesitating.*