# THEORY — Sliding Window Technique
> Mechanics + invariants + complexity proof. Lab `18-sliding-window`.

## 1. Problem statement (5)
- Input, output, constraints stated formally.
- For Sliding Window Technique: expand right, shrink left while invalid; freq map / deque.
- Context: variable / fixed windows with monotonic aggregates.
- Success = correct output on all edge cases + proven bounds.

## 2. Intuition in one paragraph (8)
- Sliding Window Technique exploits structure: window invariant: [l,r) is longest/shortest valid ending at r.
- Think of it as maintaining a promise while scanning/building the answer.
- If the promise ever breaks, the algorithm has a repair step.
- Example domain: rate limiting, longest-substring-k-distinct, min-subarray.

## 3. Formal model (10)
- State: defines current partial solution.
- Decision: choice at each step derived from variable / fixed windows with monotonic aggregates.
- Transition: how state evolves (see recurrence below).
- Objective: minimize/maximize cost or decide feasibility.
- Model instance: `expand right, shrink left while invalid; freq map / deque`.

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

## 5. Worked trace (12)
- Small input example tailored to Sliding Window Technique.
- Table-driven trace (step | state | decision | invariant holds?).
- Step 1: init — invariant holds vacuously.
- Step 2: first decision — show why alternatives are dominated.
- Step 3: middle — show auxiliary structure update.
- Step 4: last — show answer extraction.
- Key lesson: trace exposes off-by-one and order bugs early.

## 6. Invariants (precise) (10)
- I1: window invariant: [l,r) is longest/shortest valid ending at r.
- I2: Every discarded candidate cannot belong to an optimal solution.
- I3: Auxiliary structure always reflects processed prefix.
- Initialization: I holds before loop (empty prefix).
- Maintenance: each iteration re-establishes I (case split).
- Termination: I + exit condition => correctness.

## 7. Correctness proof sketch (10)
- Lemma 1 (safety): maintained invariant holds each iteration.
- Lemma 2 (progress): measure strictly decreases/increases toward goal.
- Theorem: on termination output is optimal/correct.
- Proof by induction on steps using I1–I3.
- Counterexample if invariant dropped: construct small failing input.

## 8. Complexity analysis with proof (12)
- Count primitive ops per step; sum over steps.
- Recurrence where applicable: T(n) = a·T(n/b) + f(n) (see MATH_FOUNDATION.md).
- Apply Master theorem / Akra-Bazzi / accounting method.
- Typical bound for this lab: O(n) each index visited <= twice; O(k) aux.
- Space: auxiliary tables + recursion stack + output.
- Lower bound argument: comparison / information-theoretic where relevant.
- Tightness: exhibit worst-case family achieving the bound.

## 9. Variants and connections (8)
- Iterative vs recursive formulations.
- Top-down memo vs bottom-up tabulation (for DP-flavored Sliding Window Technique).
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
