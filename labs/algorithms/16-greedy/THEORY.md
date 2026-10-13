# Theory: Greedy Choice and Exchange Arguments
> When local optima compose into global optima - activity selection, fractions, Huffman.

## Problem statement
- Greedy builds a solution by repeated locally-best choices, never revisiting.
- It works only with two properties: greedy-choice (a safe first pick exists) and optimal substructure.
- This lab covers three canonical wins plus the counterexample that bounds the method.

## Activity selection
- Input: activities with start/finish; output: largest compatible subset.
- Rule: sort by finish time, keep each activity starting at or after the last kept end.
- Exchange: some optimum can swap its first activity for the earliest-finishing one without harm.
- Remainder is the same problem on later activities: induction completes the proof.

## Fractional knapsack
- Items divisible; take highest value-density first, fraction of the last as needed.
- Swap proof: replacing lower-density content with higher-density content never loses value.
- Indivisibility breaks it: 0/1 knapsack needs DP, shown by small counterexamples.
- Sorting dominates: O(n log n) time, O(1) extra space.

## Huffman coding
- Repeatedly merge the two lightest weights; merged weight returns to the pool.
- Prefix-free codes from merge order; frequent symbols get short codes.
- Optimality via exchange on the two lightest symbols plus induction on the merge.
- Priority queue implementation: O(n log n) for n symbols.

## Correctness pattern
- Name the greedy-choice property: which first pick is provably safe and why.
- Name the optimal substructure: how the remainder is a smaller instance.
- Exchange arguments convert an arbitrary optimum into one using the greedy pick.
- Counterexample duty: every greedy claim ships with the instance shape that would break it.

## Complexity derivation
- Activity selection: sort O(n log n) plus linear scan; space O(1) extra.
- Fractional knapsack: same sort-dominated bound.
- Huffman: n merges times O(log n) queue ops = O(n log n).
- Canonical coin change: O(coins) after the divisibility structure is established.

## Variants
- Canonical coins {25,10,5,1}: greedy optimal by divisibility; {1,3,4} at total 6 needs DP (2 beats 3).
- Interval partitioning (minimum rooms) as the companion greedy with a different rule.
- Scheduling with deadlines and profits as the next-step greedy with union-find.

## Pitfalls
- Sorting by start time or raw value and asserting optimality without proof.
- Believing coin greedy works for every denomination set.
- Skipping tie-breaking rules, making outputs nondeterministic.
- Confusing greedy with DP when the choice needs future information.

## Interview signal
- Deliver the activity-selection exchange in three clean steps.
- Break coin greedy with {1,3,4} at total 6 on demand.
- State both greedy properties for each algorithm covered.
