# Real-World Project: Queens Census
> Count N-queens solutions with pruning statistics and board printing.

## Problem
Exhaustive search must be instrumented: solutions found plus nodes visited.
Known solution counts give an exact oracle for correctness.
## Inputs
- Board size n (1 to 10) and a flag to print the first solution board.
- Expected counts for n = 1..8: 1, 0, 0, 2, 10, 4, 40, 92.
- Output: solution count, nodes visited, pruned rows, elapsed milliseconds.
## Steps
1. Place queens row by row with column/diagonal conflict tests.
2. Count a solution at row n; count a prune each time no column fits a row.
3. Record nodes visited (calls) and report the prune-to-node ratio.
4. Assert counts for n = 1..8 against the expected sequence before printing tables.
5. Print the first n = 8 solution as an ASCII board.
6. Refuse n above 10 with the factorial-growth reason in the message.
## Acceptance criteria
- Counts for n = 1..8 match 1, 0, 0, 2, 10, 4, 40, 92 exactly.
- n = 8 finishes in under 30 seconds on the lab machine.
- Printed n = 8 board verifies conflict-free under an independent checker.
- Node counts are deterministic across runs (fixed move order).
- n = 11 is refused with the growth reason, not attempted.
## Failure modes
- n = 0 and negative n are rejected at parse time.
- Boards print with row/column indices so solutions can be checked by eye.
- Timing excludes JVM warmup by averaging 3 runs (documented in output).
## Extensions
- Symmetry-reduced counting (first-row half + mirror doubling) as an extension.
- Sudoku filler reusing the choose-recurse-unchoose skeleton.
## How to demo
- Show the count table with node statistics for n = 1..8.
- Show the ASCII board of the first n = 8 solution.
