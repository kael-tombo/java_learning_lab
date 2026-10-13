# Theory: Backtracking Search and Pruning
> Choose-recurse-unchoose over decision trees with sound prune tests.

## Problem statement
- Enumerate combinatorial objects (subsets, permutations, placements) subject to constraints.
- State: partial solution plus the undo stack; moves extend, recursion explores, undo retracts.
- Pruning abandons subtrees provably free of solutions; unsound pruning loses answers.
- Tree size (2^n, n!, Catalan-class) sets the budget before any optimization claim.

## Skeleton
- choose: apply one decision to the shared state (take element, place queen, fix digit).
- recurse: solve the smaller instance with updated constraints.
- unchoose: revert exactly the choose step so siblings see clean state.
- Base case records or counts; constraint test fires before recursing, not after.

## N-queens model
- Place one queen per row; track used columns and both diagonal families.
- Conflict test for (r, c): column used, or |c - c'| == r - r' for any placed row r'.
- Dead row (no column fits) backtracks; row n reached counts one solution.
- Counts n = 1..8: 1, 0, 0, 2, 10, 4, 40, 92 - the built-in correctness oracle.

## Counting arguments
- Subsets of n: 2^n leaves (take/skip per element); enumeration costs Omega(2^n) inherently.
- Permutations of n: n! leaves; swap-to-front with swap-back visits each exactly once.
- N-queens raw space n^n pruned to factorial-class by the one-per-row-and-column structure.
- Node counters separate search shape (fixed) from prune savings (measured).

## Pruning soundness
- A prune test may cut a subtree only if no completion inside can be valid.
- Forward checks (column/diagonal occupancy) are sound because they test necessary conditions.
- Bound-based cuts (branch and bound) need optimistic estimates - see the companion lab.
- Test soundness by asserting pruned runs return the same counts as unpruned runs.

## Complexity derivation
- Time is proportional to visited nodes times O(1)-ish per-node work: worst case stays exponential.
- Space is the recursion depth plus shared state: O(n) for queens, subsets, permutations.
- Pruning improves constants and sometimes effective branching, not the complexity class.
- Symmetry arguments (first-row halving) divide counts but need mirror-correctness proof.

## Variants
- Combination sum with start-index ordering to prevent duplicate sets.
- Sudoku-style filling with row/column/box constraint propagation.
- Branch and bound: same trees with bound-driven cuts (lab 11).

## Pitfalls
- Forgetting the undo so state leaks across sibling branches.
- Pruning on sufficient-but-unnecessary conditions, dropping valid solutions.
- Counting placements instead of completions (base case at the wrong depth).
- Duplicate enumeration from unordered choices without a canonical order rule.

## Interview signal
- Explain what exactly is undone per step and what corruption follows without it.
- Derive the diagonal test from row/column differences.
- Quote tree-size class before discussing any optimization.
