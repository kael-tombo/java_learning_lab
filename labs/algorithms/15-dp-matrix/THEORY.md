# Theory: Matrix Chain Multiplication
> Interval DP over split points: optimal parenthesization with cubic cost.

## Problem statement
- Input: dimensions p[0..n] for matrices A_i of size p[i-1] x p[i], i = 1..n.
- Output: minimum scalar multiplications to compute the product, plus a parenthesization.
- Multiplying p x q by q x r costs p*q*r scalars; associativity lets us choose the order.
- Edge cases: n = 1 costs 0; n = 2 is the single product.

## Recurrence
- m[i][j] = minimum cost for A_i..A_j, with m[i][i] = 0.
- m[i][j] = min over k in [i, j-1] of m[i][k] + m[k+1][j] + p[i-1]*p[k]*p[j].
- The last multiplication combines the two halves at some split k; trying all k covers every tree.
- s[i][j] = argmin k records the split for reconstruction.

## Fill order
- m[i][j] depends on strictly shorter intervals, so fill by chain length 2..n.
- Row-major fill is wrong: it reads m entries from longer, unfilled intervals.
- Proof: every referenced subinterval has length less than j-i+1, hence already final.
- Reconstruction follows s from [1][n] down to singletons.

## Worked trace
- Dims 10 30 5 60 (3 matrices). m[1][2] = 10*30*5 = 1500; m[2][3] = 30*5*60 = 9000.
- m[1][3]: k=1 gives 0 + 9000 + 10*30*60 = 27000; k=2 gives 1500 + 0 + 10*5*60 = 4500.
- Optimum 4500 with split at 2: ((A1 A2) A3). Naive left assoc here equals it; larger chains differ.
- Classic six-matrix dims 30 35 15 5 10 20 25 give optimum 15125.

## Correctness argument
- Optimal substructure: an optimal tree's halves are optimal for their intervals (cut and replace).
- The split loop tries every possible root split, so the true root is considered.
- Induction on interval length lifts cell correctness to the full chain.
- Split table determinism (lowest k on ties) keeps reconstruction reproducible.

## Complexity derivation
- States: Theta(n^2) intervals; transitions per state: up to O(n) splits at O(1) each.
- Time Theta(n^3), space Theta(n^2) for both tables.
- Reconstruction walks O(n) splits after the tables are built.
- Brute-force parenthesization count is Catalan-class exponential - hence DP matters.

## Variants
- Left-assoc or right-assoc cost as the naive baseline for savings reports.
- Optimal binary search trees: same interval shape, different cost model.
- Polygon triangulation: same split structure over vertex ranges.

## Pitfalls
- Dimension triple p[i-1]*p[k]*p[j] written with shifted indices.
- Filling by rows instead of by chain length.
- Building costs without the split table, then unable to reconstruct.
- int overflow in products; costs belong in long.

## Interview signal
- Write the recurrence with exact indices and the base case.
- Prove length-order fill from the subinterval-length argument.
- Derive Theta(n^3) from states times splits.
