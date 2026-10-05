# MINI_PROJECT — Discrete Math: Proof & Invariant Checker
> Implement + verify + tabulate. ~3 hours.

## Goal
Build a CLI that evaluates truth tables for given formulas, verifies induction steps
on small bases, and checks loop-invariant-style properties of toy algorithms.

## Build Steps
1. `TruthTable.java`: parse propositions with ∧ ∨ ¬ → ↔, print full table, flag tautology.
2. `Induction.java`: for a property `P(n)`, verify base + 16 inductive cases numerically.
3. `SetOps.java`: union/intersection/difference/subset checks with printed evidence.
4. `LoopChecks.java`: binary-search invariant `lo ≤ idx < hi` checked every iteration.
5. Driver: run the suite; emit PASS/FAIL report and a Markdown summary.

## Sample Output
```
(p∧q)→p: rows=4 tautology? true
sum_{i=1..n} i = n(n+1)/2: base ok, step ok for n≤64 ✓
binary search invariant held for all 1000 random runs
```

## Benchmark Table (fill)
| check | n | ms |
|-------|---|-----|
| truth table 4 vars | 16 rows | |
| induction numerics | 64 | |
| brute-force search check | 1000 runs | |

## Acceptance
- [ ] Tautology detection exact for ≤4 variables.
- [ ] Binary search fuzz produces zero invariant violations.
- [ ] Report marks verified vs unverified claims distinctly.

## Extensions
- Quine–McCluskey minimizer for boolean formulas.
- Property-based test harness feeding random formulas.
