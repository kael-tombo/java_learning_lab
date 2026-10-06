# Applied Linear Algebra — Quiz (15 Questions with Worked Answers)

PCA, least squares, PageRank, SVD compression, and the linear algebra hidden
inside applied methods. Focus: which decomposition solves which problem, and
what the modelling assumptions are.

---

## Q1 — PCA is an eigenproblem, not an SVD problem
**Q.** How do you compute the principal components of data $X\in\mathbb{R}^{n\times p}$?

**A.** Center the columns ($X_c=X-\bar x$). Either
(a) form the covariance $S=\frac1{n-1}X_c^TX_c$ ($p\times p$) and take
eigenvectors (cost $\mathcal{O}(np^2+p^3)$, good when $p\ll n$), or
(b) do an SVD $X_c=U\Sigma V^T$ and take the first $k$ columns of $V$ (cost
$\mathcal{O}(npk)$, good when $n\ll p$, and more accurate).
Both give the same answer up to sign and are equivalent through
$V=\Sigma^{-1}X^TU$ — the "eigenvectors of $X^TX$" are the right singular vectors
of $X$. **Never form $X^TX$** when $n>p$: it squares $\kappa(X)$.
Gotcha: PCA centers but does not scale — a feature in dollars and one in cents
will dominate; standardise first if units are arbitrary.

---

## Q2 — Total variance is the trace
**Q.** For data with $p$ centred features, what is $\sum_i\sigma_i^2$?

**A.** $\sum_{i=1}^{p}\lambda_i=\operatorname{tr}(X^TX)$, i.e. the total variance.
Proof: eigenvalues of $X^TX$ sum to its trace. Consequence for choosing $k$:
$k$ components with $\frac{\sum_{i\le k}\sigma_i^2}{\sum_i\sigma_i^2}>0.95$
explains 95% of the variance — a *descriptive* criterion, not a performance one.
You must centre first: $\operatorname{tr}(X^TX)$ includes the mean-squared
magnitude of the mean, which is not variance.

---

## Q3 — Ridge regression is shrinkage, not feature removal
**Q.** Why can't ridge regression set a coefficient exactly to zero, and what does
it do instead?

**A.** The LASSO objective $\min\|y-X\beta\|_2^2+\lambda\|\beta\|_1$ has a
diamond-shaped constraint ball whose corners are on coordinate axes — the
solution hits corners, so $k$ coefficients become exactly 0. Ridge uses a
*spherical* ball: its boundary touches axes but the minimiser generically doesn't,
so all coefficients stay nonzero (just shrunk). Geometrically: lasso's sparsity
comes from the shape of the constraint set. Ridge has closed form
$\hat\beta=(X^TX+\lambda I)^{-1}X^Ty$ via the SVD (compute
$B=X_c^TX_c/(n-1)+n\lambda I$, solve $B^{-1}\frac1nX^TXy$ in SVD form);
LASSO has no closed form (coordinate descent or proximal gradient).
Practical: elastic net $\lambda_1\|\beta\|_1+\lambda_2\|\beta\|_2^2$ combines them.

---

## Q4 — Least squares and the pseudoinverse
**Q.** $X\in\mathbb{R}^{n\times p}$ rank-deficient. What is the least-squares
solution set?

**A.** $X^+$ is the Moore–Penrose pseudoinverse: for $X=USV^T$ with singular
$\sigma_1..\sigma_r>0$, $X^+=V\Sigma_r^{-1}U^T$. Then $X^+y$ is the minimum-norm
solution; the full solution set is $X^+y+(I-X^+X)z$ for arbitrary $z$.
For any $x$: $X^+y$ is the solution, and among solutions it's the one of smallest
$\ell_2$-norm (and satisfies $x\in\text{row}(X)$).
Never invert the normal equations when $X^TX$ is singular — use SVD/QR with
column pivoting, or add ridge. Rank determination via SVD (Q13 of the
decompositions lab) is the numerically honest approach.

---

## Q5 — Logistic regression: the IRLS interpretation
**Q.** Why is IRLS "iteratively reweighted least squares"?

**A.** Newton's method on the log-likelihood gives
$w_i=\sigma(z_i)(1-\sigma(z_i))$ and iterates weighted least squares on
$z=\eta+X\beta$ with weights $w$. Solving each WLS by QR or Cholesky is the
"reweighted least squares" part. But IRLS can fail to converge (separable data,
overfitting, extreme features) — modern practice uses L-BFGS or
quasi-Newton instead, or regularised logistic regression ($+$ ridge).
Also: watch for separation, which sends coefficients to infinity; Firth's
penalised likelihood or $L_2$ regularisation fixes it.

