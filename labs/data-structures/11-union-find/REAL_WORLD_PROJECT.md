# Connectivity Pipeline: Kruskal MST plus Accounts-Merge on DSU

Two jobs share one disjoint-set union. Overnight, Kruskal's algorithm
lays minimum-spanning-tree edges over the datacenter fabric. By day, an
accounts-merge pipeline resolves which user records belong to one human.

Union-find core. Parent array with union by size and path halving; every
operation costs effectively alpha(n), the inverse Ackermann function,
which stays below 5 for any input that fits on hardware. A component
counter and max-size tracker ride along for free.

Kruskal side. Edges sort once, then union in order, skipping pairs
already connected. The MST weight must equal a Prim-computed reference
on every fixture; the report quotes edge-sort time separately so the
DSU share of the runtime is visible, not guessed.

Accounts side. Records sharing an email or phone union into entities;
each entity emits a canonical id plus member list. The oracle is a
quadratic pairwise comparison on 5k records; entity sets must match
exactly, including singleton accounts nobody merges.

Scale fixtures. Percolation grid 500x500 (open sites union with open
neighbors, percolation = top row joined to bottom), network fabric with
50k nodes / 200k candidate edges, account file with 100k records.

Breakage set. Self-union, duplicate union, find on unknown element,
Kruskal fed a disconnected graph (forest output specified), accounts
with empty contact fields (never merge on blanks).

Deliver. DSU, both callers, fixture generators, oracle logs, timing
split (sort vs union), one-page entity-resolution note. Credit: MST
parity 12, merge exactness 10, percolation plus misuse handling 8.
## Lab ledger
- MST weight matched on all fixtures.
- Entity sets byte-identical to oracle.
- Percolation threshold noted.
- Sort-vs-union split published.
- Blanks-never-merge test kept.
