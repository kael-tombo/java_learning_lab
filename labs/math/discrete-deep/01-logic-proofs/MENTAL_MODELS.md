# Mental Models: Logic and Proofs

## 1. Logic as a Game with Rules

Think of a proof as a game where you start with given facts (premises) and apply allowed moves (inference rules) to reach a conclusion. Each move must be justified by an inference rule — like in chess, you cannot make arbitrary moves. The goal is to reach the target proposition using only legal moves.

## 2. Truth Tables as Lookup Tables

A truth table is a complete lookup table for a logical formula. For n variables, there are 2^n rows—each row is one possible "world." The formula's value in each world is determined by the connective definitions. To check if P → Q is a tautology, scan the table: if any row has P true and Q false, the implication fails in that world.

## 3. Proofs as Chains of Implications

A direct proof of "If P then Q" is a chain: P → R₁ → R₂ → ... → Q. Each link is a valid inference. If any link breaks, the chain fails. This is why proving intermediate lemmas is powerful: they are reusable links.

## 4. Quantifiers as Loops

Think of ∀x P(x) as a loop that checks P(x) for every x in the domain. ∃x P(x) is a loop that stops at the first x satisfying P(x). The order of nested quantifiers determines which loop is outer: ∀x ∃y R(x,y) means "for each x, we can find a (possibly different) y," while ∃y ∀x R(x,y) means "there is a single y that works for all x."

## 5. Proof by Contradiction as a Detour

To prove P, assume ¬P and derive a contradiction (Q ∧ ¬Q). This shows that ¬P leads to an impossible situation, so P must be true. It is a detour: you temporarily assume the opposite of what you want, show it is untenable, and conclude the original claim.

## 6. Induction as a Row of Dominoes

Mathematical induction is like a row of dominoes: the base case knocks over the first domino, and the inductive step ensures that if domino k falls, domino k+1 falls too. Together, all dominoes fall. Without the base case, nothing starts; without the inductive step, the chain breaks.
