# Real-World Project: Parenthesization Optimizer
> Optimal matrix-chain parenthesization with cost proof against naive left association.

## Problem
Matrix products with mismatched dimensions make parenthesization choice worth real multiplications.
The tool computes the optimal cost, shows the parenthesization, and prices the naive alternative.
## Inputs
- Dimension list p of length n+1 for n matrices (n up to 12).
- Fixture: the classic six-matrix dims 30 35 15 5 10 20 25 with known optimum 15125.
- Output: optimal cost, parenthesization string, and left-assoc cost for comparison.
## Steps
1. Validate dims (positive integers, at least 2 entries).
2. Fill cost table m by increasing chain length with the split recurrence.
3. Record the argmin split per interval in a split table.
4. Reconstruct the parenthesization string from the split table.
5. Compute the left-associated cost directly for the savings report.
6. Print optimal cost, parenthesization, naive cost, and multiplications saved.
## Acceptance criteria
- Classic fixture reports optimal cost exactly 15125 with a valid parenthesization.
- Reconstructed parenthesization re-evaluates to the reported optimal cost.
- Two-matrix input reports the single product with no split needed.
- Left-assoc cost on the classic fixture exceeds optimum by the expected margin.
- Invalid dims (zero, negative, single entry) are rejected with messages.
## Failure modes
- Integer overflow in cost products is guarded (costs use long with a documented cap).
- Ties in splits pick the lowest k deterministically so output is reproducible.
- Inputs over 12 matrices warn about cubic growth before computing.
## Extensions
- ASCII tree rendering of the optimal parenthesization.
- Polygon-triangulation mode showing the same interval DP on a second problem.
## How to demo
- Show the split table for a 4-matrix fixture and read the answer off it.
- Show the savings line: naive cost vs optimal cost on the classic fixture.
