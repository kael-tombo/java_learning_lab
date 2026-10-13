# Mini Project: Queens Counter
> N-queens counts against the known sequence with node statistics.

## Background
- Row-by-row placement with column/diagonal tests is the whole engine.
- Counts for n = 1..8 are known: 1, 0, 0, 2, 10, 4, 40, 92.
- Node counts separate a correct program from an efficient-enough one.
## Goal
Count solutions for n = 1..8, print boards, and report node stats.
Match the known sequence exactly before calling it done.
## Tasks
1. Implement placement with incremental conflict tests.
2. Count solutions and count visited nodes in the same run.
3. Assert the n = 1..8 sequence matches the known values.
4. Print the first n = 4 solution as an ASCII board.
5. Record per-n timings and node counts in a table.
6. Verify printed boards with an independent conflict checker.
## Acceptance criteria
- Sequence matches all 8 known values exactly.
- n = 8 finishes in under 30 seconds.
- Printed boards pass the independent checker.
- Node counts are deterministic across reruns.
- n above the cap is refused with the growth reason.
## Pitfalls
- Missing the undo (board state leaks between sibling branches).
- Diagonal test with wrong arithmetic that passes n = 4 but fails n = 5.
- Counting placements instead of completions (row-n check misplaced).
- Symmetry breaking attempted incorrectly, halving the true count.
## Stretch
- First-solution printer for n = 8 with full board output.
- Subset/permutation enumerators reusing the same skeleton.
## Timebox
One evening session, roughly 2 hours with verification.
