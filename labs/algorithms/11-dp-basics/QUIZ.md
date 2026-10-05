# QUIZ — DP Basics (15Q + Answers)
> Complexity, invariants, counter-examples. Answers at end.

## Questions
1. Fib naive recurrence: (A) T(n)=T(n-1)+O(1) (B) T(n)=T(n-1)+T(n-2)+O(1) (C) T(n)=2T(n/2) (D) T(n)=T(n/2)+O(1)
2. Naive fib complexity: (A) O(n) (B) O(n log n) (C) exponential ~φⁿ (D) O(log n)
3. Memo invariant: stored entries are ___. (A) estimates (B) final answers (C) random (D) empty
4. Tab invariant after `i`: all `dp[j≤i]` are ___. (A) final (B) stale (C) unknown (D) maximal
5. `ways(0)` (climbing) = ___? (A) 0 (B) 1 (C) 2 (D) undefined
6. Space optimized Fib: (A) O(n) (B) O(1) (C) O(log n) (D) O(2ⁿ)
7. Counter-example: wrong base `ways(0)=0` causes ___. (A) nothing (B) off-by-one everywhere (C) speedup (D) stack safety
8. Memo vs tab asymptotic: (A) same O(n) (B) memo O(2ⁿ) (C) tab O(log n) (D) unrelated
9. State DAG order for Fib: (A) decreasing (B) increasing i (C) random (D) reverse only
10. `ways(n)` equals: (A) fib(n) (B) fib(n+1) (C) n! (D) 2ⁿ
11. True/False: DP helps when subproblems don't overlap.
12. True/False: recursion depth n risks StackOverflowError for large n.
13. `fib(47)` in int: (A) fine (B) overflows (C) negative-proof (D) zero
14. Which is top-down? (A) tabulation (B) memo DFS (C) greedy (D) BFS
15. Fast doubling Fib is: (A) O(n) (B) O(log n) (C) O(2ⁿ) (D) O(n²)

## Answers
1-B. 2-C. 3-B. 4-A. 5-B (empty way). 6-B (two vars).
7-B. 8-A. 9-B. 10-B. 11-False (no overlap → no gain).
12-True. 13-B (use long/mod). 14-B. 15-B.
- Scoring: 26–30 mastery; 20–25 review bases; <20 redo E1 table.

## Follow-ups
- Prove memo O(n) via state counting. Show mod-insertion preserves recurrence.
