# QUIZ — DP Deep Track
> 15 questions with answers. Track `dp-deep`.

1. Two DP preconditions? → Optimal substructure + overlapping subproblems.
2. Why backward loop in 0/1 knapsack? → Prevents reusing the same item twice.
3. Unbounded loop direction? → Forward (ascending) to allow reuse.
4. LCS recurrence? → match: dp[i-1][j-1]+1; else max(dp[i-1][j], dp[i][j-1]).
5. LCS time/space? → O(mn) time; O(min(m,n)) with rolling rows (value only).
6. LIS O(n log n) trick? → tails array + binary search replacement.
7. Kadane core? → cur = max(x, cur+x); track best; handles all-negative.
8. Matrix-chain naive? → O(n³) over lengths and splits.
9. Knuth condition? → Quadrangle inequality + monotonicity → O(n²).
10. D&C optimization needs? → opt[i][j] monotonic in j.
11. Tree DP order? → Post-order; children before parent; reroot second pass.
12. Digit DP states? → (pos, tight, sum/flag); memoize non-tight only.
13. Memo vs tabulation? → Memo pays recursion + sparse states; tabulation pays full table, better locality.
14. Reconstruction needs? → Parent/move table or backtrack walk.
15. CHT use-case? → DP with lines: dp[i] = min_j(m_j·x_i + b_j) in O(n log n)/O(n).

## Scoring
- 13-15: expert. 10-12: practitioner. < 10: revisit THEORY + flashcards.

## Follow-ups
- Prove one bound on paper; implement one variant from memory.
