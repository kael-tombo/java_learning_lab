# Flag and Tag Store Across Four Set Backends

Catalog. A feature-flag service with 200k flags plus a document tagging
pipeline: hash sets for dedup, sorted sets for reporting, bit sets for
dense id ranges, enum sets for permission bits. One project exercises
all four and records where each wins.

Hash lane. Tag dedup over a 1M-ingest stream; membership answers vs a
sorted-list oracle on 50k probes. Resize behavior and load-factor choice
logged with max-bucket stats.

Sorted lane. Flag reporting in key order with range slices for the
admin UI; order verified against a stream sort on every export. Rank
and predecessor spot-checks included.

BitSet lane. Dense user-id sets (ids below 2M) for rollout cohorts;
union/intersect/difference vs HashSet oracle on 200 cohort ops. Memory
per member quoted from heap deltas - the bit set should win by an order
of magnitude on dense ids, and the report shows the density where the
advantage flips.

EnumSet lane. Permission flags as bit vectors over a fixed enum;
all-of/any-of queries checked exhaustively (the domain is small enough
for total coverage).

Cohort drill. Rollout cohort built three ways (hash, sorted, bit set)
with identical membership proofs; export order, query time, and bytes
tabled side by side with a per-density recommendation.

Ship. Four-lane service, drill table, oracle logs. Marks: backend
parity 12, density crossover evidence 10, enum exhaustiveness 8.
## Store extras
- Dedup oracle log kept.
- Export order verified.
- Cohort triple-proof tabled.
- Density flip point posted.
- Enum coverage exhaustive.
- Resize stats logged.
- Member bytes quoted.
- Recommendation dated.
