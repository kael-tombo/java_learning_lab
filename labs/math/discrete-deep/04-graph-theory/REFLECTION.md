# Reflection: Graph Theory

## The Abstraction Move Is the Real Lesson

Euler's answer didn't improve on the bridge-walkers' intuition — it *deleted* most of the problem. The enduring lesson: before reaching for an algorithm, decide what to throw away. In this lab, whether a problem keeps edge weights, direction, or multiplicity changes everything (BFS vs Dijkstra, matching vs flow), and stating those choices explicitly is most of the design work.

## Dijkstra by Hand Changed How I Read the Code

Tracing the six-node example exposed the two places implementations actually go wrong: popping by *distance* rather than by name (C settled at 2 before B at 4 — several times I reached for the alphabetically next node) and the improvement cascade (dist(D) fell 10 → 8 only because B itself had just been improved from 4 → 3 through C). Seeing that "relaxation of an already-popped node can cascade into better paths downstream" explains why the priority queue must re-push instead of trusting the first value.

## Counts Before Code

The complexity table (BFS O(V+E), Dijkstra O((V+E) log V), Floyd–Warshall O(V³), Bellman–Ford O(V·E)) reads differently after doing the representations yourself: "O(V+E)" is a statement about adjacency lists, not about graphs. I will now always ask which representation a quoted complexity assumes — and default to stating mine.

## Where the Proofs Live

Three arguments worth keeping verbatim: the BFS-on-push invariant (first touch = fewest edges), Dijkstra's settling proof (any alternative leaves S through a ≥0 edge) and the exact point where negatives break it, and the cut property that licenses both MST greedy algorithms. Each is short enough to recall while coding — and each maps to a test (stale PQ entries, negative-weight fixture, MST vs Prim weight equality).

## The Security Angle Was Unexpected

Thinking of cert chains, attack graphs, and BGP origin validation as graph problems showed that most real "security" work is edge-set hygiene: reject cycles where a DAG is required, cap traversal budgets against fan-out explosions, and authenticate edges rather than optimize paths. The counting side (b^h paths at depth h) is where the denial-of-service risk comes from — same growth logic as the enumeration ceilings in lab 03.

## Open Threads

- Union–find's near-O(1) amortized behavior (inverse Ackermann) is a proof I have only sketched; worth reading Tarjan–Vuillemin carefully.
- Planarity (Kuratowski's forbidden subdivisions) and coloring lower bounds (Brooks) were treated only at the reference level here — they are the natural next depth.
- Max-flow algorithms (Dinic, push-relabel) deserve their own worked trace the way Dijkstra got one; the residual-network "undo" idea is the piece that needs practice.

## What I Would Do Differently in Code

Return `dist[]` + `parent[]` (O(V) memory) instead of building path strings inside the algorithm, force the "mark on enqueue / skip stale entries" lines with unit tests on the golden fixture, and refuse inputs whose declared vertex range doesn't match the parse (the 1-based/0-based assert). Those three changes cover every bug in the DEBUGGING file.
