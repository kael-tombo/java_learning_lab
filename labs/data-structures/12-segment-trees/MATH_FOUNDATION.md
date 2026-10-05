# Math Foundation: Segment Trees (incl. Lazy Propagation)

## Segment-tree math

- Build cost: level sums give T(n) = 2T(n/2) + O(1) => O(n) nodes (~4n array).

- Query visits at most 2 nodes per level => O(log n); prove by interval partition.

- Lazy composition: add/add composes by addition; assign overrides pending adds.

- Worked: n=8, query [2,6]: list the O(log n) visited nodes and their intervals.

- Memory: 4n array vs 2*2^ceil(log2 n) iterative layout; compare bytes at n=10^6.

- Non-commutative ops (matrix prod): order of merges matters; show a counterexample.

## Worked numbers (n = 8, then scale to 10^6)

1. Hot path `build(arr)`: count exact primitive steps on an 8-element instance.
2. Double to n = 16: which term grows, which stays flat? Name the dominant term.
3. Solve the governing recurrence and check it against the two data points.
4. Extrapolate: predict time and memory at n = 10^6 from a timing at n = 10^5.
5. State the input that breaks the prediction and the fix that restores it.

## Bounds table (prove each row on paper)

| Operation | Claimed bound | Proof sketch |
|---|---|---|
| `build(arr)` | O(n) | bottom-up or recursive build |
| `query(l,r)` | O(log n) | aggregate over interval |
| `pointUpdate(i,v)` | O(log n) | leaf update + recompute path |
| `rangeAdd(l,r,v)` | O(log n) | lazy-propagated add |
| `rangeAssign(l,r,v)` | O(log n) | lazy assignment with push |
| `push(node)` | O(1) | propagate lazy tag to children |

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
