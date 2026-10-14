# Time-Travel Analytics on Persistent Segment Trees

Archive. An event log of 1M counter updates must answer: what was the
range sum at 3 PM Tuesday - any Tuesday, any minute. Persistent segment
trees keep every version queryable in O(log n) time with O(log n) fresh
nodes per update, sharing the rest with the previous root.

Version mechanics. Point update clones the O(log n) path and reuses all
other nodes; version roots indexed by timestamp in an append-only array.
Range query pins a version id and walks that root alone. Version count
times log n bounds total allocation - the report quotes measured nodes
per update at three log sizes.

Analytics caller. Range sums and range maxima over arbitrary historical
windows; 5k queries across 200 pinned versions diffed against per
version naive arrays. Every answer must match; a single mismatch names
the version, range, and both values.

MVCC-style caller. Counter service with snapshot reads under a write
stream: readers pin versions, writers advance. A scripted interleave of
10k writes and 2k reads must show each read matching its pinned version
exactly - no torn history.

Retention file. Version pruning policy (keep hourly beyond a week, pin
API for audits); pruned-version queries return a typed gone error, never
a wrong answer. Memory before/after a prune cycle quoted.

Corruption rehearsal. Update applied to a stale root (branch rule
invoked or rejected - documented), query at future version (rejected),
root array truncation simulation (gone errors, counted).

Deliver. Tree, analytics CLI, MVCC harness, oracle logs, retention
note. Marks: version-query parity 12, snapshot isolation proof 10,
retention plus rejection handling 8.
## Version atlas
- Hourly pins beyond a week.
- Gone-error semantics tested.
- Prune cycle memory quoted.
- Stale-root rule documented.
- Replay check in CI.
