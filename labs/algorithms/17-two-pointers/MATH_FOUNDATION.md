# Math Foundation: 2n Visit Bound and Discard Proofs
> Aggregate-method linearity, sorted two-sum discard counting, cycle-phase distances.

## Definitions
- Visit: one pointer landing on one index; budget 2n across both pointers.
- Discard: a step permanently eliminating an index from consideration.
- Invariant examples: sortedness bounds, unique-prefix property, region partition.
- Cycle parameters: mu (tail length), lambda (cycle length) for runner analysis.

## Counting argument
- Each pointer moves monotonically over n positions: at most n visits each.
- Aggregate total <= 2n regardless of interleaving: Theta(n) time.
- Per-step work O(1) in all four patterns: total linear with O(1) space.
- Sorting prerequisite (two-sum) adds O(n log n) when input is unsorted.

## Recurrence
- No recursion needed: loops with monotone measures (remaining indices, unknown region).
- Dutch flag: unknown-region size strictly decreases each step.
- Dedup: read pointer advances each step; write advances only on novelty.
- Cycle phase 1: relative speed 1 guarantees meeting within lambda steps.

## Derivation of the bound
- Aggregate method: charge each loop iteration to a pointer advance; advances <= 2n.
- Two-sum discard: each comparison eliminates lo or hi permanently: <= n compares.
- Cycle start: phase-2 meeting follows from mu-offset modular arithmetic (standard).
- One-pass claims verified by visit counters, not by loop-nesting appearance.

## Worked mini-proofs
- Proof 1: 2n aggregate bound from monotone pointer domains. (3 lines)
- Proof 2: two-sum discard safety (moved value cannot pair with the remainder). (4 lines)
- Proof 3: three-region invariant maintenance per symbol case. (4 lines)

## Exercises with answers
- 1. Max comparisons for sorted two-sum on n = 7. Answer: 6 (one discard per compare).
- 2. Dedup writes for [1,1,2,2,2,3]. Answer: 3 unique, write pointer ends at index 2.
- 3. Why must pointers move monotonically? Answer: backward moves break the charging.

## Pitfalls
- Nested-loop appearance mistaken for quadratic cost.
- Discard argument skipped: moving pointers without proving safety.
- Cycle math applied to acyclic lists (phase 1 never meets; handle null).

## Checklist
- Prove the 2n bound by the aggregate method cold.
- Prove one discard step for sorted two-sum.
