# Probability Axioms — Quiz (15 Questions with Worked Answers)

Kolmogorov's axioms, countable additivity, conditional probability, inclusion–
exclusion, and the distinctions between measure-theoretic probability and the
intuition that misleads people.

---

## Q1 — What the axioms do and do not say
**Q.** State the three axioms and one thing each does not determine.

**A.** (1) $P(\Omega)=1$; (2) $P(\Omega)=\sum_iP(\{A_i\})$ for pairwise disjoint
sets; (3) $P(A)\ge0$ for measurable $A$.
They do **not** determine the actual values — the axioms plus the assignment
$P(\{1,\dots,6\})=1/6$ define the fair die; different assignments give different
models. Nor do they determine the *independence* of events: independence is an
additional property, not an axiom, and it is not implied by anything else. Nor
do they forbid $\sigma$-additivity failure for uncountable collections: countable
additivity only constrains countable disjoint unions, so $P([0,1])=1$ with every
singleton having probability 0 is perfectly consistent (this is the
Lebesgue/coin-toss model — "the point where the infinite coin tosses land").

---

## Q2 — Countable additivity vs finite additivity
**Q.** A function assigns $P(\text{any interval})=0$ and $P(\text{whole line})=1$.
Is it a probability?

**A.** Under countable additivity: **no**, because $\mathbb{R}=\bigcup_{n}(\text{a
bounded interval of size }n)$ is a countable disjoint union of null sets, forcing
$P(\mathbb{R})=0\ne1$. Under *finite* additivity it is fine. The distinction is
the whole point of Kolmogorov's choice: finite additivity permits "every point
has probability 0 yet the line has probability 1", which is exactly the
non-standard analysis construction of a uniform distribution on all of $\mathbb{R}$.
The practical consequence: any proof that decomposes an event into countably
many pieces requires countable additivity, and that's a real constraint in
algorithmic work (e.g. a "countably infinite" stream of payments).

---

## Q3 — $P(A^c)$ and complements
**Q.** Derive $P(A^c)=1-P(A)$ and check monotonicity.

**A.** From $P(\Omega)=P(A\cup A^c)=P(A)+P(A^c)$ (disjoint) — the complement axiom.
Monotonicity: $A\subseteq B\Rightarrow B=A\sqcup(B\setminus A)$ so
$P(B)-P(A)=P(B\setminus A)\ge0$. Monotonicity is where the non-negativity axiom
does its work; without it the two axioms alone allow "negative probabilities".

---

## Q4 — Inclusion–exclusion for events
**Q.** Three events with $P(A)=P(B)=P(C)=0.5$, pairwise intersections $0.3$, triple
$0.1$. Compute $P(A\cup B\cup C)$.

**A.** $1.5-0.9+0.1=0.7$. Verify feasibility: yes, these values are consistent
(since $0.1\le0.3$). Inclusion–exclusion always has the alternating pattern, and
the reason is bookkeeping: an outcome in all three sets is counted $3$ times by
the singles, $\binom32=3$ subtracted times, so net $3-3=0$, needing $+1$ for the
triple term. For $k$ events with no $k$-wise independence this is the only
correct formula.

---

## Q5 — Complementarity and mutual exclusivity are different
**Q.** If $P(A\cup B)=1$, is $A\cap B=\varnothing$?

**A.** No. $P(A\cup B)=P(A)+P(B)-P(A\cap B)=1$ can hold with
$P(A\cap B)>0$. Counter-example: $P(A)=P(B)=0.7$, $P(A\cap B)=0.4$ gives
$1.4-0.4=1$. $P(A\cup B)=1$ means only that *together* they cover everything.
$P(A\cap B)=0$ is what "mutually exclusive" means, and $P(A\cap B^c)=0$ means
$A$ implies $B$. Three distinct relations routinely conflated.

---

## Q6 — Independence is not mutual exclusivity
**Q.** A fair coin: are H and T on a single toss independent? On two tosses?

**A.** Single toss: $P(H\cap T)=0$ and $P(H)P(T)=\frac14$, so **not** independent —
they're mutually exclusive. Two tosses: $P(\text{H first}\cap \text{H second})=\frac14=\frac12\cdot\frac12$,
independent. The lesson: independent random variables have independent
*events*, and mutually exclusive events are never independent (except for null
events). Saying "independent" about variables on the same outcome space must be
checked.

---

## Q7 — Conditional probability definitions agree
**Q.** Show the conditional probability definitions coincide.

**A.** Definition (ratio): $P(A\mid B)=P(A\cap B)/P(B)$ for $P(B)>0$.
Definition (regular conditional / limit): $\lim_{\epsilon\to0}P(A\cap B_\epsilon)/
P(B_\epsilon)$ for shrinking neighbourhoods $B_\epsilon\downarrow B$ — this equals
the ratio only under mild regularity and can differ for pathological $B$ (singular
conditionals in continuous settings). The finite-space version with weights,
$P(A\mid B)=w(A\cap B)/\sum_{c\in B}w(c)$, is the algebraic generalisation.
Under either, $P(B\mid B)=1$, $P(A\mid A)=1$, $P(\Omega\mid B)=1$,
$P(\varnothing\mid B)=0$ — verify these; they're how you catch broken
implementations of conditional probability.

---

## Q8 — Law of total probability and Bayes
**Q.** $P(A\mid B_1)=0.5$, $P(A\mid B_2)=0.1$, $P(B_1)=0.3$, $P(B_2)=0.7$.
Compute $P(A)$ and $P(B_1\mid A)$.

