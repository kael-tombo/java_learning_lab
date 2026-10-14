# Ephemeral Range Store on Treaps, with Persistent Cousin

Depot. A game-server leaderboard and social feed need an ordered
key-value store that appears, serves a burst, and vanishes - no disk,
no recovery story, just fast range ops. Randomized treaps give expected
O(log n) insert/delete/split/merge with short code; a persistent
variant serves undo stacks as the second act.

Treap core. Random priorities with heap order plus BST key order; split
by key and merge by priority compose insert, delete, and range extract.
Expected depth logarithmic - the report shows the measured depth
histogram at 200k keys against the log curve, seed published.

Leaderboard caller. Score updates, rank queries, top-K windows, range
extracts for page views; all answers diffed against a sorted-list
oracle on 30k scripted ops. Split/merge power the page slices directly.

Feed caller. Time-ordered posts with range pulls and mid-feed deletes;
cursor pagination verified stable across concurrent-shaped (scripted)
deletes.

Persistent cousin. Path-copied insert/delete returning new roots for
undo stacks; old versions readable mid-session. Sharing ratio measured
like lab 20 in miniature; 5k-version walk proves old reads never shift.

Priority audit. Heap property verified by full walk after fuzz batches;
degenerate-priority injection (fixed seed of equal priorities) must keep
key order correct even as balance degrades - reported, with the depth
cost quoted.

Hand in. Both treaps, callers, depth data, oracle logs, audit output.
Weighting: split/merge correctness 12, caller parity 10, persistence
plus audit 8.
## Depth watch
- Histogram vs log curve.
- Seed published.
- Priority audit in CI.
- Equal-priority probe kept.
- Sharing ratio quoted.
