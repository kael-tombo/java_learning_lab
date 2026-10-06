# Quiz — Topological Sort

15 questions. Each key gives the reason.

---

## Q1
What is a topological order?

<details><summary>Answer</summary>

A linear order of vertices where every edge u→v has u before v.

</details>

## Q2
When does one exist?

<details><summary>Answer</summary>

Exactly when the graph is a DAG.

</details>

## Q3
Kahn's algorithm idea?

<details><summary>Answer</summary>

Remove vertices of in-degree 0, decrement neighbours, repeat.

</details>

## Q4
Kahn's complexity?

<details><summary>Answer</summary>

Θ(V+E).

</details>

## Q5
DFS-based topo order?

<details><summary>Answer</summary>

Reverse post-order of DFS.

</details>

## Q6
How does Kahn detect a cycle?

<details><summary>Answer</summary>

Some vertices never get in-degree 0 / never leave the queue.

</details>

## Q7
DFS cycle detection in the same pass?

<details><summary>Answer</summary>

A back edge to a grey (in-progress) vertex signals a cycle.

</details>

## Q8
Longest path in a DAG — how?

<details><summary>Answer</summary>

Relax edges in topological order.

</details>

## Q9
Is the topological order unique?

<details><summary>Answer</summary>

No — a DAG has many in general.

</details>

## Q10
Why must every DAG have a source?

<details><summary>Answer</summary>

A finite digraph with no source contains a cycle — walk backwards until you revisit a vertex.

</details>

## Q11
Build systems reduce to?

<details><summary>Answer</summary>

Topological sort of the dependency DAG.

</details>

## Q12
A cycle forces?

<details><summary>Answer</summary>

No topological order — the requirements contradict each other.

</details>

## Q13
Kahn's output order property?

<details><summary>Answer</summary>

Every vertex appears after all its dependencies.

</details>

## Q14
Post-order of DFS gives?

<details><summary>Answer</summary>

Reverse topological order.

</details>

## Q15
Two valid topo orders of a single edge a→b?

<details><summary>Answer</summary>

Only a then b.

</details>
