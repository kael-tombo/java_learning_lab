# Matrix Decompositions — Quiz (15 Questions with Worked Answers)

LU, QR, Cholesky, Schur, Jordan, SVD and polar decomposition: what each is for,
what it costs, and when the textbook version breaks down.

---

## Q1 — LU without pivoting can fail
**Q.** For which matrices does Gaussian elimination produce an $L$ with nonzero
diagonal so that $PA=LU$ requires no row swap?

**A.** Exactly the *nonsingular leading principal minors* condition. Counter-
example: $A=\begin{pmatrix}0&1\\1&0\end{pmatrix}$ — the first pivot is $0$, so
naive elimination divides by zero. Partial pivoting gives $PA=\begin{pmatrix}1&0\\0&1\end{pmatrix}$,
$LU=\begin{pmatrix}1&0\\0&1\end{pmatrix}\begin{pmatrix}0&1\\1&0\end{pmatrix}$.
With full (square) pivoting, an LU always exists with a permutation matrix $P$
on the left — that's the practical guarantee; "LU exists" without qualification is
false and is why LAPACK routines are named `getrf` (rectangular, no pivoting
assumed).

---

## Q2 — Cost of the decompositions
**Q.** Compare flop counts of dense $n\times n$ LU, QR, SVD.

**A.** LU: $\frac23n^3$. Householder QR: $\frac43n^3$. SVD: $\sim\frac83n^3$ to
$\frac{64}{3}n^3$ depending on the algorithm (Golub–Reinsch, divide-and-conquer).
So SVD costs roughly 4–8x QR and roughly 10x LU. For large sparse problems the
picture changes completely: sparse LU is $\sim O(n^{1.5})$ to $O(n^2)$,
sparse iterative methods $O(1)$ per iteration. That's why the default is "never
form a dense factorisation unless the matrix is dense."

---

## Q3 — QR gives a least-squares solution
**Q.** Solve $Ax\approx b$ in least squares given $A=QR$.

**A.** With $Q$ orthogonal ($Q^TQ=I$), $\|Ax-b\|^2=\|QRx-b\|^2=\|Rx-Q^Tb\|^2$
since $\|Qv\|=\|v\|$. So $Rx=Q^Tb$ and $x=R^{-1}Q^Tb$ — the normal equations
with no squaring of $\kappa(A)$. Normal equations give
$x=(A^TA)^{-1}A^Tb$, whose condition number $\kappa(A)^2$ — squaring the
condition number is precisely why you should never form $A^TA$ in floating point.
This is a foundational QR application, not a convenience.

---

## Q4 — Cholesky's hypotheses are not optional
**Q.** Which SPD matrices admit $A=LL^T$?

**A.** Exactly the symmetric positive **definite** ones. Counter-example:
$A=\begin{pmatrix}0&0\\0&1\end{pmatrix}$ is symmetric positive *semi*definite
($x^TAx=x_2^2\ge0$) and not positive definite — Cholesky fails (first pivot is
$0$). $A=\begin{pmatrix}1&1\\1&1\end{pmatrix}$ is positive semi-definite,
singular, and also fails. Semidefiniteness ⇒ you need pivoted or rank-revealing
Cholesky, or an eigendecomposition, or add $\delta I$.
Cost $\frac13 n^3$, half of LU, and it's the standard tool for sampling
(Gaussian samplers: $L$ from Cholesky of the covariance, then $z=L\varepsilon$).

---

## Q5 — QR via Gram–Schmidt vs Householder
**Q.** Which is numerically stable, and why?

**A.** Householder QR. Classical Gram–Schmidt computes $q_j$ by dividing by
$\|a_j\|$; for nearly dependent columns that norm is near zero and the loss of
orthogonality is $O(\kappa)$ — errors amplify. Modified Gram–Schmidt reorthogonalises
each step and achieves $O(\epsilon\kappa)$, and Householder QR (using reflections
$\sigma = I - 2vv^T$) achieves $O(\epsilon)$ orthogonality independent of
conditioning. Householder is what LAPACK does; "Gram–Schmidt" in most libraries
means Householder for good reason.

