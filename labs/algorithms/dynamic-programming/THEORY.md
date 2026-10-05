# THEORY — Dynamic Programming Track
> Mechanics + invariants + complexity proof. Track `dynamic-programming`.

## 1. Problem statement (5)
- Input, output, constraints stated formally.
- For this track: optimization/counting over recursive structure with reuse.
- Context: entry point to the dp-deep track.
- Success = correct output on all edge cases + proven bounds.

## 2. Intuition in one paragraph (8)
- Dynamic programming exploits structure: optimal substructure plus overlapping subproblems.
- Think of it as maintaining a promise while scanning/building the answer.
- If the promise ever breaks, the algorithm has a repair step.
- Example domain: path counting, coin change, staircase climbs.

## 3. Formal model (10)
- State: defines current partial solution.
- Decision: choice at each step derived from recurrence.
- Transition: how state evolves (see recurrence below).
- Objective: minimize/maximize cost or decide feasibility.
- Model instance: `f(n)`, `f(i,j) grid`, `f(amount)` with memo key.

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
11. Write naive recursion first; memoize on exact state key.
12. Convert to bottom-up in topological order.
13. Compress dimensions when safe; keep parent info if reconstructing.
14. Guard recursion depth; switch to iterative for long chains.
15. Fuzz memo vs brute on tiny inputs.

## 5. Worked trace (12)
- Small input example: fib(5) call tree with memo hits.
- Table-driven trace (step | state | decision | invariant holds?).
- Step 1: init — invariant holds vacuously.
- Step 2: first decision — show why alternatives are dominated.
- Step 3: middle — show auxiliary structure update.
- Step 4: last — show answer extraction.
- Key lesson: trace exposes off-by-one and order bugs early.
- Grid trace: 3×3 paths dp[i][j] = dp[i-1][j]+dp[i][j-1].
- Coin trace: amount=5 coins {1,2,5} order choices.

## 6. Invariants (precise) (10)
- I1: memo[state] equals optimum/count once computed (never stale).
- I2: Every discarded candidate cannot belong to an optimal solution.
- I3: Auxiliary structure always reflects processed prefix.
- I4: recursion terminates: state measure strictly decreases.
- Initialization: I holds before loop (empty prefix).
- Maintenance: each iteration re-establishes I (case split).
- Termination: I + exit condition => correctness.

## 7. Correctness proof sketch (10)
- Lemma 1 (safety): maintained invariant holds each iteration.
- Lemma 2 (progress): measure strictly decreases/increases toward goal.
- Theorem: on termination output is optimal/correct.
- Proof by induction on steps using I1–I4.
- Counterexample if invariant dropped: construct small failing input.
- Memo correctness: each state computed once from finalized substates.

## 8. Complexity analysis with proof (12)
- Count primitive ops per step; sum over steps.
- Recurrence where applicable: T(n) = a·T(n/b) + f(n) (see MATH_FOUNDATION.md).
- Apply Master theorem / Akra-Bazzi / accounting method.
- Typical bounds: fib memo O(n); grid O(mn); coin O(n·amount).
- Bound rule: #states × transition cost + memo overhead.
- Space: memo table + recursion stack + output.
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
