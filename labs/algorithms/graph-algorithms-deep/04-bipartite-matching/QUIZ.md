# Quiz — Bipartite Matching

15 questions. Each key gives the reason.

---

## Q1
State Berge's theorem.

<details><summary>Answer</summary>

A matching M is maximum iff there is no augmenting path w.r.t. M.

</details>

## Q2
What is an augmenting path?

<details><summary>Answer</summary>

An alternating non-matched/matched path between two unmatched vertices on opposite sides.

</details>

## Q3
Naive augmenting-path complexity?

<details><summary>Answer</summary>

O(V·E).

</details>

## Q4
Hopcroft–Karp complexity?

<details><summary>Answer</summary>

O(E·√V).

</details>

## Q5
Why is Hopcroft–Karp O(E·√V)?

<details><summary>Answer</summary>

O(√V) phases, each Θ(E); after √V phases the shortest augmenting path is long and few augmentations remain.

</details>

## Q6
State König's theorem.

<details><summary>Answer</summary>

In bipartite graphs, max matching size = min vertex cover size.

</details>

## Q7
One-line proof of max matching ≤ min vertex cover.

<details><summary>Answer</summary>

Each matching edge forces a distinct cover vertex.

</details>

## Q8
What does the BFS layering in HK build?

<details><summary>Answer</summary>

Layers by distance from unmatched L-vertices, used to find shortest augmenting paths.

</details>

## Q9
Hungarian algorithm use?

<details><summary>Answer</summary>

Maximum-weight perfect matching in a complete bipartite graph, Θ(n³).

</details>

## Q10
When does a problem reduce to bipartite matching?

<details><summary>Answer</summary>

When assignments are pairwise independent across two sides.

</details>

## Q11
General (non-bipartite) matching needs?

<details><summary>Answer</summary>

Edmonds' blossom algorithm.

</details>

## Q12
What does M Δ M* look like?

<details><summary>Answer</summary>

Alternating paths and cycles.

</details>

## Q13
Why do disjoint augmenting paths in one phase give correctness?

<details><summary>Answer</summary>

They are vertex-disjoint, so flipping each preserves alternation.

</details>

## Q14
What is the NIL sentinel in HK for?

<details><summary>Answer</summary>

It records the length of the shortest augmenting path found so far.

</details>

## Q15
Matching student to projects with preferences — which algorithm?

<details><summary>Answer</summary>

Stable matching (Gale–Shapley), not max bipartite matching.

</details>
