# THEORY — Sorting & Searching Deep Track
> Mechanics + invariants + complexity proof. Track `sorting-searching-deep`.

## 1. Problem statement (5)
- Input, output, constraints stated formally per sort/search family.
- For this track: order arrays + locate keys/patterns/statistics.
- Context: the combined foundation of data prep + lookup.
- Success = correct output on all edge cases + proven bounds.

## 2. Intuition in one paragraph (8)
- Sorting creates order; searching exploits it; selection and string matchers extend both.
- Think of it as maintaining a promise while scanning/building the answer.
- If the promise ever breaks, the algorithm has a repair step.
- Example domains: analytics pipelines, log grep, leaderboards, autocomplete.

## 3. Formal model (10)
- State: defines current partial solution.
- Decision: choice at each step derived from comparisons/hashes/automata.
- Transition: how state evolves (see recurrence below).
- Objective: minimize/maximize cost or decide feasibility.
- Model instances: `partition ranks`; `[lo,hi) bounds`; `pi/fail links`; `tournament winners`.

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
11. Sort: partition/merge/heapify per family discipline.
12. Search: shrink [lo,hi) by comparison or gradient.
13. Select: discard side not containing k.
14. String: simulate automaton / rolling hash with verification.
15. Linear sorts: count keys, prefix, scatter stably.

## 5. Worked trace (12)
- Small input example: quicksort partition + lowerBound on result.
- Table-driven trace (step | state | decision | invariant holds?).
- Step 1: init — invariant holds vacuously.
- Step 2: first decision — show why alternatives are dominated.
- Step 3: middle — show auxiliary structure update.
- Step 4: last — show answer extraction.
- Key lesson: trace exposes off-by-one and order bugs early.
- Heap trace: heapify [4,10,3,5,1].
- KMP trace: pi for "aaba" then scan.
- Radix trace: LSD passes on 2-digit keys.

## 6. Invariants (precise) (10)
- I1: partition regions correctly classified around pivot.
- I2: search answer (if any) stays inside [lo,hi).
- I3: heap array satisfies order after every public op.
- I4: automaton state equals longest match suffix.
- I5: counting prefix gives exact output positions (stability).
- Initialization: I holds before loop (empty prefix).
- Maintenance: each iteration re-establishes I (case split).
- Termination: I + exit condition => correctness.

## 7. Correctness proof sketch (10)
- Lemma 1 (safety): maintained invariant holds each iteration.
- Lemma 2 (progress): measure strictly decreases/increases toward goal.
- Theorem: on termination output is optimal/correct.
- Proof by induction on steps using I1–I5.
- Counterexample if invariant dropped: construct small failing input.
- String matchers: no-match shifts skip only impossible alignments.

## 8. Complexity analysis with proof (12)
- Count primitive ops per step; sum over steps.
- Recurrence where applicable: T(n) = a·T(n/b) + f(n) (see MATH_FOUNDATION.md).
- Apply Master theorem / Akra-Bazzi / accounting method.
- Typical bounds: quick E[n log n]; merge/heap Θ(n log n); counting O(n+k); radix O(d(n+k)); binary O(log n); KMP/Aho O(n+m+z); quickselect E[O(n)].
- Space: in-place vs auxiliary tables.
- Lower bound argument: comparison / information-theoretic where relevant.
- Tightness: exhibit worst-case family achieving the bound.

## 9. Variants and connections (8)
- Iterative vs recursive formulations.
- TimSort/introsort hybrids; dual-pivot; 3-way string QS.
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
