# Code Deep Dive: SparseTableMin.java

The sparse table implementation uses 2D arrays. The constructor precomputes all levels using dynamic programming. The query method uses the precomputed log table for O(1) index calculation.

## Key Implementation Details

1. Precompute log values for O(1) lookup
2. Build DP table: st[i][j] = min(st[i][j-1], st[i + 2^(j-1)][j-1])
3. Query: k = log[r-l+1], return min(st[l][k], st[r - 2^k + 1][k])
4. Handle edge cases (empty array, single element)
