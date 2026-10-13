# Math Foundation: LCS Counting and Bounds
> States-times-transitions derivation of Theta(m*n) time and the rolling-row space cut.

## Definitions
- State (i, j): prefixes X[1..i], Y[1..j]; value dp[i][j] in 0..min(i, j).
- Transition: O(1) max of three neighbors or +1 diagonal step.
- Boundary: dp[0][*] = dp[*][0] = 0, no computation needed.
- Measure: primitive ops are integer compares and array reads.

## Counting argument
- State count: (m+1)(n+1) cells including boundaries.
- Transition cost: at most 3 reads + 1 compare + 1 write per interior cell.
- Total time: (m+1)(n+1) x O(1) = Theta(m*n).
- Space: full table Theta(m*n); length-only keeps 2 rows: Theta(min(m, n)).

## Recurrence
- dp[i][j] = dp[i-1][j-1] + 1 if X[i] == Y[j], else max(dp[i-1][j], dp[i][j-1]).
- Dependency depth: cell (i, j) needs row i-1 and current row up to j-1.
- Row-major fill respects all dependencies; diagonal-first would not.
- Reconstruction walk: at most m + n parent steps back to a boundary.

## Derivation of the bound
- Lower: any algorithm filling the table pays Omega(m*n) cell writes.
- Upper: the double loop performs exactly mn interior updates.
- Tight: Theta(m*n) for the table method on all inputs (no early exit in general).
- Rolling rows preserve time, cut space: same product, fewer rows stored.

## Worked mini-proofs
- Proof 1: boundary row/col correctness by definition of empty-prefix LCS (2 lines).
- Proof 2: equal-tail case adds exactly 1 via the swap-in argument (4 lines).
- Proof 3: rolling-row equivalence by induction on rows, keeping only previous row (5 lines).

## Exercises with answers
- 1. Count cells for m = 4, n = 7 including boundaries. Answer: 5 x 8 = 40.
- 2. LCS length of ABCBDAB and BDCABA. Answer: 4 (e.g., BCBA).
- 3. Space for length-only with m = 1000, n = 10 (oriented). Answer: 2 x 11 cells.

## Pitfalls
- Counting only mn and forgetting the boundary row/column in implementations.
- Claiming sublinear space while also promising reconstruction.
- Confusing LCS length with edit distance on the same table shape.

## Checklist
- Derive Theta(m*n) from states times transitions without notes.
- Explain the rolling-row cut and what functionality it sacrifices.
