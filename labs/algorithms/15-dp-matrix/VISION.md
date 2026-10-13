# Vision: Matrix Chain Multiplication
> Interval DP: optimal parenthesization through recurrence over split points.

## Where this leads
- Optimal binary-tree-over-interval structure used by parsers and triangulations.
- The O(n^3) interval-DP template: length-increasing fill order plus split loop.
- Cost-model thinking: counting scalar multiplications instead of waving at complexity.
## What mastering it unlocks
- Write m[i][j] = min over k of m[i][k] + m[k+1][j] + p[i-1]*p[k]*p[j] with correct indices.
- Explain why intervals must be filled by increasing length, not by row order.
- Reconstruct the optimal parenthesization with a split table.
- Count the cost of a given parenthesization by hand on 4 matrices.
- Derive O(n^3) time and O(n^2) space from the state count and split loop.
## What it does not cover
- Faster matrix multiplication algorithms (Strassen-style sub-cubic methods).
- Numerical linear algebra: stability, pivoting, and floating-point behavior.
- General context-free grammar parsing beyond the interval-DP connection.
## Core questions you will answer
- Why does the split have to range over every k between i and j-1?
- What goes wrong if the table is filled row by row instead of by chain length?
- How does the split table turn a cost table into a parenthesization?
- Why is the scalar-multiplication count the right cost model here?
## How to judge progress
- Fill the 4-matrix table by hand with correct indices throughout.
- Reconstruct parenthesizations from split tables on two different fixtures.
- Derive the cubic bound from states times splits without prompting.
## Common misuse
- Indexing dimensions p[i]*p[i+1] style, which shifts every product by one.
- Memoizing without the length order and recursing into unfilled states.
## After this lab
- 13-dp-lcs for DP over two prefixes before DP over intervals.
- 33-matrix-algorithms for the operational side of matrix computation.
One-line self-test: Write the matrix-chain recurrence with exact indices and base case.
