# Distributed ID Generation - Vision

## The Big Picture
A distributed ID generator must hand out unique, roughly ordered identifiers across nodes
that cannot coordinate cheaply. Each design trades monotonicity, size, and coordination cost
against a different failure mode — and most real incidents come from ignoring clock skew.

## Why This Matters
IDs leak into URLs, database keys, and external contracts. Changing scheme is a breaking
migration. And the specific bug everyone hits once is a Snowflake ID generator whose clock
went backwards, producing duplicates that only appear under load.

## The Vision for This Lab
This lab compares the four real options — database sequences, UUID variants, Snowflake-style
bit allocation, and ULID/UUIDv7 — on the axes that matter: uniqueness proof, sortability,
index locality, and behaviour under clock skew and worker exhaustion.

## Learning Philosophy
1. Uniqueness is a claim you must be able to defend
2. Monotonicity is about indexes, not about the ID looking nice
3. Never generate IDs from wall-clock time without a monotonicity guard
4. Coordinate only when you must — coordination is the dependency you are trying to avoid

## Future Path
- 10-time-ordering — logical clocks as an alternative ordering source
- 08-partitioning-sharding — ID schemes that embed the shard key
- 17-distributed-filesystems — content-addressed IDs and their guarantees

## Success Metrics
You have mastered ID generation when you can:
- [ ] Implement Snowflake and UUIDv7 with clock-skew protection
- [ ] Explain why random UUIDv4 fragments B-tree inserts
- [ ] Prove uniqueness at 10M IDs/sec across 64 workers
- [ ] Recover safely from a backwards clock jump

## The Distributed Mindset
> An ID is a claim about uniqueness that the rest of your system will trust for years.
Choose the scheme whose failure mode you would rather debug, and handle backwards clocks
explicitly rather than hoping they never happen.