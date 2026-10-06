# Vector Spaces — Quiz (15 Questions with Worked Answers)

Subspaces, bases, dimension, coordinates, and the algebraic results that decide
whether a set is a basis. Several questions test the difference between spanning
and independence, and between "dimension 2" and "any two of them".

---

## Q1 — Basis vs spanning set
**Q.** In $\mathbb{R}^3$, is $\{(1,0,0),(0,1,0),(1,1,0)\}$ a basis?

**A.** No: the third is the sum of the first two, so the set spans only the plane
$z=0$ and has dimension 2. It is a spanning set of that plane, and a *linearly
dependent* set. Basis = spans + independent. Three vectors in $\mathbb{R}^3$ can
never be dependent-free unless they are genuinely independent.

---

## Q2 — Independent but not spanning
**Q.** Is $\{(1,0,0),(0,1,0)\}$ a basis for $\mathbb{R}^3$?

**A.** Independent (no nontrivial combination vanishes) but spans a plane, not
$\mathbb{R}^3$: not a basis for $\mathbb{R}^3$, but a basis for the subspace it
spans. Key structural fact: any independent set extends to a basis and any
spanning set is thinned to one. Both operations need choice or a constructive
algorithm (Gaussian elimination does both).

---

## Q3 — Dimension of a solution space
**Q.** Dimension of the solution set of $x+2y+z=0$ in $\mathbb{R}^3$?

**A.** 2. The equation defines a plane (a hyperplane); the kernel of a
nonzero linear functional on $\mathbb{R}^3$ has dimension $3-1=2$.
Generally, $m$ independent homogeneous equations in $\mathbb{R}^n$ give
dimension $n-m$ (rank–nullity). The trap: non-linear-looking constraint
$x^2+y^2=0$ gives a single point (dimension 0), because the set isn't a
subspace. "Dimension" only makes sense for subspaces.

---

## Q4 — Basis of the space of polynomials
**Q.** Basis and dimension of $P_3(\mathbb{R})$, polynomials of degree $\le3$.

**A.** $\{1,x,x^2,x^3\}$, dimension 4. Proof of independence: a linear combination
vanishing identically forces each coefficient to be 0 (compare lowest nonzero
degree). Contrast with $P_\infty$, which has countably infinite dimension —
"dimension" can be an infinite cardinal, and finite dimension arguments (like
"$n+1$ vectors in $\mathbb{R}^n$ are dependent") need restating.

---

## Q5 — Field matters
**Q.** Does the set $\{1,\sqrt2\}$ span a 2-dimensional space over $\mathbb{R}$?
Over $\mathbb{Q}$?

**A.** Over $\mathbb{R}$: no, it's dependent ($a\cdot1+b\sqrt2=0$ with real
$a,b$ forces $a=b=0$... actually over $\mathbb{R}$ it *is* independent since
$\sqrt2$ is irrational). Careful: over $\mathbb{R}$, $\{1,\sqrt2\}$ is
independent, so it spans a 2-dimensional subspace $\mathbb{R}+\mathbb{R}\sqrt2$,
which is all of $\mathbb{R}$ only in a weird sense — no, it's a proper subspace
(the algebraic numbers). Over $\mathbb{Q}$: independent too, and it spans
$\mathbb{Q}(\sqrt2)$, a 2-dimensional $\mathbb{Q}$-space.
The point: the **same two vectors** give a 2-dimensional space over $\mathbb{Q}$
and lie in a proper subspace over $\mathbb{R}$. Dimension is field-relative.
This matters in coding: GF(2) vs GF(256) give different dimensions for the same
symbol set.

---

## Q6 — Coordinate maps are isomorphisms
**Q.** Why does a basis let you do linear algebra on coordinates?

**A.** The map $\phi:\mathbb{F}^n\to W$, $\phi(a)=\sum_ia_iv_i$, is a **linear
isomorphism** (surjective by spanning, injective by independence). Any subspace
$S\subseteq W$ has preimage $\phi^{-1}(S)$, a subspace of $\mathbb{F}^n$ — so
subspaces of $W$ correspond exactly to subspaces of $\mathbb{F}^n$, and all
the theory can be done in coordinates. This is why you can hand-wave
"change of basis" in a proof: conjugate the operator and read off the matrix.

---

## Q7 — Test for a basis of a solution space
**Q.** Which of these is a basis of $\{x\in\mathbb{R}^4: x_1+x_2+x_3+x_4=0\}$?

**A.** (a) $e_1-e_4,\ e_2-e_4,\ e_3-e_4$: each satisfies the constraint, they're
independent (compare first three coordinates), and there are 3 of them matching
the dimension ⇒ basis ✓.
(b) $e_1,e_2,e_3$: $e_1$ has sum 1 ≠ 0 ✗.
(c) $e_1-e_4, e_2-e_4, e_3-e_4, e_4$: 4 vectors in a 3-dimensional space ⇒
dependent ✗.
Both conditions — in the space and the right count — are needed. This is the
standard homogeneous-system workflow: parametrise via free variables, then
read off a basis from the parameter directions.

---

## Q8 — Intersection and sum of subspaces
**Q.** In $\mathbb{R}^3$, $U=\text{span}(e_1,e_2)$ (the $xy$-plane), $W=\text{span}(e_1,e_3)$ (the $xz$-plane). Compute $U\cap W$, $U+W$, and dimensions.

**A.** $U\cap W=\text{span}(e_1)$ (the $x$-axis), dimension 1;
$U+W=\text{span}(e_1,e_2,e_3)=\mathbb{R}^3$, dimension 3.
The formula: $\dim(U+W)=\dim U+\dim W-\dim(U\cap W)=2+2-1=3$ ✓.
This is the rank–nullity identity in subspace clothing, and the pattern
"sum can exceed the ambient dimension check" is exactly why you must account
for the intersection.

