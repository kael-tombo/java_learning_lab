# THEORY — Sorting Track
> Mechanics + invariants + complexity proof. Track `sorting`.

## 1. Problem statement (5)
- Input, output, constraints stated formally.
- For this track: sort permutation + kth order statistic in place.
- Context: quicksort is the canonical divide-and-conquer interview lab.
- Success = correct output on all edge cases + proven bounds.

## 2. Intuition in one paragraph (8)
- Quicksort exploits partitions: one pivot placement splits the problem.
- Think of it as maintaining a promise while scanning/building the answer.
- If the promise ever breaks, the algorithm has a repair step.
- Example domains: log ordering, leaderboard ranking, data prep for binary search.

## 3. Formal model (10)
- State: defines current partial solution.
- Decision: choice at each step derived from pivot rank.
- Transition: how state evolves (see recurrence below).
- Objective: minimize/maximize cost or decide feasibility.
- Model instance: `a[lo..hi) unsorted; pivot ends at final rank p`.

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
11. Choose pivot (random/median-of-3); partition scanned region.
12. Hoare: two fingers converge; swap inversions; return split.
13. 3-way: maintain <, =, > regions for duplicate-heavy input.
14. Recurse smaller side first (stack bound O(log n)).
15. Quickselect: recurse only the side containing k.

## 5. Worked trace (12)
- Small input example: Hoare on [5,1,4,2,3] pivot 5.
- Table-driven trace (step | state | decision | invariant holds?).
- Step 1: init — invariant holds vacuously.
- Step 2: first decision — show why alternatives are dominated.
- Step 3: middle — show auxiliary structure update.
- Step 4: last — show answer extraction.
- Key lesson: trace exposes off-by-one and order bugs early.
- 3-way trace: [2,1,2,0,2] regions evolution.
- Quickselect trace: k=2 on 7 elements.

## 6. Invariants (precise) (10)
- I1: Hoare: left of i ≤ pivot ≤ right of j (crossing ⇒ done).
- I2: 3-way: [lo,lt)<p, [lt,i)==p, (gt,hi]>p, [i,gt] unscanned.
- I3: pivot lands at final sorted rank after partition.
- I4: recursion processes disjoint ranges covering all elements.
- Initialization: I holds before loop (empty prefix).
- Maintenance: each iteration re-establishes I (case split).
- Termination: I + exit condition => correctness.

## 7. Correctness proof sketch (10)
- Lemma 1 (safety): maintained invariant holds each iteration.
- Lemma 2 (progress): measure strictly decreases/increases toward goal.
- Theorem: on termination output is optimal/correct.
- Proof by induction on steps using I1–I4.
- Counterexample if invariant dropped: construct small failing input.
- Sortedness: pivot-rank induction over recursion tree.

## 8. Complexity analysis with proof (12)
- Count primitive ops per step; sum over steps.
- Recurrence where applicable: T(n) = a·T(n/b) + f(n) (see MATH_FOUNDATION.md).
- Apply Master theorem / Akra-Bazzi / accounting method.
- Typical bounds: avg O(n log n); worst O(n²); 3-way O(n) on equal keys; quickselect E[O(n)].
- Recurrence avg: T(n) = (1/n)Σ(T(k)+T(n-1-k)) + O(n) → Θ(n log n).
- Space: O(log n) stack (smaller-first); O(n) naive worst.
- Lower bound argument: comparison / information-theoretic where relevant.
- Tightness: exhibit worst-case family achieving the bound.

## 9. Variants and connections (8)
- Iterative vs recursive formulations.
- Lomuto vs Hoare vs 3-way; introsort fallback.
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
