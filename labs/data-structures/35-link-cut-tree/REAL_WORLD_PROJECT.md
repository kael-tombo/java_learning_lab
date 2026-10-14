# SDN Prototype on Link-Cut Trees: Dynamic Forest Ops

Control plane. A software-defined-network controller tracks a changing
topology: links appear and vanish, operators ask connectivity and
path-max latency between switches. Link-cut trees hold the forest with
amortized O(log n) link, cut, connected, and path queries - the lab's
capstone, and the hardest audit in the track.

LCT core. Preferred-path splay decomposition with path-parent pointers;
expose/access, makeRoot (lazy reversal flag), link, cut, findRoot,
path aggregate (max edge weight). Splay amortized logarithmic behavior
is shown via operation counts on scripted sequences, not merely cited.

Topology caller. 500-switch fabric with 5k link/cut events plus
connectivity and path-max queries interleaved; every answer diffed
against a naive adjacency BFS/DFS oracle. Zero divergences tolerated -
one wrong path-max fails the run with the event index.

Latency caller. Edge weights as link latencies; path-max and path-sum
aggregates verified against the oracle on 10k queries over the live
forest. Cut-then-query across the cut must report disconnected, not a
stale aggregate.

Operation journal. Every mutation logged with its resulting root
structure hash; a replay tool rebuilds the forest from the journal and
must converge to identical aggregates - the closest this lab gets to a
recovery story.

Misuse docket. Link creating a cycle (rejected - forest only, tested),
cut of a non-edge (no-op with signal), query on isolated node (typed
answer), makeRoot idempotence (double call stable).

Ship. LCT, controller CLI, journal plus replay, oracle logs, splay
count data. Credit: oracle parity 12, aggregate exactness 10, journal
plus rejection discipline 8.
## Forest journal
- Journal replayed in CI.
- Cycle-link rejects tested.
- Splay counts archived.
- Stale-aggregate probe kept.
- 500-switch fixture pinned.
