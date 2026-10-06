# Quiz — Heavy-Light Decomposition

15 questions. Each key gives the reason.

---

## Q1
What is a heavy child?

<details><summary>Answer</summary>

The child with the largest subtree.

</details>

## Q2
HP node: heavy edge condition?

<details><summary>Answer</summary>

The child's subtree is at least half the parent's.

</details>

## Q3
Wood node: a chain is?

<details><summary>Answer</summary>

A maximal path of heavy edges.

</details>

## Q4
Light edges on a root path?

<details><summary>Answer</summary>

At most log₂ n.

</details>

## Q5
Base array property of chains?

<details><summary>Answer</summary>

Each chain is a contiguous interval.

</details>

## Q6
Path query complexity with HLD+segtree?

<details><summary>Answer</summary>

Θ(log² n).

</details>

## Q7
LCA via HLD complexity?

<details><summary>Answer</summary>

O(log n).

</details>

## Q8
Subtree query — right structure?

<details><summary>Answer</summary>

Euler-tour segment tree, one range query.

</details>

## Q9
HLD two DFS passes?

<details><summary>Answer</summary>

First computes size + heavy child; second builds the base array.

</details>

## Q10
Why halving?

<details><summary>Answer</summary>

A light child's subtree is less than half the parent's — each light edge at least doubles the remaining path's "budget."

</details>

## Q11
top[v] stored per vertex?

<details><summary>Answer</summary>

The head of the chain containing v — used for jumps.

</details>

## Q12
pos[v] stored per vertex?

<details><summary>Answer</summary>

v's position in the base array — used for range queries.

</details>

## Q13
Path u→v via LCA: segments?

<details><summary>Answer</summary>

O(log n) chain segments on each side of the LCA.

</details>

## Q14
Why not use HLD for subtrees?

<details><summary>Answer</summary>

Euler tour gives one range; HLD would split needlessly.

</details>

## Q15
LCA meeting on the same chain means?

<details><summary>Answer</summary>

The higher of the two on that chain is the LCA.

</details>