**A.** $P(A)=0.5\cdot0.3+0.1\cdot0.7=0.15+0.07=0.22$.
$P(B_1\mid A)=\frac{0.5\cdot0.3}{0.22}=\frac{0.15}{0.22}=0.6818$.
Bayes: the "prior" $0.3$ gets multiplied by the likelihood ratio $5$ to give the
posterior. This is the entire machinery behind naive Bayes classifiers and
posterior inference — partition by the conditioning events, weight by their
probabilities, renormalise.

---

## Q9 — Independence of many events: mutual vs $k$-wise
**Q.** Four fair coin tosses. Is the family mutually independent? Are all triples?

**A.** Yes and yes: for any subset $S$ of size $k$,
$P(\bigcap_{i\in S}E_i)=2^{-k}=\prod_{i\in S}P(E_i)$. Mutually independent means
**all subsets**, which is a strictly stronger requirement than $k$-wise
independence (every subset of size $\le k$). Counter-example of the distinction:
four events where every three are independent but the family isn't — constructible,
and the reason people must be careful when they verify independence only pairwise.
For coin tosses the answer is genuine mutual independence, but verifying it for
real data requires testing up to $n$-wise independence, which is intractable.

---

## Q10 — Borel–Cantelli
**Q.** Let $A_n$ = "coin $n$ shows heads" for a fair coin. Does $\sum_nP(A_n)=\infty$
imply infinitely many occur?

**A.** By Borel–Cantelli II (independence + divergence), $\limsup A_n$ has
probability 1 — heads occurs infinitely often almost surely. By BC I
(no independence needed), $\sum_nP(A_n)<\infty$ implies only finitely many occur.
So divergence alone needs independence; convergence never does.
The quantitative flip side: for independent events, P(no $A_n$ in $N..M$)
$=\prod(1-p_n)\le e^{-\sum p_n}$, so seeing no heads in 200 fair tosses has
probability $2^{-200}\approx10^{-60}$. "How long until the first head" is
geometric with mean 2, not $1/p$ by some magic.

---

## Q11 — Random variables in the axioms' language
**Q.** Define a random variable and check $X\equiv c$ is one.

**A.** $X:\Omega\to\mathbb{R}$ measurable w.r.t. $(\Omega,\mathcal F,P)$.
For $X\equiv c$: $\{X\le a\}=\Omega$ for $a\ge c$ and $\varnothing$ for $a<c$, both
measurable ✓. Degenerate variables are legitimate; there's no requirement that
$X$ be "random" in any informal sense. What measurability buys: preimages of
Borel sets are events, so $\mathbb{E}[f(X)]$ is well-defined — the definition of
expectation is an integral against $P$, not an informal average.

---

## Q12 — Rejection sampling preserves the measure
**Q.** To simulate from $f\propto g$ on $[0,1]$ using envelopes, why does
accepting with probability $g/g_{\max}$ work?

**A.** The accepted density is
$\frac{g(x)/g_{\max}}{1}\cdot\frac{g_{\max}}{\int g}=g(x)/\int g$. Two factors:
acceptance converts $g$ into the (sub)probability $g/g_{\max}$; normalisation by
$\int g$ restores a density integrating to 1. In general, if $f$ and $g$ are
densities and $M$ is known with $f\le Mg$, accept with probability $f(x)/(Mg(x))$ —
**importance sampling**, whose variance is $\chi^2(f/g)$ and whose weights matter
when you also carry other functions of $X$ (self-normalised importance sampling).

---

## Q13 — Probabilities of point events in continuous spaces
**Q.** $X\sim\text{Uniform}[0,1]$. $P(X=0.5)$?

**A.** $0$. Every singleton has probability 0, yet $P(X\in[0,1])=1$. This is not
contradictory: $[0,1]$ is a countable union of singletons and countable
additivity of zeros gives 0 — contradiction? No: the union in Q2 that broke
finite additivity was over the *whole line*, uncountable. Within $[0,1]$ you
cannot write it as a countable union of null sets; the covering needs
uncountably many pieces. This is the crux: **Lebesgue measure is not atomised by
points**, and any argument that "sums over all points" is invalid.

---

## Q14 — Borel–Cantelli / independence in practice
**Q.** A monitoring system flags an anomaly whenever $p$-value $< 0.05$ and the
anomalies are independent across days. Expected number of alerts per year?

**A.** $365\cdot0.05\approx18$ expected false alerts per year, and Borel–Cantelli
II guarantees you'll get infinitely many over an infinite horizon. This is why
multiple testing corrections (Benjamini–Hochberg FDR, Bonferroni FWER) exist: at
$k$ independent tests per day, the chance of at least one false positive per day
is $1-0.95^k$ (0.63 at $k=20$), not 5%. The number of tests, not just the
per-test threshold, determines the false-alarm rate.

---

## Q15 — Regret, which axioms do not capture
**Q.** Is the minimax regret in a game determined by the axioms?

**A.** Yes — but only because the game itself specifies payoffs; the axioms say
nothing about which distribution is *right*. The classic framing
(Savage's axioms): rationality + a dominance condition ⇒ unique finitely additive
probability up to finitely additive equivalence. This shows the axioms are not
"obvious truths about the world" but a chosen encoding of rationality, and that
the choice is consequential — risk-neutral utility axioms vs expected-utility
axioms select different measures when incompleteness is present.

---

*Self-check: Q1, Q2 and Q13 are all about the boundary between the axiom system
and intuition. Q6, Q9 and Q10 test the difference between the several distinct
notions of independence.*