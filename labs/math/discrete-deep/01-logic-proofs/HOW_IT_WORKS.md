# How It Works: Logic and Proofs

## How Truth Tables Work

A truth table enumerates every possible assignment of truth values to the atomic propositions in a formula. For n atoms, there are 2^n assignments. Each row represents one possible "world." The formula's truth value in each world is computed by applying the connective definitions bottom-up:

1. Start with the atomic propositions (given by the row).
2. Evaluate the smallest subformulas (e.g., ¬P, P ∧ Q).
3. Use those results to evaluate larger subformulas.
4. The final column gives the formula's truth value in that world.

A formula is a **tautology** if the final column is all T; a **contradiction** if all F; **contingent** otherwise.

## How Natural Deduction Works

Natural deduction builds proofs using introduction and elimination rules for each connective:

- **∧-intro**: From P and Q, conclude P ∧ Q.
- **∧-elim**: From P ∧ Q, conclude P (or Q).
- **→-intro**: Assume P, derive Q, conclude P → Q (discharging the assumption).
- **→-elim (modus ponens)**: From P → Q and P, conclude Q.
- **¬-intro**: Assume P, derive a contradiction, conclude ¬P.
- **∀-intro**: Prove P(x) for arbitrary x, conclude ∀x P(x).
- **∃-intro**: From P(t) for some term t, conclude ∃x P(x).

Each rule is justified by the semantics of the connective. The system is sound (only valid formulas are provable) and complete (all valid formulas are provable).

## How Proof by Contradiction Works

To prove P:
1. Assume ¬P.
2. Derive a contradiction (Q ∧ ¬Q for some Q).
3. Conclude P.

This works because if ¬P leads to an impossible situation, ¬P cannot hold, so P must hold (by the law of excluded middle: P ∨ ¬P).

## How Mathematical Induction Works

To prove ∀n ∈ ℕ P(n):
1. **Base case**: Prove P(0) (or P(1), depending on the domain).
2. **Inductive step**: Assume P(k) for arbitrary k (inductive hypothesis), prove P(k+1).
3. **Conclusion**: By the induction principle, ∀n P(n).

The induction principle is an axiom of the natural numbers (Peano's fifth axiom). It captures the idea that the natural numbers are generated from 0 by repeatedly adding 1.

## How Resolution Works

Resolution is a refutation procedure:
1. Negate the statement to be proved.
2. Convert the negation to conjunctive normal form (CNF): a conjunction of clauses, where each clause is a disjunction of literals.
3. Repeatedly apply the resolution rule: from (A ∨ P) and (B ∨ ¬P), infer (A ∨ B).
4. If the empty clause (□) is derived, the original statement is a tautology.

Resolution is refutation-complete: if a set of clauses is unsatisfiable, resolution derives the empty clause. It is not complete for direct proof (you cannot derive arbitrary tautologies without negating them first).
