# Messaging - Vision

## Why This Lab Exists
Moving from "call this service" to "publish that fact" changes the shape of
the entire system: availability becomes asynchronous, delivery becomes
at-least-once, and ordering becomes something you must *buy per key*. Every
producer-side bug found in production came from assuming exactly-once and
in-order delivery. This lab exists to make those assumptions explicit.

## The Mental Model
A queue is a **buffer with a delivery contract**. Choose the contract first:

```
  Producer -> [Topic: partitioned, ordered per key] -> Consumer Group
                       |                              |
                  retention policy              offset / commit
```

- Ordering exists only *within a partition*, and only for one consumer in a
  group at a time.
- "At least once" + idempotent consumer == "effectively once". This is the
  single most important sentence in the lab.

## What You Should Be able To Do
- Pick sync vs. async for a given call, and say what you lose when you go async.
- Design partition keys from ordering requirements, and state the cardinality cost.
- Implement a consumer that is idempotent under redelivery, lag, and rebalance.
- Explain consumer groups, rebalances, and why a poison message stalls a partition.
- Choose between log (Kafka) and queue (SQS/Redis Streams) semantics.
- Describe DLQ strategy: park it, alert, or replay-later.

## The Anti-Goals
- No "fire and forget" without an owner for the dead-letter queue.
- Do not invent global ordering you do not need; it costs partitions and
  latency.
- An async call is not a free decoupling; it moves the failure mode to
  *eventually* and makes it harder to observe.

## Success Criteria
You can specify a topic: partitioning, key, retention, delivery semantics, DLQ,
ordering scope, and the idempotency strategy of every consumer.

## How To Use This Lab
1. `THEORY.md` for delivery semantics and topology.
2. `MATH_FOUNDATION.md` for throughput, lag, backpressure, rebalance cost.
3. `CODE_DEEP_DIVE.md` for a broker, consumer group, and DLQ in Java.
4. `MINI_PROJECT.md` to build a reliable async pipeline.
5. `REAL_WORLD_PROJECT.md` for an event-driven domain integration.
