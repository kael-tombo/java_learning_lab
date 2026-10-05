# THEORY — Advanced Algorithms Deep Track
> Mechanics + invariants + complexity proof. Track `advanced-algo-deep`.

## 1. Problem statement (5)
- Input, output, constraints stated formally per sub-lab.
- For this track: 8 advanced domains sharing proof templates (invariants, recurrences, ratios).
- Context: exact, parallel, randomized, and approximate algorithm design.
- Success = correct output on all edge cases + proven bounds.

## 2. Intuition in one paragraph (8)
- Advanced algorithms exploit structure: bit subsets, modular witnesses, automaton states, geometric order, work/span decomposition, random choices, LP gaps.
- Think of it as maintaining a promise while scanning/building the answer.
- If the promise ever breaks, the algorithm has a repair step.
- Example domains: crypto keygen, GIS mapping, CDN routing, scheduling.

## 3. Formal model (10)
- State: defines current partial solution.
- Decision: choice at each step derived from domain structure.
- Transition: how state evolves (see recurrences below).
- Objective: minimize/maximize cost or decide feasibility.
- Model instances: `mask[0..2^n)`, `a^d mod n witnesses`, `goto/fail links`, `work W + span S`, `ratio ALG/OPT`.

## 4. Mechanics step-by-step (15)
1. Initialize structures (bitsets, tables, hulls, thread pools).
2. Establish base case / empty-structure invariant.
3. Iterate / recurse over input in defined order.
4. Apply local rule (greedy choice, DP transition, pointer move).
5. Maintain auxiliary data (prefix sums, pi table, residual graph).
6. Prune / skip provably useless branches.
7. Record best answer seen so far.
8. Terminate when input exhausted or target reached.
9. Reconstruct solution via parent pointers if needed.
10. Validate output with checker.
11. Parallel: fork subproblems, join with span-optimal depth.
12. Randomized: seed, repeat to drive error below delta.
13. Approximation: compare against LP/dual lower bound.
14. Geometry: sweep event order + balanced BST status.
15. Number theory: reduce mod phi, lift via CRT.

## 5. Worked trace (12)
- Small input example: bit DP over n=3 sets; Miller-Rabin on n=91.
- Table-driven trace (step | state | decision | invariant holds?).
- Step 1: init — invariant holds vacuously.
- Step 2: first decision — show why alternatives are dominated.
- Step 3: middle — show auxiliary structure update.
- Step 4: last — show answer extraction.
- Key lesson: trace exposes off-by-one and order bugs early.
- Geometry trace: 5 points hull insertion order.
- Parallel trace: prefix-sum up/down sweep on 8 elements.
- Randomized trace: Karger contraction on 4-node graph.
- Approximation trace: set-cover greedy picks vs OPT.

## 6. Invariants (precise) (10)
- I1: bitmask enumerates each subset exactly once.
- I2: composite n always has a Miller-Rabin witness in tested bases.
- I3: automaton state equals longest suffix-match after each char.
- I4: hull stack stays left-turn only (CCW invariant).
- I5: parallel prefix phases preserve prefix sums at every level.
- Initialization: I holds before loop (empty prefix).
- Maintenance: each iteration re-establishes I (case split).
- Termination: I + exit condition => correctness.

## 7. Correctness proof sketch (10)
- Lemma 1 (safety): maintained invariant holds each iteration.
- Lemma 2 (progress): measure strictly decreases/increases toward goal.
- Theorem: on termination output is optimal/correct (or ratio-bounded).
- Proof by induction on steps using I1–I5.
- Counterexample if invariant dropped: construct small failing input.
- Randomized: error bound via union bound over repetitions.
- Approximation: charging argument against OPT/dual feasible value.
- Parallel: Brent scheduling gives Tp <= W/P + S.

## 8. Complexity analysis with proof (12)
- Count primitive ops per step; sum over steps.
- Recurrence where applicable: T(n) = a·T(n/b) + f(n) (see MATH_FOUNDATION.md).
- Apply Master theorem / Akra-Bazzi / accounting method.
- Typical bounds: bit DP O(n·2^n); Miller-Rabin O(k log³ n); Aho-Corasick O(n+m+z); hull O(n log n); Karger O(n² log n); set-cover H(d).
- Space: auxiliary tables + recursion stack + output.
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
