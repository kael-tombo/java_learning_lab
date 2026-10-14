# VISION — Sorting Track
> Direction: from "call sort()" to choosing the method from the distribution — and proving the choice with counts.

## Where this sits
- Comparison sorting bottoms out at Omega(n log n); quicksort (avg O(n log n), worst O(n^2)), mergesort (O(n log n), stable), heapsort (O(n log n), in-place) each buy something different.
- Special structure buys more: nearly-sorted favors insertion O(n), dupes favor 3-way, small k selection is quickselect avg O(n).
- Non-comparison methods (counting/radix O(n+w)) apply when keys are bounded integers.

## 4-week direction
- Week 1: hand-trace Hoare partition and the 3-way regions until the invariants are statable cold.
- Week 2: finish MINI_PROJECT; fill every results.csv cell from real runs.
- Week 3: break quicksort with an adversarial input, then fix it two ways (random pivot, 3-way) and measure both.
- Week 4: REAL_WORLD_PROJECT review; whiteboard the lower-bound argument in 5 minutes.

## Done criteria
- State each method's time/space/stability triple from memory.
- Predict the winner for a given (size, distribution, stability need) and verify by running.
- Derive Omega(n log n) via the decision-tree argument without notes.

## Non-coverage
- This track does not cover external sorting internals (used as a path, not built), parallel sorting networks, or string sorting (see 40-string-algorithms-advanced).
- Radix/counting sorts are specified with trigger conditions, not benchmarked here.
- No claim that one method wins everywhere; the suite exists because none does.

## Pitfalls
- Benchmarking only random input; sorted and dupe cases decide production behavior.
- Forgetting stability until tie order corrupts a downstream join.
- Quoting average bounds as guarantees on adversarial feeds.

## Adjacent tracks
- Pair with searching for the lookup side and sorting-searching-deep for selection and external construction.
- Revisit after any production sort incident; the distribution checklist is the postmortem template.

## Weekly drills
- State the 3-way regions and the Hoare invariant cold, then trace one partition by hand.
- Re-derive Omega(n log n) from the decision-tree count in under 5 minutes.
- Name the stability of all six methods plus quickselect without hesitation.

## Anti-roadmap
- Do not benchmark random input only; sorted, reverse, and dupe cases are mandatory columns.
- Do not adopt an unstable sort where tie order feeds a downstream join.
