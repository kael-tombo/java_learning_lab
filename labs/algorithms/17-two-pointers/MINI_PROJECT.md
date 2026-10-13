# Mini Project: Pair Finder
> Sorted two-sum plus in-place dedup with visit budgets.

## Background
- Inward pointers solve sorted two-sum in linear time from the sortedness invariant.
- Read/write pointers dedup in place with one pass.
- Visit counters prove linearity instead of asserting it.
## Goal
Implement both routines with counters and verify on fixtures.
Show visits bounded by 2n on a 100k sorted input.
## Tasks
1. Implement sorted two-sum returning all disjoint pairs for target T.
2. Implement in-place dedup returning the unique prefix length.
3. Instrument element visits in both and assert visits at most 2n.
4. Test duplicates, negatives, empty, and single-element fixtures.
5. Verify pairs sum to T and dedup output is sorted and unique.
6. Run the 100k input and record visits vs the 2n budget.
## Acceptance criteria
- Pair fixture finds all expected pairs with none false.
- Dedup fixture matches the expected unique prefix exactly.
- All edge fixtures pass without index errors.
- 100k run respects the 2n visit budget with the numbers printed.
- Unsorted input is rejected with the inversion index.
## Pitfalls
- Running pointers on unsorted input and trusting the result.
- Double-counting pairs by moving only one pointer after a hit.
- Write pointer overtaking the read pointer in dedup variants.
- Forgetting disjointness rules, letting pairs share elements silently.
## Stretch
- Dutch-flag partition as a third pointer pattern.
- Closest-pair-to-target variant with the same scan shape.
## Timebox
One afternoon session, roughly 2 hours with budgets.
