# Exercises — Heavy-Light Decomposition

Attempt each before reading the hint.

## Ex 1
Define a heavy child and a chain.

<details><summary>Hint</summary>

Heavy child = child with the largest subtree; a chain is a maximal heavy-edge path.

</details>

## Ex 2
Why does a root-to-v path cross O(log n) light edges?

<details><summary>Hint</summary>

Each light edge at least halves the subtree size — at most log₂ n halvings.

</details>

## Ex 3
Path query decomposition via HLD?

<details><summary>Hint</summary>

Climb u and v by chain jumps to the LCA; answer each segment with a segment-tree range query.

</details>

## Ex 4
How is LCA computed with HLD?

<details><summary>Hint</summary>

Climb both to the same chain; the deeper chain-head meeting point is the LCA.

</details>

## Ex 5
Subtree query — which structure?

<details><summary>Hint</summary>

Euler-tour segment tree: the subtree is one contiguous range.

</details>

## Ex 6
Why is each chain contiguous in the base array?

<details><summary>Hint</summary>

The second DFS visits the heavy child first, so a heavy path is traversed contiguously.

</details>

## Ex 7
Total path-query complexity?

<details><summary>Hint</summary>

Θ(log² n): O(log n) chain segments × O(log n) per range query.

</details>