---

## Q9 — Symmetric matrices as a subspace
**Q.** Dimension of the space of $n\times n$ symmetric matrices? Show it's a subspace.

**A.** $n(n+1)/2$: entries on and above the diagonal are free. Subspace check:
zero matrix is symmetric; if $A=A^T$ and $B=B^T$ then $(\alpha A+\beta B)^T
=\alpha A^T+\beta B^T=\alpha A+\beta B$. Contrast skew-symmetric: $A^T=-A$,
diagonal forced to 0, dimension $n(n-1)/2$. Both are $3$-dimensional for $n=2$,
$6$-dimensional for $n=3$. These dimensions show up constantly in optimization
(the space of symmetric matrices is where the Hessian acts).

---

## Q10 — Direct sum and projections
**Q.** $\mathbb{R}^2 = \text{span}(e_1)\oplus\text{span}(e_1+e_2)$. Project
$(2,5)$ onto each.

**A.** Write $(2,5)=\alpha e_1+\beta(e_1+e_2)=(\alpha+\beta,\beta)$, so
$\beta=5$, $\alpha=-3$. Projection onto $\text{span}(e_1)$ is $(-3,0)$;
onto $\text{span}(e_1+e_2)$ is $(5,5)$. Sum: $(-3,0)+(5,5)=(2,5)$ ✓.
Directness: the intersection is $\{0\}$ since $\gamma e_1=\delta(e_1+e_2)$
forces $\delta=0$. Any basis of a space gives a direct-sum decomposition — that's
the geometric meaning of a basis, and it's how you turn a hard constraint
(orthogonality to a set) into independent coordinate-wise conditions.

---

## Q11 — Span vs affine span
**Q.** Is $\{(1,0),(0,1),(1,1)\}$ spanning $\mathbb{R}^2$? Can you represent
$(3,5)$ as a linear combination?

**A.** Yes, it spans (dim 2), and $(3,5)=3(1,0)+5(0,1)$ — a unique
representation since it's a basis.
But consider $\{(1,0),(0,1)\}$ and the *convex* combination question: a convex
combination of these can only reach $\{(a,b): a+b=1\}$ — the affine hull (a line),
not the whole plane. Affine span of a set is a translate of a span, and
coordinates in an affine basis need not sum to 1. Distinguishing linear from
affine combinations is essential in least-squares fitting, where you add a
column of ones precisely to convert between them.

---

## Q12 — Infinite bases need care
**Q.** Are $\{1,x,x^2,\dots\}$ a basis of $\mathbb{R}[x]$? What cardinality?

**A.** Yes, countably infinite, and every polynomial is a *finite* linear
combination — that's the part that makes it work (an algebraic basis permits
finite combinations). Cardinality argument: $\mathbb{R}[x]$ has the same
cardinality as $\mathbb{R}$, so uncountable *dimension* is impossible; but
$\mathbb{R}^\mathbb{N}$ (all sequences) does have uncountable dimension.
The pitfall: in numerical linear algebra, "dimension 1000" implies every basis
is finite; in functional analysis it may not, and notions like
"closed span" (closure!) become essential.

---

## Q13 — Change of basis
**Q.** Express $v=(1,2,3)$ in the basis $b_1=(1,0,0)$, $b_2=(0,1,1)$,
$b_3=(0,1,-1)$.

**A.** $v=\alpha b_1+\beta b_2+\gamma b_3=(\alpha,\beta+\gamma,\beta-\gamma)$.
$\alpha=1$; adding and subtracting: $2\beta=5$, $2\gamma=-1$, so
$\beta=5/2$, $\gamma=-1/2$. New coordinates: $(1,5/2,-1/2)$.
$\det[b_1\,b_2\,b_3]=-2\ne0$, so the basis is valid. The $P$ matrix
(columns = basis vectors) and the coordinates relation $v=P[v]_b$ is the
practical content: every linear-algebra routine reduces to matrix products
against a basis matrix.

---

## Q14 — Quotient space
**Q.** Let $W=\text{span}(1,2,3,4)$ in $\mathbb{R}^4$. What is $\mathbb{R}^4/W$?

**A.** Dimension $3$, and it's naturally isomorphic to $W^\perp=\text{span}(e_1-e_4, e_2-e_4, e_3-e_4)$ via the map that takes a coset's representative to its inner products with $W^\perp$. Quotient spaces are the *algebraic* form of "mod out by the irrelevant directions" — the same idea as quotienting by a null space when solving linear systems, or quotienting a group by a normal subgroup.
Its only quotient element structure: $a+W$; addition and scalar mult are well defined precisely because $W$ is a subspace.

---

## Q15 — Wedge of subspaces and directness
**Q.** Give an explicit example where two spanning sets union is not independent, and explain why naive dimension addition fails.

**A.** $\{e_1,e_2\}$ and $\{e_2,e_3\}$ in $\mathbb{R}^3$: union has 4 vectors in
dimension 3 ⇒ dependent. Naive "2+2=4 dimensions" would be wrong. The fix is the
correct formula $\dim(U+W)=\dim U+\dim W-\dim(U\cap W)$.
The practical rule: never add dimensions of overlapping spanning sets; compute
the intersection first, or reduce to row-echelon form. This exact mistake shows up
as "my null space dimension and column space dimension don't add to n" — they do,
once the intersection is accounted for.

---

*Self-check: Q2, Q11 and Q12 contrast what a basis gives with what a spanning set
gives, and Q14 shows what "modding out" means. Q5's field-relative point is the
one most often missed.*