# Math Foundation: Interval Counting and Cubic Cost
> Theta(n^2) intervals times O(n) splits gives Theta(n^3); Catalan-scale brute force avoided.

## Definitions
- State (i, j): optimal cost for matrices A_i..A_j, 1 <= i <= j <= n.
- Interval length L = j - i + 1; base L = 1 costs 0.
- Split k: last multiplication joins [i..k] and [k+1..j].
- Cost term p[i-1]*p[k]*p[j] prices the final join of the two halves.

## Counting argument
- Interval count: n(n+1)/2 = Theta(n^2) states including singletons.
- Splits per state of length L: L - 1 candidates, each O(1) to evaluate.
- Total sum over L of (n-L+1)(L-1) = Theta(n^3) by the cubic sum.
- Space: two Theta(n^2) tables (costs and splits).

## Recurrence
- m[i][j] = min over k of m[i][k] + m[k+1][j] + p[i-1]*p[k]*p[j].
- Dependencies are strictly shorter intervals: length order is a topological order.
- Row-major order violates dependencies; length order respects all of them.
- Reconstruction follows argmin splits: O(n) descent from [1][n].

## Derivation of the bound
- Sum_{L>=2} (n-L+1)(L-1): substitute t = L-1, sum t(n-t) ~ n^3/6.
- Hence Theta(n^3) time; halving the constant needs different algorithms, not tuning.
- Brute-force parenthesization count grows Catalan-class exponential: DP is exponentially better.
- Six-matrix classic: DP does hundreds of ops where enumeration does thousands of trees.

## Worked mini-proofs
- Proof 1: length order is topological (dependency lengths strictly smaller). (3 lines)
- Proof 2: cubic sum evaluation via t(n-t) summation. (5 lines)
- Proof 3: optimal substructure by cut-and-replace on the root split. (4 lines)

## Exercises with answers
- 1. Interval count for n = 6. Answer: 21.
- 2. Splits tried for interval length 4. Answer: 3.
- 3. Cost of ((A1 A2) A3) for dims 10 30 5 60. Answer: 1500 + 3000 = 4500.

## Pitfalls
- Summation starting at L = 1 (singletons need no split loop).
- Index triple shifted by one position in the join cost.
- Claiming O(n^2) by forgetting the split loop inside each state.

## Checklist
- Evaluate the cubic sum from states times splits without notes.
- Prove length order is a valid topological order.
