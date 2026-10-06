# Theory — Topological Sort

A *topological order* of a directed graph is a linear ordering of its
vertices such that every edge u → v has u before v. Such an ordering exists
if and only if the graph is acyclic (a DAG). The problem is the canonical
scheduling-of-prerequisites question: courses with prerequisites, build
steps with dependencies, task pipelines.

## Why DAGs only

If a topological order existed on a cycle v₁ → v₂ → … → vₖ → v₁, then v₁
must precede v₂, v₂ precede v₃, …, and vₖ precede v₁, giving v₁ < v₁ — a
contradiction. Conversely, every DAG has a topological order: a finite DAG
has a source (a vertex with in-degree 0), and removing it leaves a smaller
DAG; repeating yields an order.

## Kahn's algorithm (BFS)

Compute the in-degree of every vertex. Enqueue all vertices of in-degree 0.
Repeatedly dequeue a vertex u, output it, and for each outgoing edge u → v
decrement in-degree(v); when it hits 0, enqueue v. If the output contains
all n vertices, the graph is a DAG and the output is a topological order; if
some vertices never reach in-degree 0, they are part of (or downstream of) a
cycle. Each vertex is enqueued once and each edge relaxed once: Θ(V+E).

## DFS-based order

Alternatively, run DFS from every unvisited vertex and, on finishing a
vertex (post-order), push it onto a stack. The stack order reversed is a
topological order. The intuition: when DFS finishes u, every descendant of u
already appears below it on the stack, so u precedes them. Equivalently,
reversing the post-order reverses every edge. Θ(V+E) time.

## Using the order

Once you have a topological order, every dependency is "computed before its
dependents." This turns DAG problems into a single left-to-right scan: longest
path in a DAG, count of paths, evaluating an expression DAG, build-order
resolution. The topological sort is the preprocessing step that makes the
scan well-defined.

## Detecting a cycle

Both algorithms double as cycle detectors: Kahn's leaves ≥ 1 vertex
unoutputted iff a cycle exists; the DFS version finds a back edge iff a
cycle exists. A topological order and a cycle are mutually exclusive.

## Pitfalls

- Treating an undirected graph with topological sort — it is a directed
  concept.
- Forgetting that "no output for a vertex" signals a cycle, not an isolated
  component.
- Assuming the topological order is unique — most DAGs have many.