---

## Q6 — Cholesky and the semidefinite case
**Q.** You need $L$ for a covariance that's estimated and may be near-singular. Options?

**A.** (i) Add ridge $\Sigma+\lambda I$ and take its Cholesky — changes the
model slightly, always positive definite. (ii) Pivoted Cholesky reveals the
rank $r$ and gives a rank-$r$ approximation — the right tool for
low-rank-plus-noise structure. (iii) Eigendecomposition, keeping components
above a threshold, then $\Sigma_{trunc}\approx U\Lambda U^T$ and
$L=U\Lambda^{1/2}$. In practice option (i) with a small $\lambda$ is simplest;
option (ii) tells you whether the ridge is papering over a real rank deficiency.

---

## Q7 — The SVD is optimal for low-rank approximation
**Q.** State the Eckart–Young theorem and its consequence.

**A.** For every $k$, $A_k=\sigma_1u_1v_1^T+\dots+\sigma_ku_kv_k^T$ is the
**best rank-$k$ approximation** in both spectral and Frobenius norms, with error
$\|A-A_k\|_2=\sigma_{k+1}$ and $\|A-A_k\|_F=\sqrt{\sum_{i>k}\sigma_i^2}$.
Hence no other rank-$k$ matrix is closer. This is why SVD is the tool for
compression, denoising, and low-rank regression — and why it is expensive:
optimality comes with $O(n^3)$.

---

## Q8 — Singular values are not eigenvalues
**Q.** For $A=\begin{pmatrix}1&1\\0&0\end{pmatrix}$, compare eigenvalues and
singular values.

**A.** $A^TA=\begin{pmatrix}1&1\\1&1\end{pmatrix}$ has eigenvalues $2,0$, so
singular values are $\sqrt2,0$. Eigenvalues of $A$ are $1,0$.
Three differences: (i) singular values are $\ge0$ always; (ii) $\sigma_i$ are the
eigenvalues of $(A^TA)^{1/2}$; (iii) $\sigma_{\max}=\|A\|_2$, the spectral
norm. Practically: $\|A\|_2\ne\rho(A)$ for non-normal matrices — $\|A\|_2$ is
the correct quantity for error bounds and conditioning, $\rho(A)$ for asymptotic
growth.

---

## Q9 — When eigenvalues are complex
**Q.** $A=\begin{pmatrix}0&-1\\1&0\end{pmatrix}$ — eigenvalues? SVD?

**A.** Characteristic $\lambda^2+1$, eigenvalues $\pm i$: a $90°$ rotation, no real
eigenvalues. Singular values are both $1$ ($A^TA=I$). So: complex spectrum with
maximal singular values — a normal, orthogonal matrix. If you need real
factorisation, the Schur form $T=QTQ^T$ (real, quasi-triangular, $2\times2$
blocks for complex pairs) is the target, not Jordan form.
Practical takeaway: symmetric matrices have real eigenvalues and orthogonal
eigenvectors (a real guarantee); general matrices don't, so use SVD/Schur.

---

## Q10 — The polar decomposition
**Q.** Every invertible $A$ admits $A=QH$ with $Q$ orthogonal and $H$
symmetric positive definite. Is it unique? Which one is used for the matrix exponential?

**A.** Uniqueness: $Q$ is unique iff $A$ is nonsingular. $H=(A^TA)^{1/2}$, the
principal square root. The polar decomposition is the natural home for
logarithms: $A=e^{\log A}$ where
$\log A=\log H+\log Q$, and $\log Q=Q(\pi i K)$ for a skew-symmetric $K$ with
eigenvalues in $(-\pi,\pi)$, giving a *principal* logarithm. Inverse problems in
control (retargeting, time-optimal control) are expressed as matrix logarithms,
and computing $\log A$ via the Schur decomposition is the standard numerically
stable route.

