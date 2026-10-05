# MATH_FOUNDATION — Topological Sort
> Recurrences, Master theorem, amortized analysis for DAG linearization.

## 1. Recurrences (tailored)
- Kahn: `T(V,E)=Θ(V+E)` — indegree pass `Θ(V+E)` + each vertex/edge once. No divide split.
- DFS-topo: same `Θ(V+E)` + `O(1)` prepend per finish.
- Counting orders DP: `O(V·2^V)` over subsets (exact counting, exponential).
- Longest path on DAG: `Θ(V+E)` (topo + relax) — linear DP.
- Lexicographic PQ-Kahn: `Θ((V+E) log V)` (PQ factor).

## 2. Master Theorem (scope)
- Linear graph scans don't fit `aT(n/b)+f`; recognize non-applicability.
- Applies to helpers: merge-sorting labels, segment-tree over DAG queries.
- PQ-Kahn `T(n)=T(n-1)+O(log n)` unrolls to `Θ(n log n)` (summation, not Master).
- Contrast example `2T(n/2)+n → n log n` to show pattern matching.
- Interview point: saying "Master gives O(V+E)" is a red flag — correct it.

## 3. DAG Counting Proofs
- DAG ⟺ has source: remove source inductively (existence + termination).
- Kahn completeness: source always available → never stalls on DAG.
- Orders count: `1` (total order) to `V!` (empty edges); DP over subsets for exact.
- Uniqueness ⟺ Hamiltonian path in DAG (edge between consecutive pair).

## 4. Amortized Analysis
- Each edge decrements indegree exactly once → aggregate `O(E)` (charge to edge).
- Each vertex enqueued/dequeued once → `O(V)`; total `O(V+E)` aggregate, no per-op log (FIFO).
- Potential `Φ` = remaining edges + unemitted vertices; each step drops `Φ` ≥1.
- PQ variant: `log` per vertex unavoidable (ordering constraint costs).

## 5. Probabilistic Notes
- Random DAG (`i<j` edges p): expected sources `≈1/(p)`-ish; Kahn queue rarely empty.
- Random tie-break among sources → uniform-ish over orders (not exactly; note bias).

## 6. Worked Numbers
- `V=10⁵,E=10⁶`: Kahn ~1.1M ops; PQ variant ~1.7M heap steps.
- Counting DP feasible only `V≤20` (`V·2^V` wall).
- Semester batches = BFS depth (longest path length).

## 7. Exercises
- [ ] Prove source lemma + Kahn completeness.
- [ ] Aggregate `O(V+E)` via edge charging.
- [ ] Unroll PQ-Kahn sum to `(V+E) log V`.
- [ ] Count orders on diamond (expect 2 or 3 by edges).
