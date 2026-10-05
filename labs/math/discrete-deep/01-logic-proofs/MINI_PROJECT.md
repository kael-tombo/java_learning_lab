# MINI_PROJECT — Logic & Proofs: Truth-Table & Induction Checker
> Implement + tabulate + verify. ~2 hours.

## Goal
Build a CLI that evaluates propositional formulas, prints truth tables, checks
logical equivalence of two formulas, and validates an induction step numerically.

## Build Steps
1. `Parse.java`: tokens for ¬ ∧ ∨ → ↔ and variables.
2. `Eval.java`: evaluate over all assignments; print table.
3. `Equiv.java`: two formulas equivalent iff tables match.
4. `Induct.java`: check P(k)→P(k+1) numerically for k in [1..64].
5. Driver: 6 equivalences + 3 inductions; print PASS/FAIL.

## Acceptance
- [ ] Tautology/contradiction detection works on fixtures.
- [ ] Induction check catches a broken step.

## Extensions
- Minimal DNF of a formula.
