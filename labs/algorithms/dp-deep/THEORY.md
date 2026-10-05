# THEORY — DP Deep Track
> Mechanics + invariants + complexity proof. Track `dp-deep`.

## 1. Problem statement (5)
- Input, output, constraints stated formally per DP family.
- For this track: optimal substructure over prefixes/intervals/trees/digits.
- Context: the highest-yield interview + production optimization pattern.
- Success = correct output on all edge cases + proven bounds.

## 2. Intuition in one paragraph (8)
- DP exploits structure: optimal substructure plus overlapping subproblems.
- Think of it as maintaining a promise while scanning/building the answer.
- If the promise ever breaks, the algorithm has a repair step.
- Example domains: diff tools, resource allocation, sequence alignment.

## 3. Formal model (10)
- State: defines current partial solution.
- Decision: choice at each step derived from optimal substructure.
- Transition: how state evolves (see recurrence below).
- Objective: minimize/maximize cost or decide feasibility.
- Model instances: `dp[i][w]`, `dp[i][j] LCS prefixes`, `dp[len][l] intervals`, `dp[u][k] tree`.

## 4. Mechanics step-by-step (15)
1. Initialize structures (arrays, heaps, hash maps as needed).
2. Establish base case / empty-structure invariant.
3. Iterate / recurse over input in defined order.
4. Apply local rule (greedy choice, DP transition, pointer move).
5. Maintain auxiliary data (prefix sums, pi table, residual graph).
6. Prune / skip provably useless branches.
7. Record best answer seen so far.
8. Terminate when input exhausted or target reached.
9. Reconstruct solution via parent pointers if needed.
10. Validate output with checker.
11. Order states topologically (increasing i/j/len/subtree).
12. Compress dimensions when transition looks back fixed rows.
13. Apply Knuth/D&C when quadrangle inequality + monotonicity hold.
14. Digit DP: iterate pos with tight flag + memo (pos,tight,sum).
15. Tree DP: post-order combine children knapsacks.

## 5. Worked trace (12)
- Small input example: LCS("abcde","ace") table fill.
- Table-driven trace (step | state | decision | invariant holds?).
- Step 1: init — invariant holds vacuously.
- Step 2: first decision — show why alternatives are dominated.
- Step 3: middle — show auxiliary structure update.
- Step 4: last — show answer extraction.
- Key lesson: trace exposes off-by-one and order bugs early.
- Knapsack trace: W=5 weights {2,3,4} row evolution.
- LIS trace: tails array updates on [3,1,2,5,4].
- Interval trace: matrix-chain len=2..n splits.

## 6. Invariants (precise) (10)
- I1: dp[state] equals optimum over the processed prefix/subproblem.
- I2: Every discarded candidate cannot belong to an optimal solution.
- I3: Auxiliary structure always reflects processed prefix.
- I4: transition reads only already-finalized states (order invariant).
- I5: compressed rows preserve values needed by future transitions.
- Initialization: I holds before loop (empty prefix).
- Maintenance: each iteration re-establishes I (case split).
- Termination: I + exit condition => correctness.

## 7. Correctness proof sketch (10)
- Lemma 1 (safety): maintained invariant holds each iteration.
- Lemma 2 (progress): measure strictly decreases/increases toward goal.
- Theorem: on termination output is optimal/correct.
- Proof by induction on steps using I1–I5.
- Counterexample if invariant dropped: construct small failing input.
- Optimal substructure: optimal solution restricts to optimal subsolutions.
- Overlapping: memo hits reuse; DAG order guarantees single computation.

## 8. Complexity analysis with proof (12)
- Count primitive ops per step; sum over steps.
- Recurrence where applicable: T(n) = a·T(n/b) + f(n) (see MATH_FOUNDATION.md).
- Apply Master theorem / Akra-Bazzi / accounting method.
- Typical bounds: LCS O(mn); knapsack O(nW); LIS O(n log n); matrix-chain O(n³)/O(n²) Knuth; tree O(n·k²); digit O(pos·sum·10).
- Space: tables + compression (rolling rows) + recursion stack.
- Lower bound argument: comparison / information-theoretic where relevant.
- Tightness: exhibit worst-case family achieving the bound.

## 9. Variants and connections (8)
- Iterative vs recursive formulations.
- Top-down memo vs bottom-up tabulation.
- Randomized / parallel / streaming variants.
- Reduces to / from neighboring lab topics.
- When NOT to use: input too small, constraints violated, simpler method wins.

## 10. Common misconceptions (5)
- Confusing average with worst case.
- Forgetting reconstruction vs value-only DP.
- Off-by-one in indices / hash modulus.
- Assuming sorted input when it is not.
- Ignoring integer overflow in cost accumulation.

## 11. Interview signal (3)
- State invariant first, then code.
- Derive complexity without hand-waving.
- Name one pitfall and its test.

## 12. Checklist (2)
- [ ] Can replay trace without notes. [ ] Can prove bound. [ ] Can code in 20 min.
