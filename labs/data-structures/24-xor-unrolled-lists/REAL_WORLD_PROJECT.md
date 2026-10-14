# Embedded Event Log on XOR and Unrolled Lists

Constraint. A sensor gateway with a hard memory ceiling keeps a
100k-entry event log and a small text buffer for local display. Pointer
overhead is the enemy: classic doubly-linked nodes spend more on links
than payload, so XOR linking and unrolled blocks split the job.

XOR lane. Nodes store link = prev XOR next with traversal by carrying
the previous address; memory per node drops to one link field. The
writeup states the traversal rule precisely and the test walks both
directions over 20k nodes comparing against an ArrayList oracle.

Unrolled lane. Blocks of 64 entries with a valid-count per block;
inserts shift within a block, splits cascade at most one block deep.
Cache behavior is the headline: timed sequential scan vs a pointer
chased list at 500k entries, with the measured gap published.

Text-buffer caller. Rope-lite editing over unrolled blocks: middle
inserts and deletes benchmarked against StringBuilder shifting and a
naive linked buffer at 1 MB of text. Winners quoted per operation mix,
no sweeping claims.

Safety register. XOR traversal from a stale handle (guard fails loudly),
unrolled block overflow policy (split, never silent drop), empty-log
edge ops, single-element reversal correctness.

Comparison close. Bytes per entry for all three representations from
heap deltas, scan timings, edit timings, and a paragraph naming the
workload where each lane wins. Weighting: oracle parity 12, memory plus
cache evidence 10, edge handling 8.
## Memory card
- Bytes per entry, all three lanes.
- Block size 64 stays default.
- Scan gap re-measured per release.
- XOR walk oracle always on.
- Stale-handle guard tested.
