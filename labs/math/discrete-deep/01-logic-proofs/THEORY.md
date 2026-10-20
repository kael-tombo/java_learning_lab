# Logic and Proofs — Theory

## 1. Propositions and Connectives, Precisely

A proposition is a sentence with a definite truth value in each context.
Connectives are truth functions: ¬p, p∧q (true iff both), p∨q (inclusive),
p→q defined as false exactly when p is true and q is false — so p→q equals
¬p∨q on all four valuations, a fact the truth-table engine confirms on
every row. Tautologies are formulas true at every valuation of their
variables; contradictions are false at every valuation; satisfiable
formulas are true at at least one. For n variables there are exactly 2ⁿ
valuations: 8 for three variables, 1024 for ten, 1048576 for twenty —
truth tables verify but do not scale.

## 2. Natural Deduction: Rules as the Only Moves

A natural-deduction system licenses steps and nothing more: modus ponens
(from p→q and p infer q), and-introduction/elimination, or-introduction,
¬-elimination, →-introduction under a temporary assumption (discharge),
and reductio. A proof of Γ ⊢ φ is a finite tree whose leaves are
Γ-members and whose nodes apply one rule. The lab's
central sequent — (p→q)∧(q→r) ⊢ p→r — is a tautology: true at all 8
valuations, with the hypotheses alone holding at exactly 4 of them.
The reverse chain (q→r)∧(p→q) ⊢ r→p is NOT derivable because it is not
valid: at p=false, q=false, r=true both hypotheses hold while r→p fails.
Validity is the ceiling on what deduction can produce.

## 3. Induction and Its Variants

Weak induction on the naturals: prove P(0); prove P(n) → P(n+1); conclude
P(n) for every n. Executionally, for S(n) = "sum of the first n odd
numbers equals n²": base S(0) holds with 0 = 0; the step is exact
identity n² + (2n+1) = (n+1)², verified for every n in 0..999 by the
run. Strong induction allows assuming P(k) for ALL k ≤ n — needed when
the step uses more than the immediate predecessor (Euclid's prime bounds,
every-n-factors decomposition). Structural induction is the same
procedure on recursively defined objects: a subtree has fewer nodes than
the tree, so descent terminates.

## 4. Contraposition vs Contradiction — Two Different Machines

Contraposition rewrites p→q as ¬q→¬p (run: holds at all rows). Use it to
prove an implication whose
conclusion is negative: instead of chasing "q", assume ¬q and derive ¬p.
Contradiction is different: to prove p, assume ¬p, derive absurdity ⊥, and
discharge by negation elimination. The engine shows why it is sound: ⊥
has 0 satisfying assignments, so (p∧¬p)→q is vacuously a tautology and
p→(¬p→q) holds at every row. Warning pairs: ¬¬p ⊢ p needs classical
logic (intuitionistically you may conclude ¬p is false but not p);
and (p→q) does NOT entail (¬p→¬q) — the run's agreement check printed
False, since converse-failure is the classic fallacy.

## 5. Soundness and Completeness, Sketch Form

Soundness: every derivable sequent is valid. Proof by induction on the
derivation: each rule preserves truth at every valuation (check modus
ponens once — p→q and p true force q true — and the same one-row argument
covers the rest). Completeness (Gödel 1930): every valid formula is
derivable; the constructive route runs through a Kalmár-style argument,
building from each truth assignment a conjunction onto which the target
formula is derivable, then eliminating fresh variables by excluded
middle. Consequence: compactness — every finite subset of Γ satisfiable
forces Γ satisfiable — since unsatisfiability would yield a finite
derivation of ⊥, contradicting soundness.

## 6. Decidability and Cost

Propositional validity is decidable by the 2ⁿ enumeration, but the cost
is exponential in variable count: 2¹⁰ = 1024 rows is easy, 2²⁰ = 1048576
is minutes, and real instances have hundreds of variables. SAT is the
canonical NP-complete problem. First-order
logic, by contrast, is semi-decidable: validities are enumerable but
non-validity admits no terminating procedure (Church–Turing). This is
the precise boundary crossed when proofs meet computation.

## 7. What the Lab Verifies in Code

Truth-table engine (lab program 1) settles valid/invalid by enumeration
and prints explicit counterexample valuations; program 2 exercises the
negation-of-implication equivalence ¬(p→q) ≡ p∧¬q (true on all 4 rows),
both contradiction templates, induction checked to n = 1000, and the
near-miss n²−n+41, which stays prime for n = 0..40 and first fails at
n = 41 — checking cases is not proving, shown as data.
