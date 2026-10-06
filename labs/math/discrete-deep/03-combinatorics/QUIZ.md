# Combinatorics — Quiz (15 Questions with Worked Answers)

Counting arguments: PIE, permutations, binomial identities, derangements,
Stirling numbers, and the double counting that catches most errors.

---

## Q1 — Double counting
**Q.** How many ways to seat $n$ people around a round table? Why not $n!$?

**A.** $(n-1)!$: rotating the whole arrangement gives the same seating, and there
are exactly $n$ rotations. Reflection is *not* identified unless the table can be
flipped, which for a physical round table it can't — a frequent miscount. General
principle: count the objects with a free action of a group $G$ and divide by
$|G|$; this is orbit-counting (Burnside), which reduces to division only when the
action is free. When it isn't — necklaces with two colours and rotational
symmetry — you must use Burnside's lemma properly.

---

## Q2 — PIE, three sets
**Q.** Of 100 students, 40 study CS, 50 maths, 30 physics; 20 study CS and maths,
15 CS and physics, 10 maths and physics, and 5 study all three. How many study
none?

**A.** At least one: $40+50+30-(20+15+10)+5=80$. None: $100-80=20$.
The alternating sum is forced: the pairwise overlaps each counted the triple
intersection three times (it should be once), so the $+5$ correction restores it.
Getting this sign pattern wrong is the classic PIE error.

---

## Q3 — Binomial identity from counting
**Q.** Prove $\sum_{k=0}^n\binom{n}{k}=2^n$ by counting.

**A.** Count subsets of an $n$-set two ways. Directly: $2^n$ subsets. By size:
$\sum_k\binom nk$. Same number, so identity holds. Every identity in this area
should come with such an argument — an algebraic proof of
$\sum_k\binom nk2^{n-k}=3^n$ also exists (colourings with three colours), and both
are worth having.

---

## Q4 — Vandermonde's identity
**Q.** Count "choose 4 people from two disjoint groups of 5 and 6".

**A.** $\binom{11}{4}=330$ directly. Splitting by how many of the 4 come from the
first group: $k=0$: $1\cdot15=15$; $k=1$: $5\cdot20=100$; $k=2$: $10\cdot15=150$;
$k=3$: $10\cdot6=60$; $k=4$: $5\cdot1=5$. Sum $=330$. ✓
This is Vandermonde's convolution
$\sum_k\binom mk\binom n{r-k}=\binom{m+n}{r}$ — and the reason generating-function
multiplication corresponds to convolution. The single most useful self-check:
compute one side and the closed form independently. A mismatch means a
mis-indexed binomial ($\binom64$ vs $\binom63$ is the usual culprit), and it is
far cheaper to catch here than three steps later in an implementation.

---

## Q5 — Derangements
**Q.** 5 people, 5 hats, random assignment. Probability nobody gets their own?

**A.** $D_5=5!\sum_{k=0}^5\frac{(-1)^k}{k!}=120(1-1+\frac12-\frac16+\frac1{24}-\frac1{120})=44$.
Probability $\frac{44}{120}=\frac{11}{30}\approx0.367$. Limit as $n\to\infty$:
$1/e\approx0.3679$ — the same $e^{-1}$ as the Poisson(1) count of fixed points.
The classic miscount is $D_n=n!-\binom n1(n-1)!+\cdots$ without alternating
signs, which double-counts the overlaps.

---

## Q6 — Inclusion–exclusion with intersections
**Q.** Derive the inclusion–exclusion formula for $k$ sets from first principles
and state the condition it needs.

**A.** $|\cup_i A_i|=\sum_\emptyset\ne J\subseteq[k]}(-1)^{|J|+1}|\cap_{j\in J}A_j|$.
Element $x$ in exactly $m$ of the sets is counted $\sum_{j=1}^m(-1)^{j+1}\binom mj=1$
(identity from $\sum_{j=0}^m(-1)^j\binom mj=0$). No hypothesis needed for the
formula itself; "union bound" $|\cup A_i|\le\sum|A_i|$ needs nothing either, but
equality requires pairwise disjointness.

---

## Q7 — Complements and the principle of inclusion
**Q.** Count strings of length 4 over $\{a,b\}$ containing at least two $a$'s.

**A.** $16 - \binom40-\binom41=16-1-4=11$. Or directly
$\binom42+\binom43+\binom44=6+4+1=11$.
"Complement first" is a habit worth forming: the complement is usually simpler
and the arithmetic is less error-prone.

---

## Q8 — Permutations with repetition
**Q.** How many distinct arrangements of the letters of BANANA?

**A.** $6!/(3!\cdot2!\cdot1!)=60$. The denominator divides out permutations of
*identical* copies. Implementation warning: computing $6!=720$ and then
"dividing by factorials computed in floating point" breaks for $n\ge 21$ since
$21!>2^{64}$; compute the multinomial incrementally with integer division at
each step.

