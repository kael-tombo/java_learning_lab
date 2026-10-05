# THEORY — Topological Sort
> Mechanics + invariants + complexity proof sketch for DAG linearization.

## 1. Problem Statement
- Input: directed graph `G=(V,E)`.
- Output: order `v₁..vₙ` with every `u→v` having `u` before `v`, or cycle verdict.
- Exists ⟺ `G` is a DAG. Partial output + leftover nodes signals cycle.
- Success: `O(V+E)`, both Kahn + DFS forms, deterministic tie-break documented.

## 2. Kahn's Mechanics (Indegree)
- Compute `indeg[v]` for all. Queue all `indeg==0`.
- Pop `u`, append to order; for `v∈Adj[u]`: `indeg--`; if 0 enqueue.
- End: `|order|==V` → valid; else cycle (leftover = cyclic core + dependents).
- Lexicographically smallest: use `PriorityQueue` instead of FIFO (costs `log V`).
- Level batches (course-schedule semesters): drain layer by layer, count rounds.

## 3. DFS Mechanics (Postorder)
- DFS; on finish (`BLACK`), push `u` onto stack/list-front.
- Result reversed-finish = topo order (DAG only).
- Back edge (`→GRAY`) → cycle → abort with flag.
- Outer loop over all vertices (forest) — single source insufficient.

## 4. Invariants
- Kahn I: queue = exactly current indegree-0 remainder nodes; emitted prefix has no incoming from remainder.
- Init: indegrees exact; queue correct. Step preserves by decrementing only removed edges.
- DFS I: on DAG, when `u` finishes all descendants already emitted → prepending `u` keeps order valid.
- Termination: Kahn queue empty with remainder nonempty ⟺ every remainder node has indeg ≥1 ⟺ cycle.

## 5. Worked Traces
- `A→B,A→C,B→D,C→D`: indeg A0 → emit A → B,C → D. Orders ABCD or ACBD.
- Cycle `A→B→C→A`: no indeg-0 → order empty → cycle flagged.
- Disconnected `E` alone: indeg 0, appears anywhere valid.

## 6. Complexity Proof Sketch
- Indegrees: one edge scan `O(V+E)`. Each vertex queued/dequeued once, each edge decrements once → `O(V+E)`.
- DFS variant same `O(V+E)` as plain DFS + `O(1)` prepend per finish.
- Space `O(V+E)` graph + `O(V)` indeg/queue/order.
- Uniqueness: Hamiltonian-path DAG → unique order; else multiple (tie-break policy decides).
- Lower bound: must inspect every edge to certify order → `Ω(V+E)`.

## 7. Correctness Arguments
- Kahn sound: emitted edge `u→v` has `u` before `v` (u removed first, v indeg drops after).
- Kahn complete: DAG always has a source (indeg-0) — finite DAG sink/source lemma.
- DFS sound on DAG via finish-time ordering lemma (edge `u→v` ⇒ `fin[v]<fin[u]`).

## 8. When NOT to Use
- Undirected / cyclic workflows → topo undefined; use DFS cycle report + SCC instead.
- Weighted ordering with costs → critical-path (topo + DP), not pure topo.
- Dynamic graphs → incremental topo needed (Kahn per change is `O(V+E)` each).

## 9. Java Notes
- `ArrayDeque<Integer>` for Kahn; `PriorityQueue` for lexicographic.
- `List<List<Integer>>` adj; `int[] indeg` copy (don't mutate caller's).
- Iterative DFS with `(node,idx)` stack to get true postorder without recursion limits.

## 10. Checklist
- [ ] Both Kahn + DFS implemented + cross-checked.
- [ ] Cycle verdict tested (leftover vs back edge).
- [ ] Tie-break documented (FIFO vs PQ).
- [ ] Forest loop over all vertices.
