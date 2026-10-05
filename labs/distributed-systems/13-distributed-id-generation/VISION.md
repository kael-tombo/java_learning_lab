# Distributed ID Generation (Deep) - Vision

## The Big Picture
Deep ID generation is a bit-allocation problem with a safety argument attached. Every scheme
spends its bits on three things: *when*, *where*, and *which* — and the choices are not
interchangeable. Time bits buy ordering, location bits buy coordination-free uniqueness at
the cost of exhaustion, and randomness buys both safety and index damage.

## Why This Matters
IDs are the one field every component depends on and no one designs carefully. They end up
in cache keys, in distributed-trace baggage, in database B-trees, and in URLs customers
bookmark. A bad ID scheme is discovered through all four at once.

## The Vision for This Lab
This lab works the bit budget explicitly. You will implement UUIDv7, ULID, K-sortable IDs,
and a Snowflake variant, then measure the two things that actually decide the choice:
collision probability at scale and index write amplification.

## Learning Philosophy
1. Draw the bit layout before writing the code — always
2. Clock safety is a first-class feature, not an error branch
3. Uniqueness claims must be arithmetic: state the failure probability
4. Random IDs tax every index they touch; pay that cost consciously

## Future Path
- 10-time-ordering — HLC-style monotonic counters inside ID layouts
- 08-partitioning-sharding — embedding the shard key in the ID
- 12-time-ordering — K-ordering and database-specific ID types

## Success Metrics
You have mastered deep ID generation when you can:
- [ ] Derive the collision probability for a given bit budget and rate
- [ ] Implement UUIDv7 and ULID with monotonic increment and overflow handling
- [ ] Measure index write amplification for random vs sequential keys
- [ ] Recover from a backwards clock without generating duplicates

## The Distributed Mindset
> An ID generator is a distributed system's only globally unique object. Spend bits on the
guarantee you need, spend none on the ones you do not, and make the clock assumption explicit
in the name of the class.