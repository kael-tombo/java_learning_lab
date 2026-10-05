# Distributed Queues - Vision

## The Big Picture
A work queue is a promise that work will eventually be done, exactly usefully, and not
twice. Distributed queues add durability, visibility timeouts, and horizontal consumers — and
with them the hard questions of ordering, deduplication, and what to do with the message that
will never succeed.

## Why This Matters
Queues are where every system defers work and forgets about it. Backlog growth, poison
messages, visibility-timeout expiry, and redelivery storms are all queue bugs, and all of
them show up as silent failure rather than errors.

## The Vision for This Lab
This lab builds a durable queue from first principles — visibility timeouts, dead-letter
queues, deduplication, and priority — because the semantics are what you must reason about.
Then it puts the semantics under a failure injection and measures what survives.

## Learning Philosophy
1. Visibility timeout is a lease on a message, not a lock
2. At-least-once means the consumer must be idempotent; no exceptions
3. A poison message must have a terminal path, not infinite retries
4. Ordering is per key, and a DLQ break in ordering is a design decision

## Future Path
- 06-distributed-messaging — brokers, streams, and consumer groups
- 04-distributed-transactions — the outbox depends on durable delivery
- 13-kafka-consumer-lag-incident — queues failing under real load

## Success Metrics
You have mastered distributed queues when you can:
- [ ] Implement visibility timeout with redelivery and count
2. Prove a crash mid-processing redelivers rather than loses
- [ ] Build a DLQ with a replay path that preserves idempotency
- [ ] Choose per-queue delivery guarantees from the consumer's idempotency

## The Distributed Mindset
> A queue is where work goes to be forgotten. Every message you enqueue is a promise that
someone will eventually own the failure. Decide now what "eventually" means and what happens
when it never happens.