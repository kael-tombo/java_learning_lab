# Linear Transformations — Quiz (15 Questions with Worked Answers)

Kernels, images, rank–nullity, matrix representation, invertibility and the
standard forms. Questions about hypotheses: finite vs infinite dimension,
square vs rectangular, algebraic vs geometric multiplicity.

---

## Q1 — Rank–nullity, used
**Q.** $T:\mathbb{R}^3\to\mathbb{R}^2$, $T(x,y,z)=(x+y,\ z)$. Find $\ker T$
and $\operatorname{im}T$.

**A.** $\ker T=\{(x,y,z):x+y=0,\ z=0\}=\text{span}\{(1,-1,0)\}$, dimension 1.
$\operatorname{im}T=\mathbb{R}^2$ (take $(1,0)$ from $(1,0,0)$ and $(0,1)$ from
$(0,0,1)$), dimension 2.
Check: $1+2=3$ ✓. Rank–nullity: rank + nullity = 2+1 = 3 ✓. Rank can never
exceed $\min(3,2)=2$ — this is the most fundamental inequality in linear algebra.

---

## Q2 — Rank–nullity is about the domain
**Q.** Can rank–nullity be applied without the matrix being square?

**A.** Yes. For $T:\mathbb{F}^m\to\mathbb{F}^n$ of rank $r$: $r+\dim\ker T=m$,
the dimension of the **domain**. The common slip is writing $=n$; that fails
immediately unless $r+n-\dim\ker=m$ happens to hold. Formally this is the
first isomorphism theorem: $V/\ker T\cong\operatorname{im}T$.

---

## Q3 — Invertible vs one-sided inverse
**Q.** Does $AB=I$ for square matrices imply $B=I$? Does $BA=I$?

**A.** For square matrices over a field, both do: $AB=I$ forces $A$ invertible
(det $A\cdot$det $B=1$), $B=A^{-1}$, and then $BA=I$. For **rectangular**
matrices, neither direction gives invertibility: take $A=\begin{pmatrix}1&0\\0&1\\0&0\end{pmatrix}$
($3\times2$), $B=\begin{pmatrix}1&0\\0&1\end{pmatrix}$; then $AB=I_3$ while
$B\ne I$ and $BA=\begin{pmatrix}1&0\\0&1\\0&0\end{pmatrix}\ne I_2$.
So the "square" hypothesis is load-bearing, and code that uses a non-square
pseudoinverse must be explicit about which inverse it means.

---

## Q4 — Matrix of a transformation
**Q.** $T(x,y,z)=(2x-y,\ y+z)$. Write its matrix and check on a sample vector.

**A.** Columns are images of basis vectors: $T(e_1)=(2,0)$,
$T(e_2)=(-1,1)$, $T(e_3)=(0,1)$, so
$A=\begin{pmatrix}2&-1&0\\0&1&1\end{pmatrix}$.
Check on $(1,1,1)$: $A(1,1,1)^T=(1,2)$; directly
$(2\cdot1-1,\ 1+1)=(1,2)$ ✓. The columns-are-images convention catches
most transcription errors: if you compute a column and it doesn't match, the bug
is in the convention or the arithmetic, not in the concept.

---

## Q5 — Image vs range of a restriction
**Q.** $T:\mathbb{R}^3\to\mathbb{R}^3$ rotation by 90° about $z$. Is $T$
invertible? Restricted to the $xy$-plane?

**A.** $\det A=1\ne0$, so invertible; restriction to the $xy$-plane is also
invertible on that plane. Contrast projection $P(x,y,z)=(x,y,0)$: not
invertible on $\mathbb{R}^3$ ($\ker P=\text{span}e_3$), but invertible on
$W=\text{span}\{e_1,e_2\}$, with $P|_W=\mathrm{id}$. The general pattern: a
map with a kernel still has a well-defined *bijection* between a complement of
the kernel and the image — that's exactly what the first isomorphism theorem
gives, and it's how you "cancel the null directions" in an algorithm.

---

## Q6 — Change of basis formula
**Q.** Verify $P^{-1}AP$ is the matrix of $A$ in the new basis $P$.

