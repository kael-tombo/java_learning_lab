# Distributed Messaging - Vision

## The Big Picture
Messaging decouples services in time, and time is where the bugs live. A message broker
gives you at-least-once delivery, ordering within a partition, and a durable log — and in
exchange it gives you duplicate processing, head-of-line blocking, and consumer lag.

## Why This Matters
Every asynchronous architecture eventually has a consumer that must be idempotent, a
partition count that must be chosen deliberately, and a retry policy that must distinguish
"the service is down" from "the message is poison." These are design decisions made in code
long after the broker was chosen.

## The Vision for This Lab
This lab goes beneath the client API. You will implement the broker mechanics — partitioning,
offset commit, consumer groups, rebalancing, and at-least-once semantics — then build the
consumer patterns that make those semantics survivable: idempotency keys, DLQs, and lag as a
first-class signal.

## Learning Philosophy
1. **At-least-once is the only real promise** — design every consumer to be replayed
2. **Ordering is scoped to a key** — the partition is the unit of order, not the topic
3. **Offsets are the unit of correctness** — commit means "I finished", nothing else
4. **Lag is a business metric** — seconds of lag is seconds of stale decisions

## Future Path
- 18-distributed-queues — queue semantics: priority, delay, dead-letter
- 04-distributed-transactions — the outbox lives on this transport
- 13-kafka-consumer-lag-incident — a production lag incident end to end

## Success Metrics
You have mastered messaging when you can:
- [ ] Implement consumer groups with correct rebalancing and offset commits
- [ ] Build an idempotent consumer and prove replay is harmless
- [ ] Choose a partition count from throughput and key-affinity requirements
- [ ] Diagnose consumer lag from lag-per-partition shape

## The Distributed Mindset
> A queue is a promise that work will happen eventually. It says nothing about how many times,
in what order relative to your other consumers, or how long you may stare at it before the
business notices. You own all three.