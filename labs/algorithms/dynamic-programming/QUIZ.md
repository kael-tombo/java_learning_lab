# QUIZ — Dynamic Programming Track
> 15 questions with answers. Track `dynamic-programming`.

1. Two DP preconditions? → Optimal substructure + overlapping subproblems.
2. Memo key rule? → Include every parameter that varies across calls.
3. Memoized fib complexity? → O(n) time, O(n) space (table + stack).
4. Naive fib without memo? → Θ(φ^n) repeated subtrees.
5. Grid paths recurrence? → f(i,j) = f(i-1,j) + f(i,j-1) with obstacle = 0.
6. Coin min-coins base? → dp[0] = 0, rest INF; iterate amounts ascending.
7. Count-ways vs min-coins loop? → Ways: outer coins; min: order flexible.
8. Tabulation advantage? → No recursion depth; better locality.
9. Memo advantage? → Computes only reachable states.
10. Space compression needs? → Transition reads fixed lookback rows.
11. Bound formula? → #states × transition cost.
12. Why fuzz vs brute? → Catches missing memo dims + base bugs.
13. long vs int? → Counts/paths overflow int fast; use long/BigInteger.
14. Reconstruction needs? → Parent/move table or backtrack walk.
15. When NOT DP? → Greedy choice safe, or no overlap (plain recursion fine).

## Scoring
- 13-15: expert. 10-12: practitioner. < 10: revisit THEORY + flashcards.

## Follow-ups
- Prove one bound on paper; implement one variant from memory.
