# QUIZ — Backtracking Search
> 15 questions. Answers included. Lab `19-backtracking`.

## Q1. What problem does Backtracking Search solve and what are its inputs/outputs?
- Answer: Computes optimal/feasible answer for choose-explore-unchoose; constraint propagation; see THEORY §1.

## Q2. State the key invariant in one sentence.
- Answer: partial assignment never violates constraints (pruned otherwise).

## Q3. What is the headline time/space bound?
- Answer: worst O(b^d); pruning + memo can collapse to DP.

## Q4. When is the naive bound tight? Give a worst-case family.
- Answer: Adversarial sorted/reverse or crafted collisions forcing full work.

## Q5. Name one auxiliary structure and what it stores.
- Answer: Depends: DP table / pi array / heap / residual graph / freq map stores processed-prefix summary.

## Q6. What breaks if input order assumption is violated?
- Answer: Invariant collapses; fix by sorting or re-deriving order.

## Q7. Give one edge case and expected behavior.
- Answer: Empty/singleton: return sentinel or trivial solution; null: throw IAE.

## Q8. How do you reconstruct the full solution, not just its value?
- Answer: Parent/choice pointers saved at each transition, then backtrack.

## Q9. Top-down vs bottom-up: which avoids recursion depth issues?
- Answer: Bottom-up tabulation; top-down risks stack overflow.

## Q10. How does overflow/mod show up here?
- Answer: Accumulated costs overflow int; use long/BigInteger or mod arithmetic.

## Q11. Name a variant and its tradeoff.
- Answer: Randomized/parallel/streaming trades determinism/space for speed.

## Q12. How would you test against a brute-force oracle?
- Answer: Fuzz small n (n<=10), compare to exponential brute force, 200+ seeds.

## Q13. What production system uses this and why?
- Answer: See REAL_WORLD_PROJECT; e.g., N-queens, Sudoku, permutations, subsets.

## Q14. What is a common off-by-one trap?
- Answer: Inclusive vs exclusive window bounds; border/failure link indexing.

## Q15. In one line, when NOT to use this technique?
- Answer: When n is tiny, constraints break the invariant, or simpler linear scan suffices.

## Scoring
- 13–15: mastery; 10–12: review THEORY §§6–8; <10: redo EXERCISES E1–E3.
