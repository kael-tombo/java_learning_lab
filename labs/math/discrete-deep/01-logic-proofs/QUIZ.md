# Logic and Proofs — Quiz (15 Questions with Worked Answers)

Propositional and predicate logic, proof techniques, and the difference between
a valid argument and a true conclusion. Several questions hinge on quantifier
order or on a hidden assumption.

---

## Q1 — Valid argument vs true conclusion
**Q.** Is the following argument *valid*? If so, is its conclusion necessarily true?

All cats are mammals. Some mammals are not cats. Therefore some cats are not mammals.

**A.** Valid? No. Validity concerns form only: is the conclusion forced by the
premises? Model it with $C(x)$ = "cats are mammals", $M(x)$ = "mammal",
$N(x)$ = "not cat". Let $\forall x\,C(x)\to M(x)$ be true, and let some
$m$ satisfy $M(m)\land\neg C(m)$ (a whale). Set $C$ empty. All premises true,
conclusion $\exists x\,C(x)\land\neg M(x)$ false. So the argument is **invalid
and unsound**. The practical lesson: in modelling work, "all A are B" plus "some
B are not A" is consistent (it merely says not every mammal is a cat), but it
tells you nothing about whether any non-mammal is a cat.

---

## Q2 — Order of quantifiers changes everything
**Q.** Formally negate: "Everyone loves at least one person."

**A.** Original: $\forall x\,\exists y\,L(x,y)$. Negation:
$\exists x\,\forall y\,\neg L(x,y)$ — *some* person loves *nobody*. The
mechanics: $\neg\forall=\exists$, $\neg\exists=\forall$, and the quantifier
order reverses. Compare "there is somebody everyone loves": $\exists x\,\forall
y\,L(x,y)$. Same words, different meaning; a domain with 3 people makes the
difference obvious. These two formulas are not equivalent on any domain of size
$\ge2$, which is precisely why the reversal rule exists.

---

## Q3 — Negating an implication
**Q.** Negate "$P\Rightarrow Q$". Is "$Q\Rightarrow P$" the negation?

