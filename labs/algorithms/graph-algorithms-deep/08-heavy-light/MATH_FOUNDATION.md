# Math Foundation — Heavy-Light Decomposition

Derivations, applicability, and counter-examples for the formulas this lab relies on.

---

## Light-edge bound

Let s(v) be the subtree size of v. If (u,c) is a light edge, then size(c) ≤ size(u)/2 (c is not the heaviest child, so its subtree is at most half of u's). Each light edge on the root-to-v path at least halves the remaining size, so there are at most log₂ n of them.

Hence any root-to-v path crosses at most log₂ n chains.

## Path query segment count

A query u→v is split into two climbs: u→LCA and LCA→v. Each climb crosses one chain boundary per light edge, so each climb touches O(log n) chains. Answering a chain segment is one segment-tree range query, Θ(log n). Total Θ(log² n).

This is the standard HLD path-query bound.

## LCA climb invariant

Maintain the invariant that the current chain head of u is no deeper than... precisely: while top[u] != top[v], move the vertex whose chain head is deeper up to its parent. Each move removes one chain and at least halves the subtree size of the moved vertex. So the loop runs O(log n) times.

When top[u] == top[v], both are on one chain and the shallower vertex is the LCA.

## HLD construction correctness

The first DFS computes size(v) bottom-up, so size(child) is known before the heavy-child choice. The second DFS, visiting the heavy child first, numbers each heavy path contiguously — so every chain is one interval of the base array.

That contiguity is what reduces a path query to range queries.

## Subtree-as-interval

In the Euler-tour DFS order, the subtree of v is exactly the set of vertices visited between the first and last visit to v — a contiguous range. A subtree aggregate is therefore one range-sum query.

HLD is unnecessary for subtrees because the plain Euler order already linearises them.
