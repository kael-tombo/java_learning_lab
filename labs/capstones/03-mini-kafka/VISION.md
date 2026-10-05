# VISION — Mini Kafka Capstone

> Build a log that keeps its promises: durability, ordering, consumer groups,
> and a replication story you can explain at the whiteboard.

## Why this capstone

Kafka's design is a small number of ideas applied consistently: a log, a
partition key, an offset, and a group. Building it makes the trade-offs
concrete in a way that using it never will — you feel the cost of replication,
the cost of rebalances, and the cost of ordering.

## The Arc

1. **Log** — segments, offsets, retention, compaction.
2. **Replication** — leaders, followers, ISR, acks, and what durability means.
3. **Groups** — assignment, rebalances, offsets, and exactly-once boundary.
4. **Delivery** — producer retries, idempotence, consumer commit strategy.
5. **Operate** — lag, under-replicated partitions, disk, and the failure drills.

## Milestones (checkable)
- [ ] M1: implement append, read by offset, and segment rollover with retention.
- [ ] M2: implement leader election and ISR tracking, and demonstrate a follower lag.
- [ ] M3: implement a consumer group with rebalance on membership change, and measure its cost.
- [ ] M4: demonstrate at-least-once end to end, then add idempotence to remove duplicates.
- [ ] M5: run four failure drills and write the runbook from what actually happened.

## Anti-Goals
- A single-node "cluster" with no replication story.
- Offsets committed after processing with no re-delivery test.
- Claiming exactly-once with a sink that does not cooperate.

## Interview Lens
- "What does `acks=all` actually guarantee?"
- "Why did my consumer reprocess 4 hours of data?"
- "How do you move a key to a different partition?"

## 30-Day Plan
- Wk1 log + segments + retention. Wk2 replication + ISR + failover.
- Wk3 consumer groups + rebalances. Wk4 failure drills and the runbook.

## Done = You Can
- Explain durability, ordering, and delivery in terms of the mechanism, and
  predict the behaviour of any configuration.
