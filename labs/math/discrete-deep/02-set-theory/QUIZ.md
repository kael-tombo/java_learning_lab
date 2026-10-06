# Set Theory — Quiz (15 Questions with Worked Answers)

Cardinality, injections, equivalence relations, partitions, and the counting
identities that actually get used.

---

## Q1 — Bijection, not equality
**Q.** Give a bijection $\mathbb{N}\to\mathbb{Z}$ and explain why "they're the
same size" does not mean they're the same set.

**A.** $f(n)=2n$ for $n\ge0$ and $f(n)=-2n-1$ for $n<0$: $0\mapsto0,1\mapsto2,
2\mapsto4$ and $-1\mapsto1,-2\mapsto3$. Injectivity and surjectivity are
immediate from the even/odd split. A bijection is a *structured correspondence*
— it can be composed, and different bijections give different structures (the
evens/odds split groups by parity, another by ranges). The Cantor–Bernstein
theorem says injections both ways suffice.

---

## Q2 — Schröder–Bernstein
**Q.** Show $\mathbb{Q}$ injects into $\mathbb{N}$ and $\mathbb{N}$ injects into
$\mathbb{Q}$. Does that prove a bijection?

**A.** Yes, by Cantor–Bernstein. $\mathbb{N}\hookrightarrow\mathbb{Q}$ via
$n\mapsto n$. $\mathbb{Q}\hookrightarrow\mathbb{N}$ via the height enumeration:
list reduced fractions $(a,b)$, $b>0$, by increasing $a+b$, then by increasing
$a$. Each height level is finite, so the enumeration is a bijection onto $\mathbb{N}$.
Note the construction requires putting fractions in **lowest terms**; otherwise
$\frac12$ and $\frac24$ duplicate and you build a map that is not injective.

---

## Q3 — Cantor's diagonal
**Q.** Prove $\mathbb{R}$ cannot be listed. Why does the same argument fail for
$\mathbb{Q}$?

**A.** Given a list $r_1,r_2,\dots$, write $r_i$'s decimal expansion and form
$d_n$ = $r_nn + 1$ (where $r_{nn}$ is the $n$th digit), avoiding $9$ to dodge
double representations. Then $d\notin\{r_n\}$ for every $n$. Diagonalisation
works because each real is specified by an *infinite* sequence indexed by the
same $\mathbb{N}$ as the list. $\mathbb{Q}$ has no such self-description: its
enumeration is by finite height, and a diagonal digit scheme doesn't apply.
The deeper reason: Cantor's theorem $|A|<|A\times A|$ and
$|A\times A|=|A|$ both hold for countables but $|\mathbb{R}|<|\mathbb{R}\times\mathbb{R}|$.

---

## Q4 — Power set grows strictly faster
**Q.** Show $|S| < |\mathcal{P}(S)|$ for every set $S$. Give the injection used.

**A.** Diagonalisation again: map $A\in\mathcal{P}(S)$ to the subset of subsets
differing on membership of $a$. Concretely, assume a surjection $f\colon S\to
\mathcal{P}(S)$ and let $D=\{s\in S: s\notin f(s)\}$; then $D\neq f(s)$ for
every $s$, contradiction. Hence no surjection, hence $|S|\le|\mathcal{P}(S)|$,
and strict because the surjection would have been the easy direction. This
single fact drives undecidability (Cantor's undecidability of ZFC,
$\log_2 2^{\aleph_0}=\aleph_1$ under CH), and the practical $2^n$ blow-up in
subset enumeration.

---

## Q5 — Equivalence relations: the three checks
**Q.** Verify that "$\sim$ defined on $\mathbb{Z}$ by $a\sim b$ iff
$a-b$ is even" is an equivalence relation, and identify the classes.

**A.** Reflexive: $a-a=0$ even ✓. Symmetric: $a-b$ even ⇒ $b-a=-(a-b)$ even ✓.
Transitive: $a-b$, $b-c$ even ⇒ $a-c$ their sum, even ✓. Classes: the two
parities. The general theorem — every equivalence relation partitions its set,
and conversely every partition induces one — is the bridge to DSU-style
algorithms and to using partial functions ($f(x)=y$ iff $x\sim y$).

---

## Q6 — Partial functions and equivalence classes
**Q.** A relation $R$ is a partial function iff it is serial in the domain sense.
State it and connect to equivalence.

**A.** $R$ is a partial function if every element has **at most** one image
(antisymmetry of function-hood: $xa\in R\wedge xb\in R\Rightarrow a=b$). If
instead every element has **at least** one image and $R$ is symmetric, $R$ is
an equivalence relation. Proof: reflexivity isn't automatic, but the relation
$x\approx y \iff$ "there is a zigzag of $R$-steps" closes it into one. That is
precisely why connectivity in a graph is an equivalence relation, and why a
graph-theoretic "component" is a class.

---

## Q7 — Counting: inclusion–exclusion
**Q.** How many integers in $[1,100]$ are divisible by 2, 3 or 5?

**A.** $50+33+20-16-10-6+3=74$. Pairs: $\lfloor100/6\rfloor=16$,
$\lfloor100/10\rfloor=10$, $\lfloor100/15\rfloor=6$; triple $\lfloor100/30\rfloor=3$.
$103-32+3=74$. The pattern — add singles, subtract pairs, add triples — is PIE;
you need the alternating sum because pairwise overlaps re-add the triple
intersection. For $k$ sets, the formula has $2^k-1$ terms, which is the standard
complexity complaint.

