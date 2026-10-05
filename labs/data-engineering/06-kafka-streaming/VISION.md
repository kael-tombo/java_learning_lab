# VISION — Kafka Streaming: Durable Log as Backbone
> Where this lab takes you: from "send JSON over HTTP" to designing topics,
> keys, partitions, and consumer groups you can operate at 3am.

## The Arc
1. **Log** — records, offsets, segments, retention.
2. **Topics** — partitions, keys, ordering scope, throughput math.
3. **Producers** — acks, idempotence, batching, back-pressure.
4. **Consumers** — groups, rebalances, lag, commit strategy.
5. **Evolve** — schemas, replay, compaction, dead-letter.

## Milestones (checkable)
- [ ] M1: compute required partitions from throughput, batch size, and replication.
- [ ] M2: explain exactly what a rebalance costs and how `assign` avoids it.
- [ ] M3: build a producer that is idempotent and survives broker restart mid-batch.
- [ ] M4: write a replay tool that rebuilds a downstream table from offset 0.
- [ ] M5: define a topic naming and partitioning standard and defend it in review.

## Anti-Goals
- Assuming more partitions is free; it multiplies replication and file handles.
- Manual offset commits that skip records on crash.
- One topic per event type with an unbounded JSON payload schema.

## Interview Lens
- "Ordering guarantee across two topics?" (answer: none, without a design)
- "Consumer lag is 2M and climbing. Where do you look first?"
- "How do you move a key to a different partition after a bug?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT with a real producer/consumer pair.
- Wk3 add replay, compaction, and a schema registry check. Wk4 REAL_WORLD_PROJECT.

## Done = You Can
- Size, name, partition, and troubleshoot a Kafka estate like an operator.
