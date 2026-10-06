# Math Foundation — Topological Sort

Derivations, applicability, and counter-examples for the formulas this lab relies on.

---

## DAG iff topological order

(⇒) Every finite DAG has a source: else walk backwards forever, revisiting a vertex — a cycle. Remove the source and repeat; the removal order is a topological order. (⇐) If a topological order existed on a cycle v₁→…→vₖ→v₁, then v₁ < v₂ < … < vₖ < v₁, contradiction.

So existence of a topological order and acyclicity are equivalent.

## Kahn's correctness

Maintain that output-so-far is a valid prefix: every emitted vertex had all its predecessors emitted (its in-degree reached 0 only after they were processed). If the queue empties before n vertices are emitted, the unemitted vertices form a subgraph where every vertex has in-degree ≥ 1 — which contains a cycle.

Hence "queue empties early" ⟺ the graph has a cycle.

## DFS reverse post-order

For every edge u→v in a DAG, finish(u) > finish(v): if v finishes first, then when u is examined v is already black, so finish(u) > finish(v); v cannot finish after u because then v would be a descendant of u and finish before u. Ordering by decreasing finish time therefore puts u before v.

This is why reversing post-order is a topological order.

## DAG longest path as DP

Let L[v] be the longest path ending at v. Topological order guarantees all predecessors of v are computed first, so L[v] = max over u→v of L[u] + w(u,v) is well-defined. Θ(V+E).

In a general graph this relaxation must iterate (Bellman–Ford); in a DAG one pass in topological order suffices.

## No source ⇒ cycle

If every vertex has in-degree ≥ 1, start anywhere and follow incoming edges backwards; after n+1 steps some vertex repeats — the segment between repeats is a cycle.

Contrapositive: a finite DAG always has at least one source.
