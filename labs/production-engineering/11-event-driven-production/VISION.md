# VISION — Lab 11: Event-Driven Architecture & Kafka in Production

> From "we publish events" to "every message is accounted for, ordered correctly, and nobody loses data."

---

## The Arc

1. **The log as a primitive** — partitions, offsets, the leader/ISR, retention, and what Kafka does *not* guarantee.
2. **Producer correctness** — `acks`, idempotence, retries, in-flight requests, batching, and the configuration that is actually safe.
3. **Consumer correctness** — commit discipline, poll intervals, rebalances, static membership, pause-and-persist.
4. **Delivery semantics** — at-most-once vs at-least-once vs exactly-once, and what Kafka transactions genuinely cover.
5. **The dual-write problem** — transactional outbox, CDC relay, and why the relay still forces consumer idempotency.
6. **Idempotency as a discipline** — dedup keys, bounded TTLs, check-and-insert in the same transaction.
7. **Schemas as contracts** — registry, compatibility levels, safe change, deprecate-don't-delete.
8. **Failure paths** — poison messages, DLT content and alerting, retry classification.
9. **Operations** — lag, retention sizing, hot partitions, partition expansion, cost of fan-out.
10. **Process patterns** — sagas, choreography vs orchestration, projections and rebuildability.

---

## Why this lab exists

Event-driven systems move failure from a stack trace into a queue. That is often better — but the failure now happens asynchronously, at a different service, at a different time, with less context. The data-loss modes (unpublished events, expired backlog, permanently blocked partition, DLT nobody reads) are quiet.

The specific goal here: **you can design an event pipeline with an explicit delivery guarantee, prove it under failure, and size retention so that a one-hour outage loses no data.**

---

## Milestones (checkable)

- [ ] M1: For a real event flow, state the delivery guarantee per edge and justify it (at-least-once plus idempotency, or exactly-once with its scope named).
- [ ] M2: Implement a transactional outbox relay and demonstrate the dual-write problem it removes, plus its at-least-once behaviour.
- [ ] M3: Build an idempotent consumer with a bounded dedup TTL and prove no double effect under rebalance, retry, and relay-crash injection.
- [ ] M4: Reproduce a rebalance storm (lag growing, CPU idle) and fix it with three different configurations, showing the arithmetic for each.
- [ ] M5: Produce a poison-message failure, verify the DLT record contains everything needed to reproduce it, and alert on rate rather than depth.
- [ ] M6: Compute retention from `max_tolerable_outage × rate × safety` and demonstrate silent data loss with a shorter retention.
- [ ] M7: Run a Schema Registry compatibility check and reject a set of real "harmless-looking" breaking changes.

---

## Anti-Goals

- `enable.auto.commit=true` for anything that matters.
- Producer without `acks=all` and idempotence.
- `max.poll.records` raised without checking `max.poll.interval.ms`.
- Infinite retries on a poison message.
- A DLT that receives only the bare message.
- Alerting on absolute lag only.
- Retention set by habit rather than by outage tolerance.
- Adding partitions without considering the ordering break.
- Assuming exactly-once covers a database write.

---

## Interview Lens

- "How do you guarantee an event is not lost between the DB and the broker?"
- "Why are our consumers in a rebalance loop?"
- "What does exactly-once mean here, precisely?"
- "How big should retention be?"
- "What happens when a message cannot be processed?"

---

## 30-Day Plan

- **Week 1** — THEORY: log model, producer/consumer configs, delivery semantics, outbox; hands-on with a single-node cluster, `kafka-consumer-groups`, `kafka-run-class` tools. M1–M2.
- **Week 2** — EXERCISES: lag/retention math, poll-interval arithmetic, schema compatibility; QUIZ to 13/15; FLASHCARDS daily. M3–M4.
- **Week 3** — MINI_PROJECT: full pipeline with outbox, idempotent consumer, DLT, registry, and failure injection. M5–M7.
- **Week 4** — REAL_WORLD_PROJECT war story; produce an event-driven design review for a real flow; teach-back: "our delivery guarantees, defended" in 10 minutes.

---

## Artifacts you should be able to show

1. A delivery-semantics table for every edge of a real event flow, with the idempotency key specified.
2. A retention calculation with the outage tolerance it implies.
3. A rebalance-storm reproduction with the before/after poll-cycle arithmetic.
4. A DLT record and the alerting policy that catches problems in minutes, not hours.
5. A schema-compatibility matrix for a real event set, with a rejected breaking change.

---

## Done = You Can

- Say precisely what guarantee a pipeline provides and where it stops.
- Diagnose "lag growing, CPU idle" in under five minutes.
- Size retention from an SLO rather than from habit.
- Design a DLT you can actually debug from.
- Explain why a schema change is or is not safe for the consumers you do not control.
