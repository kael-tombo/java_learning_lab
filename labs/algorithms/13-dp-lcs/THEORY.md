# Theory: Longest Common Subsequence
> Two-string DP over prefix pairs: recurrence, fill order, reconstruction, bounds.

## Problem statement
- Input: strings X of length m and Y of length n over the same alphabet.
- Output: the length of the longest sequence that is a subsequence of both, plus one such sequence.
- A subsequence keeps order but not contiguity; do not confuse it with substring.
- Boundary cases: either string empty gives length 0; identical strings give full length.

## Recurrence
- State dp[i][j] = LCS length of prefixes X[1..i] and Y[1..j], with dp[0][*] = dp[*][0] = 0.
- If X[i] == Y[j]: dp[i][j] = dp[i-1][j-1] + 1 (last characters pair up in some optimum).
- Else: dp[i][j] = max(dp[i-1][j], dp[i][j-1]) (drop one tail or the other).
- The answer is dp[m][n]; the recurrence references only already-filled neighbors.

## Worked trace
- X = ABC, Y = AC. Row 0 and column 0 are all zeros by definition.
- i=1 (A) vs j=1 (A): equal, dp = dp[0][0] + 1 = 1. j=2 (C): differ, max(0, 1) = 1.
- i=2 (B): vs A differ max(1, 0) = 1; vs C differ max(1, 1) = 1.
- i=3 (C): vs A differ max(1, 0) = 1; vs C equal, dp[2][1] + 1 = 2.
- Result 2 with subsequence AC; backtracking from dp[3][2] recovers it.

## Correctness argument
- Case X[i] == Y[j]: some optimal solution pairs them (else swap the partner in), so +1 is safe.
- Case differ: no optimal solution needs both tails, so dropping one tail keeps an optimum.
- Induction on i + j lifts the per-cell claim to the full table.
- Fill order (rows outer, columns inner) guarantees every referenced cell is final.

## Complexity derivation
- States: (m+1)(n+1) cells, each computed in O(1) from three neighbors.
- Time Theta(m*n); full table space Theta(m*n) when reconstruction is needed.
- Length-only needs one rolling row: space Theta(min(m, n)) by orienting the short string across.
- Reconstruction walks back at most m + n steps following parent decisions.

## Variants
- Edit distance (Levenshtein) on the same table with insert/delete/substitute costs.
- Length-only rolling rows vs full table with parent pointers: know which the task needs.
- Space-shrinking divide-and-conquer (Hirschberg) exists but is beyond this lab's scope.

## Pitfalls
- Off-by-one: dp indices run 0..m while string indices run 0..m-1; the +1 shift is mandatory.
- Reconstructing from a rolling-row table that no longer holds the parents.
- Treating ties (equal max from top vs left) as errors; any optimal parent is fine.
- Assuming the recovered LCS is unique; usually it is not.

## Interview signal
- Write the recurrence and defend the equal-character case in one sentence.
- State fill order and the rolling-row optimization with what is lost.
- Trace a 3x2 table cold without index mistakes.
