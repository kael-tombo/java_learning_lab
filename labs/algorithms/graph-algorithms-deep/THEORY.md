# THEORY — Graph Algorithms Deep Track
> Mechanics + invariants + complexity proof. Track `graph-algorithms-deep`.

## 1. Problem statement (5)
- Input, output, constraints stated formally per graph family.
- For this track: paths/trees/flows/matchings/colorings on G=(V,E).
- Context: networks, schedules, assignments, routing.
- Success = correct output on all edge cases + proven bounds.

## 2. Intuition in one paragraph (8)
- Graph algorithms maintain a promise: dist labels bound true shortest paths; heights bound flow pushing; colors stay proper; HLD chains stay contiguous.
- Think of it as maintaining a promise while scanning/building the answer.
- If the promise ever breaks, the algorithm has a repair step.
- Example domains: road networks, airline scheduling, exam timetabling.

## 3. Formal model (10)
- State: defines current partial solution.
- Decision: choice at each step derived from cut/path/flow structure.
- Transition: how state evolves (see recurrence below).
- Objective: minimize/maximize cost or decide feasibility.
- Model instances: `dist[v] upper bounds`; `residual capacities`; `match pairs`; `color classes`; `chain heads`.

## 4. Mechanics step-by-step (15)
1. Initialize structures (arrays, heaps, hash maps as needed).
2. Establish base case / empty-structure invariant.
3. Iterate / recurse over input in defined order.
4. Apply local rule (greedy choice, DP transition, pointer move).
5. Maintain auxiliary data (prefix sums, pi table, residual graph).
6. Prune / skip provably useless branches.
7. Record best answer seen so far.
8. Terminate when input exhausted or target reached.
9. Reconstruct solution via parent pointers if needed.
10. Validate output with checker.
11. Dijkstra: extract-min unsettled; relax outgoing edges once.
12. Bellman-Ford: V-1 relaxations + negative-cycle check pass.
13. Dinic: BFS levels then blocking-flow DFS; repeat.
14. Hopcroft-Karp: BFS layers + batch DFS augments.
15. HLD: heavy paths + segment tree over base array.

## 5. Worked trace (12)
- Small input example: Dijkstra on 5 nodes; Dinic on 4 nodes.
- Table-driven trace (step | state | decision | invariant holds?).
- Step 1: init — invariant holds vacuously.
- Step 2: first decision — show why alternatives are dominated.
- Step 3: middle — show auxiliary structure update.
- Step 4: last — show answer extraction.
- Key lesson: trace exposes off-by-one and order bugs early.
- MST trace: Kruskal edge order with DSU sets.
- Matching trace: augmenting path flips.
- HLD trace: chains over a 7-node tree.

## 6. Invariants (precise) (10)
- I1: Dijkstra settled nodes hold final shortest distances.
- I2: residual graph always mirrors remaining capacity both ways.
- I3: matching stays valid (no shared endpoints) after each augment.
- I4: topo order respects every processed edge direction.
- I5: HLD base array keeps each heavy path contiguous.
- Initialization: I holds before loop (empty prefix).
- Maintenance: each iteration re-establishes I (case split).
- Termination: I + exit condition => correctness.

## 7. Correctness proof sketch (10)
- Lemma 1 (safety): maintained invariant holds each iteration.
- Lemma 2 (progress): measure strictly decreases/increases toward goal.
- Theorem: on termination output is optimal/correct.
- Proof by induction on steps using I1–I5.
- Counterexample if invariant dropped: construct small failing input.
- Max-flow: min-cut duality certifies optimality at zero residual path.

## 8. Complexity analysis with proof (12)
- Count primitive ops per step; sum over steps.
- Recurrence where applicable: T(n) = a·T(n/b) + f(n) (see MATH_FOUNDATION.md).
- Apply Master theorem / Akra-Bazzi / accounting method.
- Typical bounds: MST O(E log V); Dijkstra O(E log V); BF O(VE); Floyd O(V³); Dinic O(V²E); Hopcroft-Karp O(E√V); HLD query O(log² n).
- Space: adjacency + labels + residual edges.
- Lower bound argument: comparison / information-theoretic where relevant.
- Tightness: exhibit worst-case family achieving the bound.

## 9. Variants and connections (8)
- Iterative vs recursive formulations.
- Binary vs Fibonacci heaps; Dinic vs push-relabel.
- Randomized / parallel / streaming variants.
- Reduces to / from neighboring lab topics.
- When NOT to use: input too small, constraints violated, simpler method wins.

## 10. Common misconceptions (5)
- Confusing average with worst case.
- Dijkstra on negative weights (forbidden).
- Off-by-one in indices / hash modulus.
- Assuming sorted input when it is not.
- Ignoring integer overflow in cost accumulation.

## 11. Interview signal (3)
- State invariant first, then code.
- Derive complexity without hand-waving.
- Name one pitfall and its test.

## 12. Checklist (2)
- [ ] Can replay trace without notes. [ ] Can prove bound. [ ] Can code in 20 min.
