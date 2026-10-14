# Live Range Dashboard on a Lazy Segment Tree

Incident framing. The analytics team refreshes a dashboard of range sums
and range maxima over a 1M-cell event array while writes land between
refreshes. A brute-force scan per refresh costs O(n); the segment tree
answers both in O(log n) and applies range adds in O(log n) via lazy
propagation. This build proves the gap with both implementations wired
to the same query log.

Tree shape. Size 4n array layout over the event cells, each node holding
sum and max plus a pending-add tag. Point set, range add, range sum, and
range max all recurse to O(log n) nodes; push-down happens only on the
visited path so untouched subtrees keep their tags.

Leaderboard caller. The same tree backs range-max queries for game
divisions: best score on interval [l, r] with point updates on match
end. Max answers must equal a linear scan oracle on 10k random ranges.

Lazy audit. After every 500th operation in test mode, a full push-down
plus leaf comparison against a naive array must agree exactly; a tag
leak anywhere aborts the run with the node index.

Duel harness. Identical query logs (70 percent queries, 30 percent
updates) run against the tree and the brute force at n = 10k, 100k, 1M.
The report publishes per-query nanos for both and the crossover size
where the tree pulls ahead permanently.

Rotten inputs. Empty range, inverted bounds, range covering the whole
array, 100k consecutive adds to one cell (overflow policy documented),
update-then-query at the boundary index.

Ship list. Tree, dashboard CLI, duel harness, lazy-audit log, crossover
chart data. Marks: lazy correctness 12, oracle parity on both callers
10, duel honesty including the region where brute force wins 8.
## Audit rhythm
- Push-down check every 500 ops.
- Duel rerun on each change.
- Crossover size re-measured quarterly.
- Tag-leak abort message kept stable.
- Leaderboard oracle always on.
