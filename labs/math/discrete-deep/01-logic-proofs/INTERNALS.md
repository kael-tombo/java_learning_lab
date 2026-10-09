# Internals: Logic and Proofs

## Propositional Logic

Propositional logic deals with atomic propositions (P, Q, R, ...) combined via connectives:

| Connective | Symbol | Meaning |
|-----------|--------|---------|
| Negation | ¬P | not P |
| Conjunction | P ∧ Q | P and Q |
| Disjunction | P ∨ Q | P or Q (inclusive) |
| Implication | P → Q | if P then Q |
| Biconditional | P ↔ Q | P if and only if Q |

**Truth tables** define each connective by enumerating all 2^n assignments of truth values to n atomic propositions. A formula is a **tautology** if it is true under all assignments, a **contradiction** if false under all, and **contingent** otherwise.

## Predicate Logic (First-Order Logic)

Predicate logic extends propositional logic with:
- **Variables** (x, y, z) ranging over a domain of discourse
- **Predicates** (P(x), Q(x,y)) expressing properties and relations
- **Quantifiers**: ∀x (for all x) and ∃x (there exists x)

The semantics of quantifiers depends on the domain. Over the natural numbers, ∀x ∃y (y > x) is true; over a finite domain {1, 2, 3}, it is false.

## Proof Systems

### Natural Deduction
Uses introduction and elimination rules for each connective. For example:
- **∧-introduction**: From P and Q, infer P ∧ Q.
- **→-elimination (modus ponens)**: From P → Q and P, infer Q.
- **∀-elimination**: From ∀x P(x), infer P(t) for any term t.

### Hilbert Systems
Use axioms and modus ponens. For example, one axiom schema: P → (Q → P). Hilbert systems are compact but proofs are unintuitive.

### Resolution
Used in automated theorem proving. Convert formulas to conjunctive normal form (CNF), then apply the resolution rule: from (P ∨ Q) and (¬P ∨ R), infer (Q ∨ R). Resolution is refutation-complete: if the CNF of ¬φ is unsatisfiable, resolution derives the empty clause.

## The Deduction Theorem

In Hilbert-style systems, if Γ ∪ {P} ⊢ Q, then Γ ⊢ P → Q. This meta-theorem connects syntactic provability with the semantic notion of implication and justifies the "assume P, prove Q" strategy in natural deduction.

## Soundness and Completeness

- **Soundness**: Every provable formula is valid (true in all models). If ⊢ φ, then ⊨ φ.
- **Completeness** (Gödel, 1929): Every valid formula is provable. If ⊨ φ, then ⊢ φ.

These theorems establish that syntactic proof and semantic truth coincide in first-order logic.
