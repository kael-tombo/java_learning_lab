# Mini Project: Chain Cost Calculator
> Optimal parenthesization cost plus the tree that achieves it.

## Background
- Cost table m over intervals plus split table s is the whole method.
- Intervals fill by increasing length; every split k is tried.
- The classic six-matrix fixture has known optimum 15125 - use it as oracle.
## Goal
Implement cost DP, split recording, and parenthesization printing.
Verify against the classic fixture and a brute-force check on 4 matrices.
## Tasks
1. Parse dimension lists and validate positivity and length.
2. Fill m by chain length 2..n with the min-over-k recurrence.
3. Record argmin splits and reconstruct the parenthesization string.
4. Assert cost 15125 on dims 30 35 15 5 10 20 25.
5. Brute-force all parenthesizations for a 4-matrix fixture and match the DP cost.
6. Print the split table for the 4-matrix case in the README.
## Acceptance criteria
- Classic fixture reports exactly 15125.
- Brute force and DP agree on three 4-matrix fixtures.
- Reconstructed parenthesization re-evaluates to the DP cost.
- Two-matrix input returns the single product with no split.
- Invalid dims are rejected with messages.
## Pitfalls
- Row-major fill order that reads unfilled subintervals.
- Dimension indexing off by one (p[i]*p[i+1] instead of the correct triple).
- Forgetting the split table and being unable to reconstruct.
- int overflow on large dims; costs must use long.
## Stretch
- Optimal binary-search-tree mode (same interval DP, new cost model).
- Polygon triangulation mode with weight function explained.
## Timebox
One evening session, roughly 2 to 3 hours with verification.
