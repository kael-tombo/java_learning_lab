# Quiz — Cycle Detection

15 questions. Each key gives the reason.

---

## Q1
Which edge in three-colour DFS proves a cycle?

<details><summary>Answer</summary>

A back edge to a grey vertex.

</details>

## Q2
Why ignore the parent edge in undirected cycle detection?

<details><summary>Answer</summary>

It is the same undirected edge seen from the other side, not a cycle.

</details>

## Q3
Union-Find cycle test on (u,v)?

<details><summary>Answer</summary>

Cycle iff find(u) == find(v) before adding the edge.

</details>

## Q4
Floyd meeting condition?

<details><summary>Answer</summary>

Slow and fast pointers meet inside the cycle.

</details>

## Q5
Floyd entry-point method?

<details><summary>Answer</summary>

Restart one pointer at the start; advance both by one until they meet.

</details>

## Q6
Three-colour states?

<details><summary>Answer</summary>

white (unvisited), grey (on stack), black (finished).

</details>

## Q7
Tarjan outputs?

<details><summary>Answer</summary>

SCCs in reverse topological order.

</details>

## Q8
Kosaraju passes?

<details><summary>Answer</summary>

Two DFS passes — one on G, one on Gᵀ.

</details>

## Q9
Cycle in a wait-for graph means?

<details><summary>Answer</summary>

Deadlock.

</details>

## Q10
Cycle in a dependency graph means?

<details><summary>Answer</summary>

Infeasible build — a circular requirement.

</details>

## Q11
Self-loop in three-colour DFS?

<details><summary>Answer</summary>

A back edge to the current grey vertex — a cycle of length 1.

</details>

## Q12
Why does Floyd's work on a finite functional graph?

<details><summary>Answer</summary>

Iterating f from any start must repeat a state; once in the cycle the fast pointer laps the slow one.

</details>

## Q13
Cross edge in directed DFS — cycle?

<details><summary>Answer</summary>

No: a cross edge goes to a black vertex in a different subtree.

</details>

## Q14
Two-colour DFS insufficient for directed cycle detection?

<details><summary>Answer</summary>

Yes — it cannot distinguish a back edge (cycle) from a cross edge (no cycle).

</details>

## Q15
Time to recover the cycle from three-colour DFS?

<details><summary>Answer</summary>

Walk the recursion stack from the grey target back to the current vertex — Θ(cycle length).

</details>
