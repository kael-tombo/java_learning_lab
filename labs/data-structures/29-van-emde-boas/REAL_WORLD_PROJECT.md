# Bounded Timer Scheduler on a van Emde Boas Tree

Clock shop. A scheduler tracks up to 1M pending timers over a bounded
universe (2^20 millisecond slots) needing successor/predecessor/min/max
in O(log log U) - effectively a handful of steps. The lab also keeps the
route-matching caller over bounded prefix space as the second proof.

Structure. Recursive clusters with summary, min/max caching, universe
squaring down to base case; operations recurse on high/low halves for
the textbook O(log log U) bound. The report walks one insert and one
successor call with the recursion depth counted, not hand-waved.

Timer caller. Schedule, cancel, fire-due (successive successors), peek
next; fire order must equal a PriorityQueue oracle on 100k scripted
timer ops including duplicate deadlines (tiebreak documented).

Prefix caller. Bounded-space route/prefix matching verified against a
TreeSet oracle on 50k entries; min/max/successor agreement must be exact.

TreeSet duel. Both structures timed on insert/successor/delete at
universe sizes 2^16 and 2^20 with 200k occupants; memory per occupant
quoted from heap deltas. The verdict states the universe size where the
vEB wins and where its overhead loses - no universal victory claimed.

Universe rules. Keys outside [0, U) rejected loudly; empty-tree min/max
typed miss; full universe behavior specified; non-power-of-two request
rounded with the rule logged.

Ship. vEB, both callers, duel table, recursion-depth note, universe
rule tests. Bar: oracle parity 12, bound demonstration 10, duel candor
8.
## Universe card
- U = 2^20 default posted.
- Out-of-range rejects tested.
- Duel rerun per release.
- Recursion depth logged.
- Tiebreak rule documented.
