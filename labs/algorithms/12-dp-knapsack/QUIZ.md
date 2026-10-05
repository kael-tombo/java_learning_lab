# QUIZ — 0/1 Knapsack (15Q + Answers)
> Complexity, invariants, counter-examples. Answers at end.

## Questions
1. 0/1 recurrence: (A) max(skip,take-once) (B) greedy ratio (C) min edge (D) sort only
2. 1-D loop direction (0/1): (A) ascending (B) descending (C) either (D) random
3. Ascending 1-D actually solves: (A) 0/1 (B) unbounded (C) fractional (D) none
4. Complexity 0/1 DP: (A) O(n log n) (B) O(nW) pseudo-poly (C) O(2ⁿ) only (D) O(log W)
5. Space 1-D: (A) O(nW) (B) O(W) (C) O(1) (D) O(n²)
6. Reconstruction needs: (A) 1-D only (B) full table / take flags (C) nothing (D) sort
7. Counter-example: greedy-by-ratio fails on ___. (A) fractional (B) 0/1 crafted instance (C) sorted input (D) W=0
8. `wᵢ=0,vᵢ>0` policy: (A) skip (B) always take (C) crash (D) halve
9. Invariant 2-D `dp[i][w]` = optimum over ___. (A) all items (B) first i items (C) one item (D) infinite
10. 1-D invariant relies on: (A) not-yet-overwritten `dp[w-wᵢ]` (B) sorting (C) PQ (D) hashing
11. True/False: O(nW) is polynomial in input size.
12. True/False: fractional knapsack greedy is optimal.
13. `W=0` answer always: (A) 0 (+zero-weight edge) (B) max v (C) undefined (D) W
14. NP-hard ⟹: (A) no poly-in-n+logW known (B) trivial (C) O(n) exists (D) greedy works
15. Items (2,3),(3,4),(4,5) W=5 best = ___. (A) 5 (B) 7 (C) 8 (D) 9

## Answers
1-A. 2-B. 3-B. 4-B. 5-B. 6-B. 7-B. 8-B.
9-B. 10-A. 11-False (pseudo; exponential in log W). 12-True.
13-A. 14-A. 15-B (items 1+2).
- Scoring: 26–30 mastery; 20–25 review direction bug; <20 redo E2 demo.

## Follow-ups
- Write the ascending-bug input/output. Prove two-case recurrence exhaustive.
