# Vision: Backtracking
> Systematic search with undo: decision trees, constraints, and pruning.

## Where this leads
- N-queens, Sudoku-style constraint filling, subsets, permutations, combination sums.
- Constraint propagation habits: test early, fail fast, undo cleanly.
- Branch and bound foundations: bounds are just smarter prune tests.
## What mastering it unlocks
- Structure any exhaustive search as choose, recurse, unchoose.
- Enforce N-queens constraints incrementally with column/diagonal tests.
- Count visited nodes to quantify what pruning actually saved.
- Avoid duplicate work with ordering rules (start index, skip lists).
- Estimate the raw tree size (n!, 2^n) before claiming an optimization matters.
## What it does not cover
- Heuristic search (A-star, beam search) and stochastic local search.
- SAT/CDCL solving and propagation engines in full depth.
- Dynamic programming over subsets (Held-Karp style) except as contrast.
## Core questions you will answer
- What exactly is undone at each backtrack step, and what may persist?
- Why does the diagonal test use absolute differences?
- How does a start-index parameter prevent duplicate combinations?
- When does pruning change the worst case, and when only the constant?
## How to judge progress
- Write choose-recurse-unchoose for a new combinatorial object without a template.
- Instrument node counts and report pruning savings as numbers.
- Predict tree size class (factorial, exponential, Catalan-ish) up front.
## Common misuse
- Forgetting the undo step and watching state leak across siblings.
- Pruning with an unsound test that silently drops valid solutions.
## After this lab
- 11-branch-and-bound for bounds-driven pruning of the same trees.
- 10-backtracking for the companion lab with overlapping drills.
One-line self-test: Explain the undo step and why siblings would corrupt each other without it.
