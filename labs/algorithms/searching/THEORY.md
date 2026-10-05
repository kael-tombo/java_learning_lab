# THEORY — Searching Track
> Mechanics + invariants + complexity proof. Track `searching`.

## 1. Problem statement (5)
- Input, output, constraints stated formally.
- For this track: find key/peak/bound in arrays with order structure.
- Context: the most-interviewed loop invariant in the repo.
- Success = correct output on all edge cases + proven bounds.

## 2. Intuition in one paragraph (8)
- Searching exploits order: each probe discards a provable fraction.
- Think of it as maintaining a promise while scanning/building the answer.
- If the promise ever breaks, the algorithm has a repair step.
- Example domains: feature flags, version lookup, peak load detection.

## 3. Formal model (10)
- State: defines current partial solution.
- Decision: choice at each step derived from comparison at mid.
- Transition: how state evolves (see recurrence below).
- Objective: minimize/maximize cost or decide feasibility.
- Model instance: `a[lo..hi) candidates; answer in [lo,hi] or absent`.

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
11. Pick half-open [lo,hi) + mid=(lo+hi)>>>1 discipline.
12. Shrink lo or hi by comparison; never stall (mid strictly inside).
13. Rotated: one half is always sorted; test membership there.
14. Peak: move toward the higher neighbor (gradient invariant).
15. Answer-search: predicate monotonic; binary search the predicate.

## 5. Worked trace (12)
- Small input example: lowerBound([1,2,2,5], 2) step table.
- Table-driven trace (step | state | decision | invariant holds?).
- Step 1: init — invariant holds vacuously.
- Step 2: first decision — show why alternatives are dominated.
- Step 3: middle — show auxiliary structure update.
- Step 4: last — show answer extraction.
- Key lesson: trace exposes off-by-one and order bugs early.
- Rotated trace: [4,5,6,7,0,1,2] target 0.
- Peak trace: [1,3,2] moves.

## 6. Invariants (precise) (10)
- I1: if answer exists, it lies in [lo,hi).
- I2: every index outside [lo,hi) is provably not the answer.
- I3: interval strictly shrinks each iteration (progress).
- I4: predicate P false below lo, true from some point (answer-search).
- Initialization: I holds before loop (empty prefix).
- Maintenance: each iteration re-establishes I (case split).
- Termination: I + exit condition => correctness.

## 7. Correctness proof sketch (10)
- Lemma 1 (safety): maintained invariant holds each iteration.
- Lemma 2 (progress): measure strictly decreases/increases toward goal.
- Theorem: on termination output is optimal/correct.
- Proof by induction on steps using I1–I4.
- Counterexample if invariant dropped: construct small failing input.
- Termination: hi-lo reaches 0 or 1; lo is the bound.

## 8. Complexity analysis with proof (12)
- Count primitive ops per step; sum over steps.
- Recurrence where applicable: T(n) = a·T(n/b) + f(n) (see MATH_FOUNDATION.md).
- Apply Master theorem / Akra-Bazzi / accounting method.
- Typical bounds: binary O(log n); interpolation O(log log n) avg; exponential O(log pos).
- Recurrence: T(n) = T(n/2) + O(1) → Θ(log n) by Master case 2 (a=1,b=2).
- Space: O(1) iterative; O(log n) naive recursion.
- Lower bound argument: comparison / information-theoretic where relevant.
- Tightness: exhibit worst-case family achieving the bound.

## 9. Variants and connections (8)
- Iterative vs recursive formulations.
- lowerBound vs upperBound vs exact-hit wrappers.
- Randomized / parallel / streaming variants.
- Reduces to / from neighboring lab topics.
- When NOT to use: input too small, constraints violated, simpler method wins.

## 10. Common misconceptions (5)
- Confusing average with worst case.
- (lo+hi)/2 overflow in Java int.
- Off-by-one in indices / hash modulus.
- Assuming sorted input when it is not.
- Ignoring integer overflow in cost accumulation.

## 11. Interview signal (3)
- State invariant first, then code.
- Derive complexity without hand-waving.
- Name one pitfall and its test.

## 12. Checklist (2)
- [ ] Can replay trace without notes. [ ] Can prove bound. [ ] Can code in 20 min.
