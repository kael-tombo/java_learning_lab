# Offline Connectivity Judge on Undoable Union-Find

Docket. A judge receives a timeline of edge additions AND removals plus
connectivity questions at named instants - the classic offline dynamic
connectivity problem. Persistent answers come from a rollback DSU walked
over a segment tree of edge lifespans.

Rollback DSU. Union by size without path compression (compression would
break undo); every mutation pushes an inverse record on an op stack.
Snapshot returns the stack height; rollback pops to it. Union, find
(O(log n) via tree height bound), snapshot, and rollback are the whole
surface.

Lifespan engine. Each edge's alive interval is added to segment-tree
nodes covering it; a DFS applies node edges, answers queries at leaves,
then rolls back. Query answers must equal a brute-force per-instant BFS
oracle on 300 generated timelines.

Partition simulator. Second caller: scripted network partitions
applied and reverted in nesting order; nested rollback correctness
checked by interleaving three partition scopes and verifying each level
restores exactly.

Depth audit. Union tree height tracked; the log-height bound is shown
measured, and a test asserts find cost stays within it at 100k unions.
Op-stack memory quoted per 10k unions so the undo cost is explicit.

Misuse file. Rollback past a snapshot (typed error), query with no
active edges (specified empty answer), edge removed before added
(ingest rejects with line number), snapshot leak across timelines
(fresh DSU per case, enforced).

Deliver. DSU, lifespan engine, simulator, oracle logs, height data.
Marks: rollback exactness 12, timeline parity 10, bound plus misuse 8.
## Judge log
- Timelines versioned with answers.
- Oracle rerun on every change.
- Height bound asserted in CI.
- Nested-scope test kept green.
- Op-stack memory quoted.
