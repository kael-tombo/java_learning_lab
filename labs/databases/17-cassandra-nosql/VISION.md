# Cassandra NoSQL — Vision

## Where this points
Grow from first queries toward dependable judgment about partition layout and replica agreement, measured by artifacts rather than hours studied.

## Capabilities gained
- Command of partition design turns on-call database surprises into routine checklist work.
- Concretely: the partition key decides which nodes store each telemetry row.
- Concretely: wide rows cluster time-ordered readings inside one partition.

## Sequence
1. Foundations: the mini project gets reproduced after clearing the schema.
2. Depth: extend one item (the partition-key design keeping one device-day per partition) until a reviewer asks for simplification.
3. Production: real-world milestones delivered, restore drill documented.

## Honest assessment
- Strong after this lab: reasoning about node placement, since row ownership follows from the partition key.
- Strong after this lab: applying the quorum-overlap rule when reviewing replica expectations.
- Still fragile: hot partitions from a too-coarse device key remains the most likely incident for beginners.
- Still fragile: unbounded partitions growing until reads choke still needs a senior eye on the bucket design.

## Anti-patterns to drop
- Reproduce a snippet's results before adopting it anywhere.
- Stop skipping the telemetry row-count reconciliation after each key change.
- Stop treating the QUORUM write walkthrough on a three-replica sketch as optional when the review depends on it.

## Out of scope
- This lab does not cover Cassandra server version numbers and release claims; treat those as separate tracks.
- It also skips compaction-strategy tuning specifics, which belong to operations tracks.
- Deliberately omitted: invented benchmarks, version trivia, borrowed view names.

## Checkable milestones
- [ ] Rebuild the seed schema on a blank host from memory.
- [ ] Explain the clustering-order sketch sorting readings by timestamp to a peer without notes.
- [ ] Trigger consistency confusion when QUORUM expectations go unstated in staging, and recover using the runbook.
- [ ] Say where partition design ends and Cassandra server version numbers and release claims begin in a design review.

## Study guidance
Follow the items in sequence, keep scripts rerunnable, and respect the non-coverage boundary stated above.
