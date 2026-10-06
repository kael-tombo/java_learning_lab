# Exercises — Graph Coloring

Attempt each before reading the hint.

## Ex 1
Prove every graph is (Δ+1)-colourable.

<details><summary>Hint</summary>

Greedy: a vertex has at most Δ coloured neighbours, so one of Δ+1 colours is free.

</details>

## Ex 2
State Brooks' theorem and its exceptions.

<details><summary>Hint</summary>

Connected G is Δ-colourable unless G is K_{Δ+1} or an odd cycle; those need Δ+1.

</details>

## Ex 3
Why is a graph bipartite iff it is 2-colourable?

<details><summary>Hint</summary>

A 2-colouring is exactly a two-set split with no intra-set edge.

</details>

## Ex 4
Why is bipartite testing Θ(V+E)?

<details><summary>Hint</summary>

One BFS, colouring by level parity; a conflicting edge means not bipartite.

</details>

## Ex 5
What is DSATUR's selection rule?

<details><summary>Hint</summary>

Colour the vertex with the most distinctly-coloured neighbours next.

</details>

## Ex 6
Give the chromatic number of an even cycle and an odd cycle.

<details><summary>Hint</summary>

2 and 3.

</details>

## Ex 7
Why is 3-colourability NP-complete?

<details><summary>Hint</summary>

Via reduction from 3SAT; even planar degree-4 graphs are hard.

</details>