**A.** By definition $A|_W$ means $Av\in W$; in the new basis, coordinates of
$Av$ are $P^{-1}Av$. If $v=Pv'$ then $Av=APv'$, so coordinates are
$P^{-1}APv'$. So the new matrix is $P^{-1}AP$ ✓ (for a linear map $V\to V$).
For a map $V\to W$ with different bases, it's $Q^{-1}BP$. Diagonalising
precisely means finding $P$ with $P^{-1}AP$ diagonal — the "change of basis"
moves the hard problem into a form where eigenvalues can be read off.

---

## Q7 — Isometries
**Q.** Classify which of these are isometries: identity, reflection in a plane,
shear $\begin{pmatrix}1&1\\0&1\end{pmatrix}$, rotation by 45° in $\mathbb{R}^2$.

**A.** Isometry means $A^TA=I$: identity ✓, reflection ✓ ($A^TA=I$), rotation
✓. Shear: $A^TA=\begin{pmatrix}1&1\\1&2\end{pmatrix}\ne I$ ✗ — not an isometry.
Classically the orthogonal group splits as reflections and rotations;
$P$-orthogonal (preserving an inner product other than the standard one) is the
right notion in numerical linear algebra where $A^TA\ne I$ but
$A^TWA=W$ — Cholesky factors and QR decompositions are $P$-orthogonal.

---

## Q8 — Similarity preserves everything but the representation
**Q.** What does $A$ and $P^{-1}AP$ have in common? Name things that differ.

**A.** Same characteristic polynomial, same eigenvalues, same minimal
polynomial, same trace, determinant, rank, Jordan form (and hence algebraic and
geometric multiplicities). Different: the entries of $A$, its singular values,
its condition number, its (Euclidean) orthogonality. This is the precise scope
of "spectral methods": you may choose a basis to expose eigenvalues, but you
cannot make $A$ symmetric if it isn't — a non-symmetric matrix is
non-normalisable by an orthogonal similarity.

---

## Q9 — Rank of a product
**Q.** $A$ is $m\times n$, $B$ is $n\times p$, both rank $n$ (full rank).
Rank of $AB$?

**A.** $\text{rank}(AB)\ge\text{rank}A+\text{rank}B-n = n+n-n=n$, and cannot
exceed $n$, so rank $AB=n$ — provided $B$ has full row rank ($n$) and $A$ full
column rank ($n$), i.e. both square $n\times n$ invertible. In general
$\text{rank}(AB)\ge\text{rank}A+\text{rank}B-n$ (Sylvester), with equality when
$\operatorname{im}B\cap\ker A=\{0\}$. This bound is the "cancellation" fact:
two rank-deficient matrices can multiply to something higher than either,
which is why "rank of a product is the min" is false.

---

## Q10 — Trace of a product and cyclicity
**Q.** Is $\text{tr}(AB)=\text{tr}(BA)$?

**A.** Yes, always (both equal $\sum_i\sum_jA_{ij}B_{ji}$). Note: no assumption
that $AB$ and $BA$ are square is needed for the trace of the product itself,
but if $A$ is $m\times m$ and $B$ is $m\times m$ then $AB,BA$ are both square.
Trace is cyclic but **not** commutative with other products in general:
$\text{tr}(AB)$ need not equal $\text{tr}(A)\text{tr}(B)$... which is trivially
true since $\text{tr}(AB)\ne \text{tr}(A)\text{tr}(B)$ in general, e.g.
$A=B=I_2$: $\text{tr}(I)=2$ vs $2\cdot2=4$. This matters for quantum mechanics,
where $\rho A$ and $A\rho$ have the same trace but not the same spectrum.

---

## Q11 — Singular matrices and what nullity costs
**Q.** $A=\begin{pmatrix}1&2\\2&4\end{pmatrix}$. Describe $\ker$, $\operatorname{im}$,
and explain why $Ax=b$ is sometimes solvable.