---

## Q8 — Surjections from a formula
**Q.** How many onto functions $\{1,2,3\}\to\{1,2\}$ exist? General formula?

**A.** $2^3-2=6$: subtract the constant functions, or use inclusion–exclusion
$\sum_{j=0}^{2}(-1)^j\binom{2}{j}(2-j)^3=8-2=6$.
General: $k!S(n,k)$ where $S(n,k)$ is a Stirling number of the second kind —
partitions of $n$ elements into $k$ non-empty blocks, each block a fibre.
Confusing this with $S(n,k)$ the other kind ($k!$ permutations of $n$ with
exactly $k$ cycles) is a standard notation collision.

---

## Q9 — Distinguishable balls, indistinguishable boxes
**Q.** Put 5 identical balls into 3 labelled boxes; how many? Put 5 distinct
balls into 3 identical boxes?

**A.** Identical/identical-with-labels: stars and bars, $\binom{5+3-1}{3-1}=\binom72=21$.
Distinct balls, identical boxes: $S(5,3)=25$. Both are different questions
masquerading as the same sentence — the labels are where the combinatorics
lives. In code, this distinction shows up as multiset vs set handling.

---

## Q10 — Set operations and De Morgan
**Q.** Write $\overline{A\cap B}$ and $\overline{A\cup B}$ using only the other
operation.

**A.** $\overline{A\cap B}=\bar A\cup\bar B$, $\overline{A\cup B}=\bar A\cap
\bar B$. Proof for the first: $x\in\overline{A\cap B}\iff x\notin A\cap B
\iff \neg(x\in A\land x\in B)\iff x\notin A\lor x\notin B$. It matters in
practice because "NOT (a AND b)" pushes down to "NOT a OR NOT b" — which is
what lets a query planner rewrite conjunctions into indexable range scans.

---

## Q11 — Intersections of shrinking sets
**Q.** $A_n=[n,\infty)$. What is $\bigcap_n A_n$ and $\bigcup_n A_n$?

**A.** $\bigcap_n A_n=\varnothing$ (no real is $\ge$ every $n$) and
$\bigcup_n A_n=(0,\infty)$ (any positive real is $\ge1$). The general pattern:
for $A_n$ decreasing ($A_{n+1}\subseteq A_n$), $\bigcap A_n$ can be empty —
as here. De Morgan turns the empty intersection into an infinite union of
complements, which is why $\bigcup_n(-\infty,-n)=\varnothing$. These
identities are the mechanism behind continuity from below/above in measure
theory.

---

## Q12 — Cartesian products are not disjoint
**Q.** How many distinct pairs $(a,b)$ with $a\in\{1,2\}$, $b\in\{1,2,3\}$?

**A.** $2\cdot3=6$, all distinct. The trap is treating $A\times B$ and
$B\times A$ as the same set — they are naturally in bijection (swap) but as
sets of *ordered* pairs they are disjoint unless $A\cap B\ne\varnothing$ and
specific elements coincide. For products of the same set, $A\times A$ pairs
$(a,b)$ and $(b,a)$ as distinct elements, so $\{1,2\}^2$ has $4$ elements, not $3$.

---

## Q13 — Cardinal arithmetic is not ordinary arithmetic
**Q.** Is $\aleph_0+\aleph_0=\aleph_0$? Is $\aleph_0\cdot\aleph_0=\aleph_0$?
Is $2^{\aleph_0}=\aleph_0$?

**A.** Yes, yes, **no**. $\mathbb{N}\times\mathbb{N}$ is countable (encode
$2^{a}\cdot3^{b}$ by prime factorisation), but $\mathbb{R}$ is uncountable by
Cantor. So $|\mathbb{N}|^2=|\mathbb{N}|$ while $|\{0,1\}^{\mathbb{N}}|>\aleph_0$:
countable sequences of bits are strictly more numerous than naturals. The
analogy to fall for in algorithms: binary strings of length $n$ number $2^n$
while $n$-bit integers number $2^n$ too, but *all* finite binary strings
number $\aleph_0$ and *all infinite* binary strings number $2^{\aleph_0}>\aleph_0$.

---

## Q14 — Choosing the right power set operation
**Q.** You need "all subsets of size 2" of a 100-element set. How, and why not
enumeration?

**A.** Compute directly: $\binom{100}{2}=4950$. Enumerating $\mathcal{P}(S)$
means $2^{100}$ items. The general lesson: the power set is an *abstraction* for
"any subset" questions; when the question constrains the size or the
structure, work with the constrained family (a level of the boolean lattice)
instead of the whole lattice.

---

## Q15 — Lattice structure
**Q.** Which set operations form a lattice, and what does the distributive law
say about sets vs numbers?

**A.** $(\mathcal{P}(S),\subseteq,\cup,\cap)$ is a lattice: every pair has a
join ($\cup$) and meet ($\cap$). But set **union is distributive** over
intersection: $A\cup(B\cap C)=(A\cup B)\cap(A\cup C)$; arithmetic addition is not.
It is dual, not isomorphic: complements reverse the lattice order and swap
meet/join — the whole apparatus of complement-dual identities in probability
($P(A\cup B)=P(A)+P(B)-P(A\cap B)$) rests on this distributive structure, which
arithmetic itself lacks.

---

*Self-check: Q5, Q11 and Q15 are the ones where a plausible intuition
("equivalences are automatic", "countable means small", "sets are like numbers")
is exactly what makes the answer surprising.*