# Real-World Project: Sorted Ledger Tools
> Dedup and pair-sum on sorted integer ledgers with operation budgets.

## Problem
Daily sorted exports contain duplicate transaction ids that must collapse in place.
Auditors also need all pairs summing to a control total, found in one pass.
## Inputs
- ledger.csv: sorted integers, one per line, up to 1M rows.
- Control total T for the pair-sum query.
- Fixtures: heavy duplicates, no duplicates, empty file, single row.
## Steps
1. Dedup in place with read/write pointers; report unique count and prefix.
2. Pair-sum with inward-moving pointers; collect all disjoint qualifying pairs.
3. Count element visits in both routines and assert visits are at most 2n.
4. Verify dedup output is sorted, unique, and a subsequence of the input.
5. Verify each reported pair sums to T and pairs are disjoint.
6. Print counts, visits, and the visit budget check (visits <= 2n).
## Acceptance criteria
- Heavy-duplicate fixture collapses to the exact expected unique list.
- Pair-sum fixture finds all expected pairs with no false positives.
- Empty and single-row inputs return empty results without errors.
- Visit counters stay within 2n on every fixture including 1M rows.
- Unsorted input is detected (first inversion reported) and rejected.
## Failure modes
- Unsorted input never proceeds; the inversion index is part of the error.
- Integer overflow in pair sums uses long accumulation with a documented cap.
- Pairs sharing an element are resolved by the disjoint rule, documented and tested.
## Extensions
- Dutch-flag partition mode for three-valued status columns.
- Three-sum counting mode with the sorted two-loop structure.
## How to demo
- Show the visit-budget line on the 1M-row file.
- Show the inversion error on a deliberately shuffled fixture.
