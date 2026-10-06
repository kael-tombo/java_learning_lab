# Theory — Heavy-Light Decomposition

Heavy-light decomposition (HLD) is the standard trick for turning
*path*-based tree queries into a small number of *array range* queries. The
idea dates to Sleator and Tarjan (1983) and is the go-to for competitive
programming and tree databases.

## The decomposition

Root the tree. For each vertex v, let size(v) be its subtree size. Among the
children of v, the *heavy* child is the one with the largest subtree (ties
broken arbitrarily); all other children are *light*. Equivalently, an edge
is heavy if the child's subtree is at least half the parent's subtree.
Following heavy edges from the root partitions the tree into *chains* —
maximal paths of heavy edges. Each chain is a contiguous segment of the
Euler-tour-like "base array" produced by a second DFS that visits heavy
children first.

## Why the light-edge count is logarithmic

Walk from the root to a vertex v and count the light edges on the path. Each
light edge goes from a vertex u to a child c whose subtree is strictly less
than half of u's subtree — so crossing a light edge at least halves the
remaining subtree size. Starting from the root (subtree size n), at most
log₂ n light-edge crossings are possible. Every root-to-v path crosses at
most log₂ n chain boundaries.

## Path queries via the base array

Number vertices by DFS order that visits the heavy child first, so each
chain is a contiguous interval in the order. Store vertex values in this
"base array." A path query from u to v then decomposes: climb u and v to
their lowest common ancestor (LCA) by repeated "jump to the chain head of my
top-most vertex" — each jump crosses one light edge, so O(log n) jumps — and
answer each chain segment with a range query on the base array. With a
segment tree over the base array, each segment query is O(log n), giving
O(log² n) total.

## LCA via HLD

LCA(u,v) is found by climbing both u and v toward the root by chain jumps
until they land on the same chain; the higher of the two positions on that
chain is the LCA. Because each jump halves the subtree size, the total number
of jumps from each of u and v is O(log n), so LCA is O(log n) — the same
bound as binary lifting, but derived from the decomposition rather than from
powers of two.

## Subtree queries are a different animal

HLD is built for *paths*. A subtree query (aggregate over all descendants of
v) is simpler with the plain Euler tour: the subtree of v is a contiguous
interval in the DFS order, so a subtree query is a single range query — O(log
n) with a segment tree, no HLD needed. Choosing the right structure —
Euler-tour segment tree for subtrees, HLD for paths — is half of the skill.

## Complexity summary

| Structure | Query | Update | Preprocess |
|-----------|-------|--------|------------|
| HLD + segment tree, path query | Θ(log² n) | Θ(log² n) | Θ(n log n) |
| HLD + segment tree, LCA | Θ(log n) | — | Θ(n log n) |
| Euler-tour + segment tree, subtree | Θ(log n) | Θ(log n) | Θ(n log n) |
| Binary lifting, LCA | Θ(log n) | — | Θ(n log n) |

## Pitfalls

- Using HLD for subtree queries — Euler tour is simpler and faster.
- Forgetting that HLD needs the chain head's base-array position to turn a
  path segment into a range — store `top[v]` and `pos[v]` for every vertex.
- Off-by-one in the "climb until same chain" loop: the LCA is on the chain
  where u and v first meet, not where they first share a jump.
- Overwriting the heavy-child choice — the largest-subtree child must be
  visited first in the base-array DFS so each chain is contiguous.