---

## Q9 — Stirling numbers, both kinds
**Q.** What counts: (a) ways to partition 10 people into 4 non-empty committees,
(b) ways to arrange 10 people in a circle so that exactly 4 of them are in
"own position" relative to some cyclic order?

**A.** (a) $S(10,4)=34105$, partitions into non-empty blocks.
(b) $\binom{10}4\cdot(4-1)!\cdot(6-1)!=210\cdot6\cdot120=151200$ — choose the
4, arrange them into cycles ($\binom{10}4\cdot3!$), permute the rest ($5!$).
Related but distinct from fixed points of a permutation, which use the other
Stirling numbers. Naming convention: $S(n,k)$ = "second kind" = partitions;
$s(n,k)$ = "first kind" = cycles. Mixing them up is a documentation-level bug.

---

## Q10 — Circular arrangements with a fixed person
**Q.** Seat $n$ people round a table, then again with Alice and Bob adjacent.
Ratio to the unrestricted count?

**A.** Total $(n-1)!$; adjacent count $2(n-2)!$; ratio $\frac{2}{n-1}$.
Method: treat Alice+Bob as a fused block (giving $(n-1)$ objects on a circle,
hence $(n-2)!$) times 2 internal orders. Blocks are the standard tool for
"must be adjacent / must not be adjacent" problems.

---

## Q11 — Counting lattice paths with a barrier
**Q.** How many monotone paths from $(0,0)$ to $(4,3)$ never go above $y=x$?

**A.** Total paths: $\binom73=35$. Bad paths (those crossing above $y=x$) are put
in bijection with unrestricted paths to a shifted target by reflecting the
initial segment up to the first crossing, giving the ballot count
$\binom{a+b}{b-1}=\binom72=21$. Good paths: $35-21=14$.
Sanity check with the diagonal case $a=b=n$:
$\binom{2n}{n}-\binom{2n}{n-1}=\frac{1}{n+1}\binom{2n}{n}$, the Catalan number,
as it must be. The reflection principle is the tool for every "stay below a
diagonal" problem (Dyck paths, ballot theorem, Bertrand).

---

## Q12 — Surjections and pigeonhole
**Q.** Show that among 13 people, two were born in the same month.

**A.** Pigeonhole: 13 objects, 12 holes (months), so some hole gets $\ge2$.
The principle generalises: if $n$ objects go into $k$ boxes with $n>k$, some box
has $\ge\lceil n/k\rceil$. Monotonicity guarantees it. Applications:
guaranteed algorithm collision (birthday paradox at $\approx1.177\sqrt{n}$
draws), hash collision bounds, and the pigeonhole argument that $2^{n}$
mappings from $n$ bits cannot be injective on $n+1$ bits.

---

## Q13 — Multisets and the product rule
**Q.** How many ways to choose 3 elements from $\{a,b,c,d\}$ with repetition
allowed?

**A.** $\binom{4+3-1}{3}=\binom63=20$ (stars and bars). This is also the number
of monomials $x_ax_bx_cx_dx_e$ of degree 3 in 5 variables — same generating
function. Why the product rule works: a choice sequence is determined by how many
of each type, and stars-and-bars counts those.

---

## Q14 — Generating function reading
**Q.** How many solutions to $x_1+x_2+x_3=7$ with $x_i\ge0$?

**A.** Coefficient of $z^7$ in $\left(\frac1{1-z}\right)^3$, which by the
negative-binomial expansion is $\binom{7+2}{2}=\binom92=36$.
If additionally $x_1\le3$, subtract $\binom{3+2}{2}=10$ for the violating
solutions ($x_1'\!=x_1-4\ge0$), giving $26$. That subtraction is the standard
"bounded variable" technique, and it is exactly the stars-and-bars
$+C$ inclusion–exclusion in disguise.

---

## Q15 — Double counting as a correctness check
**Q.** In a directed graph with 6 vertices and 12 directed edges, how many pairs
$(u,v)$ with an edge from $u$ to $v$ and an edge from $v$ to $u$?

**A.** Not determined by the counts alone — the degree distribution matters. If
you claim a formula from counts only, look for a second way to count the same
set. E.g. sum of out-degrees is 12 and sum of in-degrees is 12; mutual pairs $M$
satisfy no constraint beyond $M\le6$ and $M\le6$. Concrete counter-examples
exist for both $M=0$ and $M=6$ with 12 edges. The lesson: "total degree" does
not determine "2-cycles"; graph structure, not degree sums, is required.

---

*Self-check: Q5, Q11 and Q15 each have a tempting shortcut that gives a wrong
number. Naming the shortcut is the point.*