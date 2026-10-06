# Exercises — Topological Sort

Attempt each before reading the hint.

## Ex 1
Prove a topological order exists iff the graph is a DAG.

<details><summary>Hint</summary>

Cycle ⇒ contradiction v₁ < v₁; DAG ⇒ repeatedly remove a source.

</details>

## Ex 2
Why does Kahn's leave unprocessed vertices iff a cycle exists?

<details><summary>Hint</summary>

A cycle keeps every member's in-degree ≥ 1, so none is enqueued.

</details>

## Ex 3
State the DFS-based topological order.

<details><summary>Hint</summary>

Reverse of post-order.

</details>

## Ex 4
Longest path in a DAG needs what preprocessing?

<details><summary>Hint</summary>

A topological order, then relax edges left-to-right.

</details>

## Ex 5
How do you get a topological order from Kahn's queue?

<details><summary>Hint</summary>

Dequeue order is one; vertices with in-degree 0 first.

</details>

## Ex 6
Does a DAG always have a topological order?

<details><summary>Hint</summary>

Yes — induction on the existence of a source.

</details>

## Ex 7
Two different topological orders — both valid?

<details><summary>Hint</summary>

Yes if both respect every edge u→v (u before v).

</details>
