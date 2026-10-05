# MATH_FOUNDATION — Trie (Prefix Tree)

Goal: derive the bounds, not just quote them. Work each sum with n=8 on paper.

## 1. Cost model
Count primitive steps: pointer hops, array probes, hash evaluations, register touches.
T(n) has best/average/worst; name which one each table entry claims.

## 2. Main recurrence / sum
Hot path `insert(word)` costs O(L). Derive it:
- Divide-and-conquer levels: T(n) = T(n/2) + O(1) => O(log n).
- Linear scan levels: sum over levels = O(n log n) build.
- Geometric tower/level probabilities: E[level] = 1/(1-p).
- Harmonic-mean estimators: variance ~ 1/sqrt(m) registers.

## 3. Worked mini-derivations (do all four)
1. n=8 walk: count exact steps of the hot path.
2. Double n to 16: which term dominates?
3. Solve T(n)=2T(n/2)+O(1) vs T(n)=T(n/2)+O(1).
4. Plug numbers: predict ms at n=10^6 from n=10^5 timing.

## 4. Amortized / probabilistic lens
- Potential method: expensive rebuilds prepaid by cheap ops (dynamic tables, rehash).
- Expectation: random levels/hashes make worst cases measure-zero.
- Concentration: median-of-runs tames single-run luck in benchmarks.
- Error budgets (sketches/hashes): FPR ~= (1-e^(-kn/m))^k; HLL std err ~= 1.04/sqrt(m).

## 5. Constants that matter in Java
- Indirection: references cost cache misses; blocks/arrays win.
- Hashing: 64-bit mixing quality decides sketch/hash accuracy.
- GC: node-per-element designs pressure the collector; prefer arrays.
- Branch prediction: sorted-linear vs binary search crossovers (~64 elems).

## 6. Exercises (paper)
E1. Derive the build cost from the level sum.
E2. Show the invariant implies the query bound.
E3. Compute memory: n entries * bytes/entry + overhead.
E4. For sketches: pick m for 2% error and justify.
E5. Explain why the bound breaks if one invariant is dropped.
