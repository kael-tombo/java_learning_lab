# RFC: Live Counters and Order Statistics on a Fenwick Tree

Status: draft. Question before the group: for prefix-sum-heavy traffic,
should the leaderboard service use a Fenwick tree rather than the
segment tree of lab 12, trading generality for half the memory and
shorter code.

Structure. BIT array of length n+1 with least-significant-bit stepping;
add(i, delta) and prefix(i) each touch O(log n) cells. Range sum is two
prefix calls. Memory is one array of n+1 longs - roughly half the 4n
segment layout - and the RFC asks reviewers to confirm the measured
halving at 1M counters.

Counting service. Live event counters with per-category prefix queries
and rank drinks: how many events at or below score X, kth percentile by
binary lifting on the tree in O(log n). Percentile answers checked
against a sorted-array oracle on 50k samples.

Inversion caller. Streaming inversion counts over match results verify
the tree on a second shape: process from the right, query prefix below
current, add current. Totals must equal the O(n^2) oracle on 8k inputs.

Build note. O(n) construction from a frequency array is specified and
timed against n insertions; both paths must yield identical trees.

Limits, stated plainly. No range-min/max, no range-add without a second
tree, indices start at 1 (the RFC mandates a guard translating 0-based
callers). Each limit gets a test proving the failure is loud.

Decision requested. Fenwick vs segment tree for prefix-only traffic,
with the memory and code-size numbers attached. Marks: prefix proof 12,
inversion plus percentile parity 10, limit tests 8.
## Decision log
- Prefix-only traffic confirmed first.
- Memory halving measured, not assumed.
- 1-based guard reviewed twice.
- Second-tree need ruled out in writing.
- Verdict dated and signed.