**A.** $\operatorname{rank}=1$ (row 2 = 2·row 1), $\ker=\text{span}(2,-1)$,
$\operatorname{im}=\text{span}(1,2)$, nullity 1, rank 1, sum 2 ✓.
$Ax=b$ solvable iff $b\perp\ker A$ iff $b_1=2b_2$. A square singular matrix is
not invertible because $Ax=b$ has no solution for some $b$ and infinitely many
for the rest. Numerically: the null direction is where small perturbations
produce huge output — the reason conditioning, not invertibility, is what
matters in practice.

---

## Q12 — Jordan form and its existence
**Q.** Every matrix over $\mathbb{C}$ is similar to a Jordan form; over $\mathbb{R}$?

**A.** Over $\mathbb{C}$: yes, since the characteristic polynomial splits and you
gather generalised eigenvectors into Jordan blocks. Over $\mathbb{R}$: only if all
eigenvalues are real (otherwise you get real canonical form with $2\times2$
blocks for complex pairs). Practical consequence: computing $\exp(A)$ (matrix
exponential) reduces to a Jordan/Schur form computation plus a finite sum of
polynomials times $\lambda^k$, so $e^{tA}$ costs $O(n^3)$, not infinitely many
matrix multiplications. Matrix exponentials appear in control theory and in the
continuous-time limit of Markov chains.

---

## Q13 — Powers and growth
**Q.** If $\|A\|>1$, does $A^k$ grow? What if eigenvalues are large but $\|A\|$ small?

**A.** $\|A^k\|\le\|A\|^k$ (submultiplicative) gives an upper bound only;
$\|A^k\|$ can be much smaller. Consider the nilpotent shift
$A=\begin{pmatrix}0&1\\0&0\end{pmatrix}$: $\|A\|=1$, $A^2=0$. Take
$A=\frac12\begin{pmatrix}0&1\\0&0\end{pmatrix}$: $\|A\|=\frac12<1$ and
$A^k=2^{-k}A\to0$ — so spectral radius dominates. The correct statement:
$\lim_{k\to\infty}\|A^k\|^{1/k}=\rho(A)$ (Gelfand's formula), i.e. asymptotic
growth is governed by the spectral radius, not the norm. The transient
(norm) matters for numerical stability.

---

## Q14 — Diagonalisation criterion
**Q.** Is $A=\begin{pmatrix}1&1\\0&1\end{pmatrix}$ diagonalisable?

**A.** Characteristic polynomial $(1-\lambda)^2$: one eigenvalue $\lambda=1$ with
algebraic multiplicity 2. Geometric multiplicity: $\dim\ker(A-I)=1$ (only
$x=0$ solves), so geometric multiplicity 1 < 2 ⇒ **not diagonalisable**. It's
similar to a single Jordan block $J_2(1)$, and $A^k=I+k(A-I)$ grows linearly in
$k$ — whereas the diagonal matrix $\mathrm{diag}(1,1)$ would have $A^k=I$. Same
eigenvalues, wildly different powers. This is why the Jordan structure, not just
the spectrum, controls long-time behaviour.

---

## Q15 — Eigenvalue computation is fragile
**Q.** $A=\begin{pmatrix}\epsilon&1\\0&\epsilon\end{pmatrix}$: eigenvalues
$\epsilon,\epsilon$. What does the perturbation analysis say?

**A.** Under perturbation, eigenvalue perturbation is bounded by roughly
$|\delta\lambda|\lesssim\|E\|\cdot\kappa$, but for a defective matrix
(algebraic multiplicity 2, geometric 1) the condition number of the eigenvector
matrix is **infinite** — the eigenvectors are arbitrarily close to being linearly
dependent. So a tiny perturbation $\epsilon\to\epsilon+\delta$ makes a
$O(\delta/\|E\|)$ relative change in $\lambda$ but a $O(1)$ change in $A^k$ for
$k\sim1/\delta$. Defective matrices are numerically poisonous: the standard
advice is never to compute Jordan form numerically, only Schur form.

---

*Self-check: Q2, Q3, Q9 and Q13 each drop a hypothesis that the textbook version
of the statement quietly includes. Naming the hypothesis is the mastery test.*