# Internals of Sparse Tables

## Memory Layout

Sparse table is a 2D array: st[n][k+1] where k = log2(n).
- Row-major: st[i][j]
- Column-major: st[j][i] (better cache for some access patterns)

## Log Table

Precompute log values for O(1) lookup:
`
log[0] = 0
log[1] = 0
for i = 2..n: log[i] = log[i/2] + 1
`

## Disjoint Sparse Table

For non-idempotent operations:
- Partition each block into prefix and suffix at the midpoint
- Query uses the highest level where l and r are in different blocks
- Returns prefix[l] + suffix[r] at that level
