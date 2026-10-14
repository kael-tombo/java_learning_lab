# Leaderboard Clone: Redis-Style Sorted Set on a Skip List

Pitch. Rebuild the sorted-set behind a game leaderboard - add, remove,
rank, range-by-score, top-K - on a probabilistic skip list, then show
where it stands against the tree-based and concurrent-map options.

Coin-flip core. Levels drawn geometrically with p = 1/2 (cap 32); every
opinion about performance derives from expected O(log n) search, insert,
and delete. The report records the observed level histogram at 200k
members beside the theoretical halving per level.

Sorted-set verbs. ZADD with score update, ZREM, ZRANK/ZREVRANK, ZRANGE
by rank window, ZRANGEBYSCORE with limit, ZCARD. Rank answers verified
against a TreeMap-plus-sorted-list oracle on 40k scripted ops.

Concurrency note. The second caller is an ordered index modeled on
ConcurrentSkipListMap semantics: lock-free reads, documented retry on
tower splice races. A two-thread soakTallies successful ops on both
sides; lost updates fail the run.

Level audit. A debug walk verifies every level-0 link chain is sorted
and every higher link skips forward correctly; forward-pointer counts
reconciled after each fuzz batch.

Degenerate weather. All-equal scores (member tiebreak by id, tested),
monotonic inserts, 10k deletes down to empty, rank queries past the end
(typed miss, not wrap).

Hand in. Skip list, leaderboard CLI, soak log, level histogram, oracle
parity log, comparison paragraph vs TreeMap with measured margins. Bar:
set semantics 12, level-structure evidence 10, soak plus misuse 8.
## Nightly soak
- 200k members, level histogram archived.
- Oracle diff must stay empty.
- Tower-splice retries counted.
- All-equal-scores probe included.
- Halt on first lost update.