---

## Q11 — $LDL^T$ versus $LL^T$
**Q.** Why do numerical libraries often use $LDL^T$?

**A.** For symmetric indefinite matrices you cannot form $A=LL^T$, but $LDL^T$
with an indefinite diagonal $D$ (some entries negative) always exists when $A$ is
symmetric and nonsingular. Cost $\frac13n^3$, half the symmetric LU.
Application: symmetric indefinite saddle-point systems in optimisation
(interior-point methods); also inertia computation (how many eigenvalues are
negative) comes free from the signs of $D$'s entries. LDL is also more compact:
$L$ has unit diagonal, saving storage.

---

## Q12 — Eigen-decomposition is numerical, exactness is not
**Q.** Does the symmetric eigenproblem ever fail numerically?

**A.** Yes — breakdown when off-diagonals underflow: a matrix like
$\begin{pmatrix}a&b\\b&a\end{pmatrix}$ with $|b|\ll|a|$ has eigenvectors
$\begin{pmatrix}1\\1\end{pmatrix},\begin{pmatrix}1\\-1\end{pmatrix}$ which
Gauss–Jordan on $A-\lambda I$ cannot resolve when the off-diagonal rounds to
zero in the shifted matrix. The fix is tridiagonalisation first (Householder),
then the implicit-shift QR algorithm (Francis double shift) for eigenvalues and
inverse iteration or the bisection algorithm (bisection on Sturm sequences) for
eigenvectors. Symmetric tridiagonal eigenvalue computation is provably backward
stable.

---

## Q13 — Verifying a decomposition
**Q.** How do you numerically check $A=QR$ or $A=LL^T$?

**A.** Check the residual, not the factors: $\|A-\hat Q\hat R\|_F/\|A\|_F\approx
\epsilon$ (say $<10^{-10}$ in double precision). Checking $Q^TQ-I\approx0$ tells
you about $Q$'s orthogonality, not whether $A$ was factored correctly; a wrong
$R$ with orthogonal $Q$ passes the second test and fails the first.
Better still, check the *backward* error $\|(I+E)A-\hat Q\hat R\|$ with
$\|E\|\le\epsilon\|A\|$ — that's what LAPACK's `xGECON` reports.

---

## Q14 — Rank-revealing factorisations
**Q.** How do you detect rank deficiency robustly?

**A.** SVD: count singular values above $\tau = \max(m,n)\epsilon\sigma_1$
(the standard threshold). Pivot-free QR with condition estimation (Businger–Golub
triple algorithm) for $LU$ — it finds a diagonal block close to singular without
pivoting. For the **symmetric** case, pivoted Cholesky downdates until the pivot
falls below tolerance. The eye test "is the determinant tiny?" fails badly:
$\det A$ is the product of all singular values, so a matrix with one tiny and
many large singular values can have moderate determinant. Rank deficiency is
about the *smallest* singular value.

---

## Q15 — When the decomposition tells you the algorithm
**Q.** Given a task, which decomposition?

**A.** Solve $Ax=b$ once: LU (or its $LDL^T$ for symmetric). Many $b$'s, same
$A$: LU still best. Least squares: QR, never normal equations. Sample from a
Gaussian with a given covariance: Cholesky. Condition number / rank / low-rank
approximation / pseudoinverse: SVD. Solve an ODE system or compute $e^{A}$:
Schur (real Schur for robustness; the eigen-decomposition only when you know the
matrix is normal). Principal log: Schur + inverse scaling-and-squaring.
Lowest latency: exploit structure (symmetry, bandedness, sparsity) — the
decomposition must match the matrix's structure to pay off.

---

*Self-check: Q1, Q4 and Q6 test whether you know the exact hypotheses of LU and
Cholesky. Q7 and Q13 are about optimality and verification — the two things
that separate a working implementation from a lucky one.*