# Exercises — Cycle Detection

Attempt each before reading the hint.

## Ex 1
In three-colour DFS, which edge class signals a cycle and why?

<details><summary>Hint</summary>

A back edge to a grey vertex — the grey vertex is an ancestor, closing a cycle.

</details>

## Ex 2
Why does a forward edge not indicate a cycle?

<details><summary>Hint</summary>

A forward edge goes to a black vertex — finished, not on the stack, so no cycle is closed.

</details>

## Ex 3
How does Union-Find detect a cycle in an undirected graph?

<details><summary>Hint</summary>

find(u)==find(v) when examining (u,v) means u and v are already connected.

</details>

## Ex 4
Floyd: why do slow and fast pointers meet?

<details><summary>Hint</summary>

Once both are in the cycle, fast gains one position per step and laps slow.

</details>

## Ex 5
Floyd: how do you find the entry of the cycle?

<details><summary>Hint</summary>

Reset one pointer to the start; move both one step — they meet at the entry.

</details>

## Ex 6
In an undirected graph, why is the parent edge not a cycle?

<details><summary>Hint</summary>

Every undirected edge is a two-way pair; only an edge to a non-parent visited vertex forms a cycle.

</details>

## Ex 7
How does Tarjan's SCC relate to cycle detection?

<details><summary>Hint</summary>

Any non-singleton SCC (or a self-loop) is a cycle.

</details>