---

## Q6 — PageRank is a power method
**Q.** Write the PageRank equation and describe what damping $d$ does.

**A.** $r=d^T\left[(1-\alpha)P+\alpha\frac{1}{n}\mathbf{1}\mathbf{1}^T\right]r$
with $P$ the (column-stochastic) random walk matrix, $d$ a teleportation vector.
Convergence is guaranteed by Perron–Frobenius (the damped matrix is positive
primitive, so $\rho<1$). $d$ encodes PageRank's own bias toward hubs; with
$d=1/n$ you get the "surfer" model. Problems: the matrix-free formulation is
essential ($\mathbf1\mathbf1^T r$ is cheap; forming the matrix is $O(n^2)$),
personalisation vectors break symmetry (and can create rank-deficient cases
requiring a dead-man's switch). Power iteration converges as
$O(\log(1/\epsilon)/\alpha)$ and parallelism comes from sparse matrix-vector
products.

---

## Q7 — Recommender systems: implicit vs explicit
**Q.** Why does PageRank work on the user-item graph but not directly on
user-item data?

**A.** PageRank needs random walk steps; user-item data isn't a walk matrix.
For implicit feedback: normalise the user-item matrix $R$ to a row-stochastic
matrix (or $RR^T$) and run random walks. For explicit feedback (ratings),
normalise ratings by subtracting the user mean $R_{ui}-\bar r_u$ first —
otherwise item-level biases swamp the low-rank structure. The best-known method
**is** biased matrix factorisation: $\hat r_{ui}=\mu+b_u+b_i+q_i^Tp_u$, i.e.
mean + biases + low rank. SVD++ / implicit ALS work better than pure SVD
because they add neighbourhood information.

---

## Q8 — Kalman filter is a linear algebra problem
**Q.** Write the linear Gaussian filtering update in matrix form.

**A.** Predict: $\hat x^-=A\hat x$, $P^-=APA^T+Q$; correct with
$K=P^-C^T(CP^-C^T+R)^{-1}$, $\hat x=\hat x^-+K(y-C\hat x^-)$,
$P=(I-KC)P^-$. Cost $O(n^3)$ per step for the inverse — Joseph form
($P=(I-KC)P^-(I-KC)^T+KRK^T$) keeps symmetry and positive definiteness, which
numerical drift otherwise destroys. Square-root filters (Cholesky-based) keep
the "square root" so $P$ stays PSD in floating point.

---

## Q9 — Least-squares collocation on a mesh
**Q.** How do you fit $x^2+y^2=r^2$ (unknown $r$) to a scattered point cloud?

**A.** Linearise: $2r\,dr=x_i^2+y_i^2$ at $r=r_0$; so $dr=\frac{x_i^2+y_i^2}{2r_0}-r_0$.
Solving $\min\sum_i(\text{residual})^2$ for the single unknown $r$ is a 1-parameter
least-squares problem; use the variable-projection trick — solve for $r$ by a
root find on the derivative of the residual norm. For a general circle
$x^2+y^2+Dx+Ey+F=0$, it's an ordinary linear least-squares problem in
$(D,E,F)$ — **algebraic** fitting. But the algebraic fit is biased (minimises
radial error); the **geometric** fit minimises true distance and needs
non-linear least squares (Gauss–Newton). This algebraic-vs-geometric distinction
is the classic RANSAC-vs-least-squares decision in point-cloud fitting.

---

## Q10 — Recommenders and cold start
**Q.** Cold start comes in three flavours. Which does collaborative filtering solve?

**A.** (1) **New user**: no ratings → MF gives $q_i^Tp_{\text{new}}=0$ (predicts
the global mean plus biases). Fixed by content features, demographics, or asking
for a few ratings. (2) **New item**: fixed by content-based item features or
metadata. (3) **New system**: fixed by popularity/freshness and exploration.
CF solves *none* of these — it needs both user and item to have interacted. This
is why production recommenders are hybrids, and why exploration (bandits) is
needed even after the model is trained.

---

## Q11 — LSA is SVD in disguise
**Q.** Latent Semantic Analysis does what to a term-document matrix, and what
does truncating lose?

**A.** $M=UDV^T$ (SVD of the term–document matrix); keeping top $k$ gives
$\hat M_k=U_kD_kV_k^T$ — Eckart–Young optimal (Q7 of decompositions lab).
Loses: (i) high-frequency detail; (ii) **negative** eigenvalues — LSA's
truncation keeps only $d_i>0$, discarding the "anti-correlation" structure,
though $d_i<0$ terms carry valid negative evidence in LSA; (iii) nothing corrects
for the underlying co-occurrence counts being dominated by frequent terms.
For retrieval, cosine similarity in the truncated space handles spelling/noise
better than raw counts; but truncation can hurt precision for specific queries.
That's why BM25 usually beats LSA for search while LSA wins for query expansion
and clustering.

---

## Q12 — Random projection and Johnson–Lindenstrauss
**Q.** Does projecting $\mathbb{R}^n\to\mathbb{R}^k$ preserve distances? Under what
condition?

**A.** JL lemma: for a fixed set of $n$ points, a random projection to
$k=O(\epsilon^{-2}\log n)$ dimensions preserves all pairwise distances within
$1\pm\epsilon$ **with high probability**. Explicit construction (Achlioptas):
$3k$ coin-flip rows, entries $1/\sqrt{k}$ for $+$, $-1/\sqrt{k}$ for $-$, $0$ else.
The proof: for any fixed pair, squared distance distortion has expectation 1 and
concentrates by Hoeffding; a union bound over $O(n^2)$ pairs gives high
probability simultaneously. So: $n$-dim vectors compress to $O(\log n)$
dimensions — this is the foundational result enabling LSH, approximate
nearest neighbour search, and sketching. Distances to *new* points are not
guaranteed — only for the fixed set (or with a data-dependent seed).

---

## Q13 — Matrix completion and rank
**Q.** Suppose you observe a handful of entries of an $n\times n$ matrix known a
priori to have rank $r<n$. Can you recover it exactly?

**A.** Yes if the observed entries hit a "spanning forest" pattern — each row and
column needs $r$ observed entries. Information-theoretic counting: the unknown
matrix has $nr-r^2/2$ free parameters (Grassmannian dimension) so $O(nr)$
observations suffice. Algorithmic reality: alternating least squares or a
hard-impute-then-SVD loop works when entries are uniformly random ($O(nr^2\log^2n)$
observations suffice for exact recovery via RIP-style spectral methods). But
if the missingness is structured (a whole block missing) recovery is
information-theoretically impossible — non-uniform sampling breaks these theorems.
This is why missing-at-random vs missing-not-at-random is a first-order modelling
question, not a detail.

---

## Q14 — Regularisation in the SVD form
**Q.** Ridge from SVD: why is truncating small singular values bad?

**A.** Ridge solution in SVD coordinates: $\hat\beta=\sum_i\frac{\sigma_i u_i^Ty}
{\sigma_i^2+\lambda}v_i$. The filter factor $f(\sigma)=\frac{\sigma}{\sigma^2+\lambda}$
is a *shrinkage* of each component, not a hard truncation: large $\sigma$
down-weighted slightly, tiny $\sigma$ suppressed. Truncation drops components
entirely; ridge shrinks them. For noisy data ridge is better (less variance); for
exact low-rank data truncation is exact and better.
Ridge and the truncated SVD are equivalent when $f(\sigma)=1[\sigma>\tau]$,
i.e. for some $\tau$; otherwise they differ. Tikhonov (general $L$) extends
both.

---

## Q15 — The one-line summary of which tool for which problem
**Q.** Match: (a) best rank-$k$ approximation, (b) least squares, (c) Gaussian
sampler with a given covariance, (d) fast solution of a symmetric banded system,
(e) principal logarithm of a matrix.

**A.** (a) SVD; (b) QR (or Cholesky on the normal equations for small, well-conditioned
problems); (c) Cholesky; (d) banded Cholesky/LU (cost $O(nb^2)$ for bandwidth $b$,
vs $O(n^3)$ dense — e.g. the Thomas algorithm, identical in essence to Cholesky);
(e) Schur + inverse scaling-and-squaring, or (if $A$ is SPD) $\log A\approx\frac{A-I}{A+I}$
scaled, with Halley iteration for accuracy.
Overarching rule: exploit the matrix's **structure** (symmetry, rank, sparsity,
bandedness, stochasticity) before reaching for a general dense factorisation.
A generic $O(n^3)$ call on a structured problem is leaving a factor of $n$
on the table.

---

*Self-check: Q1, Q4 and Q14 turn on recognising when NOT to form $X^TX$. Q5, Q9
and Q13 turn on distinguishing a linear problem from a disguised non-linear one.*