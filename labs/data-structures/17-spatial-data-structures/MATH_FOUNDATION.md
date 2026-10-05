# Math Foundation: Spatial Data Structures (R-tree / QuadTree / k-d tree)

## Spatial-index math

- R-tree height with fanout m..M: h <= log_m(n) - 1; plug m=20, n=10^6.

- mindist(q, MBR) lower-bounds every point inside: the pruning correctness proof.

- Best-first kNN expands MBRs in mindist order; first complete point found is optimal.

- Quadtree depth degenerates on skewed points; compare uniform vs clustered insertion.

- Hilbert vs Z-order: average jump distance experiment on a 16x16 grid.

- Curse of dimensionality: overlap growth makes R-trees weak past ~10 dims; alternatives?

## Worked numbers (n = 8, then scale to 10^6)

1. Hot path `insert(point)`: count exact primitive steps on an 8-element instance.
2. Double to n = 16: which term grows, which stays flat? Name the dominant term.
3. Solve the governing recurrence and check it against the two data points.
4. Extrapolate: predict time and memory at n = 10^6 from a timing at n = 10^5.
5. State the input that breaks the prediction and the fix that restores it.

## Bounds table (prove each row on paper)

| Operation | Claimed bound | Proof sketch |
|---|---|---|
| `insert(point)` | O(log n) avg | place into leaf, split on overflow |
| `rangeQuery(rect)` | O(log n + m) | DFS pruning disjoint MBRs |
| `nearest(q)` | O(log n) avg | best-first with mindist bound |
| `kNN(q,k)` | O(k log n) avg | bounded priority queue search |
| `bulkLoad(points)` | O(n log n) | STR sort-tile-recursive |
| `delete(point)` | O(log n) | remove + condense underfull nodes |

## Amortized and probabilistic lens

- Potential method: pricey rebuilds (bulk load, rehash, resize) prepaid by cheap ops.
- Expectation over random choices (levels, hashes, pivots), not over inputs.
- Adversarial inputs break average-case claims; name the adversary for this structure.

## Constants that matter in Java

- Cache lines: node hops cost misses; blocked layouts (fanout, unrolled blocks) win.
- Branch prediction: linear scan beats binary search below ~64 elements.
- GC: node-per-element designs pressure the collector; arrays of primitives win.

## Paper exercises

E1. Derive the build cost from the level sum for n = 8, then generalize.
E2. Show the headline invariant implies the query bound.
E3. Memory math: entries x bytes/entry + auxiliary overhead at n = 10^6.
E4. Predict runtime at 10x scale from a measured timing; identify the dominant term.
E5. Give one input where the bound degrades and the mitigation that restores it.

## Derivation checklist

- [ ] Cost model written down (what counts as one step?)
- [ ] Recurrence or level-sum solved and checked at n = 8
- [ ] Dominant term identified at 10x scale
- [ ] Adversary named, with the mitigation that restores the bound

## Common wrong turns

- Quoting average-case bounds for adversarial inputs.
- Forgetting auxiliary memory (tables, registers, tags) in the space math.
- Mixing up one-time build cost with per-operation cost.
- Ignoring constant factors that dominate below n = 10^4 in Java.
