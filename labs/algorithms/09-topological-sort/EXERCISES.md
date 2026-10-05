# EXERCISES — Topological Sort
> Implement + trace + edge cases. Java templates included.

## Level 1 — Mechanics (do first)
### E1 Kahn from scratch (20 min)
```java
public static List<Integer> topoKahn(int n, List<List<Integer>> adj) {
    // TODO: indeg array; queue indeg==0; emit; decrement; return order (may be partial)
    return null;
}
```
- Trace: `n=4, edges 0→1,0→2,1→3,2→3`. Show indeg + queue per step.
- Assert: every edge `u→v` has `pos[u]<pos[v]`.

### E2 DFS postorder (20 min)
```java
public static List<Integer> topoDfs(int n, List<List<Integer>> adj) {
    // TODO: colors 0/1/2; on finish prepend; detect back edge -> return null (cycle)
    return null;
}
```
- Trace same graph; show finish order + reversed result.

### E3 Cycle verdict (15 min)
- Input cyclic `0→1→2→0`. Expect: Kahn `size< n`, DFS `null`/flag.
- Return leftover nodes (Kahn) for diagnostics.

## Level 2 — Edge Cases (15 min each)
### E4 Empty / singleton / disconnected
- `n=0` → `[]`; `n=1` → `[0]`; two components ordered arbitrarily but valid.

### E5 Self-loop + parallel edges
- `u→u` is a cycle (order impossible). Parallel edges must not double-decrement below zero — guard or count multiset.

### E6 Lexicographic order
- Use `PriorityQueue` Kahn; on `0→2,1→2` expect `[0,1,2]`. Document tie-break.

## Level 3 — Trace Table (fill + verify)
| Step | Queue/Stack | Emitted | indeg remaining |
|------|-------------|---------|-----------------|
| 0 | [0] | [] | [0,1,1,2] |
| 1 | [1,2] | [0] | [- ,0,0,2] |
| 2 | [2,3?] | ... | ... |
- Complete rows for E1 graph; check with code.

## Level 4 — Property Tests
- P1: validator `isTopo(n,adj,order)` checks all edges forward.
- P2: cross-check Kahn vs DFS validity on 50 random DAGs (generate `i<j` edges).
- P3: cycle injection: add one back edge → both methods flag cycle.

## Level 5 — Stretch
- S1 Course-schedule-II style: return order or `[]`; add semester batches (levels).
- S2 Lexicographically smallest vs any-order benchmark on `n=10⁴`.
- S3 Cross-file: feed order into knapsack-style task scheduler (see MINI_PROJECT).

## Submission Checklist
- [ ] Both implementations + traces.
- [ ] Cycle/empty/self-loop tests green.
- [ ] Validator + random cross-check.
- [ ] Complexity notes: `O(V+E)` each.