**A.** $\neg(P\to Q)=P\land\neg Q$. The converse $Q\to P$ is **not** the
negation: it is compatible with both $P\to Q$ being true and false. Give
$P=$ "it rains", $Q=$ "I carry an umbrella": the converse ("if I carry an
umbrella, it rains") holds on some days and not others, independently of the
original. Converse and contrapositive are equivalent; converse and inverse
are equivalent; original and converse are not.

---

## Q4 — Disproof by counterexample
**Q.** Claim: "If $n^2$ is even then $n$ is even" for all integers $n$. True?

**A.** True, and it needs induction over $|n|$ or a mod-2 argument:
$n^2$ even ⇒ $n^2\equiv0\pmod2$; the only square residue mod 2 is 0 or 1, so
$n\equiv0$ ⇒ $n$ even. Now the claim "If $n^2$ is odd then $n$ is odd" —
true by the same route. And "If $n^2$ is even then $n$ is odd" is refuted by
$n=2$: one counterexample kills a universal claim. Counterexample search is the
cheapest refutation tool and the first thing to try.

---

## Q5 — Proofs of irrationality
**Q.** Prove $\sqrt2$ is irrational.

**A.** Assume $\sqrt2=p/q$ in lowest terms. Then $p^2=2q^2$, so $p$ is even,
$p=2k$, giving $4k^2=2q^2$ and $q^2=2k^2$ so $q$ is even. Both $p$ and $q$
even contradicts lowest terms. The structural point: proofs of irrationality of
$\sqrt{n}$ work exactly when $n$ is not a perfect square, because the
contradiction depends on the exponent of $2$ (or any prime $p$) in $n$ being
odd. If $n$ is a perfect square the statement is trivially false.

---

## Q6 — Induction: the hypothesis is not optional
**Q.** Prove by strong induction that every $n\ge2$ is divisible by a prime.

**A.** Base $n=2$. Step: suppose every $k$ with $2\le k\le n$ has a prime
divisor. If $n$ is prime, done. If composite, $n=ab$ with $2\le a,b\le n-1$,
and by the strong hypothesis $a$ has a prime divisor, which divides $ab=n$.
The pitfall: the induction **hypothesis must be assumed**, not proven — a
"proof" that goes $n=ab$, "by induction $a$ has a prime factor" without having
assumed anything is circular. Ordinary induction can't be used here directly
since $a$ may be less than $n-1$; that is exactly what strong induction buys.

---

## Q7 — Converse, inverse, contrapositive — a truth table
**Q.** Which of the four forms of "$P\to Q$" are logically equivalent?

**A.** Only $P\to Q$ and its contrapositive $\neg Q\to\neg P$ are equivalent;
likewise $\neg P\to\neg Q$ (inverse) and $Q\to P$ (converse). A truth table
over $P,Q$ confirms: rows $(T,T),(T,F),(F,T),(F,F)$ give implications all true,
true, true, true (original), true, false, false, true (contrapositive) — same
rows. Converse: true, true, true, false. Inverse: true, false, false, true.
So two equivalence classes of size two, and "taking the contrapositive" is the
only free move.

---

## Q8 — Biconditional and exclusive or
**Q.** Is "$P\leftrightarrow Q$" the same as "exactly one of $P,Q$"?

**A.** No. $P\leftrightarrow Q$ is $\neg(P\oplus Q)$: it is true when both have
the same truth value. "Exactly one" is $P\oplus Q=\neg P\land Q\lor P\land\neg Q$.
They are negations. When translating English, "if and only if", "exactly when",
"precisely if" all denote the biconditional, while "either ... or" (when
exclusive) denotes XOR. Ambiguous English "or" is a real source of specification
bugs — e.g. validation rules read as exclusive when the implementer assumed
inclusive.

---

## Q9 — Modus ponens vs affirming the consequent
**Q.** A database column has a NOT NULL constraint, and you observe a value that
is NULL. Conclude the constraint failed?

**A.** Only via modus tollens, which is valid: from $A\to B$ and $\neg B$
conclude $\neg A$. From "column has constraint" and "value is NULL" we get
"no constraint" — legitimate. What would be invalid: constraint present + value
present ⇒ constraint "works". Affirming the consequent ($A\to B$, $B$ true,
conclude $A$) is the common error in alerting logic: an alert firing does not
prove the intended cause, only that some cause occurred.

---

## Q10 — Quantifiers over infinite domains: Dirichlet
**Q.** Is there an injection $\mathbb{N}\to\mathbb{Q}$?

**A.** Yes: $n\mapsto\frac{n}{n+1}$ lands in $\mathbb{Q}$ and is injective. And a
bijection $\mathbb{Q}\to\mathbb{N}$ also exists (enumerate by reduced
$fraction$, height $a+b$, then by $a$). The punchline for modelling: countable
sets can have very different structures but the *same* cardinality, so "there
are as many rationals as naturals" is true yet $\mathbb{Q}$ lacks a
least-positive-element ordering — density and well-ordering differ. In
practice, $\mathbb{Q}$ is countable while $\mathbb{R}$ is not, which is what
makes "the probability of a real number being rational" $0$.

---

## Q11 — Proving a biconditional by splitting
**Q.** Prove "the sequence $a_n=n^2+n+41$ is prime for $n=0,\dots,39$ and not
prime at $n=40$."

**A.** The prime claims for $n\le39$ require 40 individual checks — no shortcut
— but $n=40$ gives $40^2+40+41=40^2+81=1600+81=1681=41^2$, and $41^2$ is
composite. The structural lesson: a statement can be true on a long finite
stretch and then fail, so "it works for all our test data" is weak evidence.
(This polynomial is Euler's, discovered by mistranslating $\frac{n^2+n+41}{2}$.)

---

## Q12 — Soundness, completeness, and which one you need
**Q.** A sound proof system may still fail to prove true statements. What is
that called, and does it matter here?

**A.** Incompleteness (Gödel, for sufficiently rich systems; practically, for
decidability-limited problems like Presburger arithmetic). What matters for
this lab: soundness is non-negotiable — an unsound system "proves" false
statements, which destroys every downstream use. Completeness is often
impossible or prohibitively expensive, so practitioners accept incomplete
systems plus a "trust me / verified by kernel" escape hatch (Coq, Lean, Isabelle
kernels are small and trusted; SMT solvers are usually incomplete in
completeness but sound).

---

## Q13 — Modus ponens for forward chaining
**Q.** Facts: $P(a)$, $P(b)$, $P(c)$, $P(d)$, $Q(a)$. Rules:
$P(x)\to R(x)$, $R(x)\land Q(x)\to S(x)$. What closes?

**A.** Forward chaining: $R(a),R(b),R(c),R(d)$ from the first rule, then
$S(a)$ from the second ($R(a)\land Q(a)$). Closure is $\{P(a),P(b),P(c),P(d),Q(a),
R(a),R(b),R(c),R(d),S(a)\}$. No other $S$ fires since $Q$ holds only for $a$.
Note the directionality: forward chaining is complete for definite clauses but
may be infinite for recursive rules; backward chaining (query-directed) is
complete for Horn clauses but can loop on cycles. This is the semantic core of
production-rule engines and Prolog.

---

## Q14 — Quantifier traps in specifications
**Q.** "Every user who has read a report can also download it" — what does it
license, and what does it not?

**A.** $\forall u((\exists r\,\text{Read}(u,r))\to\exists d\,\text{Download}(u,d))$.
It licenses nothing about *which* $d$, does not license the converse, and does
not assert any user actually read a report. A buggy implementation typically
enforces the converse (a download implies a read) — a different formula. The
habit to build: write the formula before writing the code, then check the code
against the formula, not against the prose.

---

## Q15 — Countermodels and why "all my test cases pass" is weak
**Q.** You check 100 cases and find no counterexample to "$f$ is injective". Can
you conclude?

**A.** Only heuristically. Model checking helps: for small finite domains you
can *exhaustively* enumerate all $f\colon A\to A$ and all inputs — e.g. for
$|A|=3$, $3^3=27$ functions — and verify injectivity by machine. That converts
a sample into a proof for that domain size. The generalization still needs
argument. This is the same shape of argument as randomized property testing in
codebases: strong evidence, not proof.

---

*Self-check: Q1, Q7 and Q9 are all "the conclusion is true but the reasoning
doesn't get you there" cases. Q3 is its negation.*