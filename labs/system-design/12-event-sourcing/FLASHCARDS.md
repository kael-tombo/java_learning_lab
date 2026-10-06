# Event Sourcing - Flashcards

60 review cards.

## Front: What is event sourcing?
**Back:** The event log IS the state. Current state is a projection computed from it, and the log is the authoritative source.

## Front: What is event-driven architecture?
**Back:** Events notify other systems while state still lives in a table that remains the source of truth.

## Front: What is the single test distinguishing event sourcing from event-driven?
**Back:** Delete every projection and rebuild from the log. If anything is lost, you are event-driven, not event sourced.

## Front: What is an aggregate?
**Back:** A consistency boundary with an identity that events attach to. It enforces invariants and emits events; it does not store state durably.

## Front: What is an aggregate's responsibility?
**Back:** Validate a command against current state and emit the events that should happen. Not: perform I/O, call other aggregates, or persist.

## Front: Why does an aggregate record events rather than mutate itself?
**Back:** Separating decision from persistence means there is no hidden state anywhere except in the events, which is what makes rebuild work.

## Front: What does event sourcing buy you that CRUD cannot give?
**Back:** Temporal queries ("balance as of date"), guaranteed audit trail, and rebuild from the log.

## Front: What does event sourcing cost?
**Back:** Painful schema evolution, read-latency engineering, operational discipline, and a genuine conflict with GDPR erasure.

## Front: When should you NOT use event sourcing?
**Back:** Mutable data with no temporal or audit requirement, high query flexibility across arbitrary dimensions, and no ability to operate a rebuild.

## Front: What is optimistic concurrency in event sourcing?
**Back:** append(aggregateId, expectedVersion, events) as a compare-and-set. Zero rows affected means conflict; rehydrate and retry.

## Front: Why optimistic rather than pessimistic locking?
**Back:** Aggregates are low-contention so retries are cheap, and a lock held across appends plus projection dispatch reintroduces the coupling you removed.

## Front: At what rate does an aggregate become a contention problem?
**Back:** Around 100 writes/s. Above that, sharding the aggregate is the fix; more retries just wastes work.

## Front: What is the conflict rate formula?
**Back:** conflict_rate = 1 - e^(-r * t_reload), a Poisson approximation. 500 writes/s with a 2 ms reload gives ~63% conflict rate.

## Front: Why must old events remain readable forever?
**Back:** The log is the source of truth and is retained indefinitely for audit, regulation, and temporal queries. Year-one events must still be interpretable in year five.

## Front: What is an upcaster?
**Back:** Rewriting an old event into the current shape at read time. You interpret, never mutate — stored events are immutable.

## Front: When to upcast versus tolerant-read?
**Back:** Upcast renames and semantic/type changes. Tolerant-read additive fields, because it needs no central transform and cannot drift.

## Front: Why can an event schema never remove a field?
**Back:** Historical events still carry it and a rebuild must interpret them identically. Every field is forever-optional; fields are only added.

## Front: What must a projection be?
**Back:** A pure, deterministic function of the event stream. Same events in, same read model out, regardless of when or how many times.

## Front: Why must projections be deterministic?
**Back:** Rebuild, verification, and cutover all depend on reproducing the read model. Non-determinism makes the verification diff meaningless.

## Front: What breaks if a projection calls Instant.now()?
**Back:** The rebuilt model never matches the live model, so no projection change can be cut over safely, and time-varying logic silently diverges.

## Front: How do you handle interest accrual in an event-sourced system?
**Back:** Model it as a scheduled event (InterestAccrued) so it is in the log and reproducible. Never compute it from now().

## Front: Where should projection metadata like processed_at go?
**Back:** In separate columns from projected values, so a rebuild can overwrite it without corrupting the projected data.

## Front: What is blue-green projection deployment?
**Back:** Build a second projection, rebuild it, verify the diff is empty, atomically switch reads, then retire the old one after a release window.

## Front: Why is blue-green safer than migrating a projection?
**Back:** The live projection is never partially mutated. A failed rebuild costs nothing and rollback is a config change, not a data restore.

## Front: Why should projections not send emails or call webhooks?
**Back:** A rebuild re-runs the whole log, so all side effects re-fire — 1.2M old notifications. Emit side effects from a separate consumer with its own dedup.

## Front: What is the required index for temporal queries?
**Back:** (aggregate_id, version) or (aggregate_id, effective_at). Without it the query is a full table scan — technically possible, practically useless.

## Front: Should events be ordered by timestamp or by version?
**Back:** By version. Clocks are unsynchronised and NTP steps reorder events; version is the store's own total order.

## Front: What are occurred_at and recorded_at?
**Back:** occurred_at is when the business event happened (set by the writer); recorded_at is when it was appended. Prefer version for ordering.

## Front: What is a snapshot, and what is it not?
**Back:** Materialised state at a version, used to avoid replaying. It is a CACHE, never the source of truth — if it is corrupt, delete it and replay.

## Front: What is the working rule for snapshot frequency?
**Back:** Snapshot when log bytes since the last snapshot exceed K times the state size (K ~ 1-4). Simple, self-tuning, directionally correct.

## Front: When should you snapshot a hot aggregate?
**Back:** Frequently — every 10-50 events can be reasonable. Replay per event (~50 us) is often 25x more expensive than serialising a whole snapshot.

## Front: How much does snapshot-seeding speed up a rebuild?
**Back:** Roughly 35x: ~30 hours from genesis drops to ~8 minutes with a snapshot per 100 events. The biggest single lever.

## Front: What is the feasibility gate for event sourcing?
**Back:** Rebuild time must fit a tolerable window. 30 hours is acceptable quarterly; 30 days is not and the design must change.

## Front: What is read amplification in event sourcing?
**Back:** Each read shape is a separate projection and a separate rebuild. Five projections means five times the rebuild cost.

## Front: Which metric do you alert on for a lagging projection?
**Back:** Projection lag (offset between the log end and the checkpoint). Error rate is zero for a projector that is perfectly running but 9 minutes behind.

## Front: How is projection lag computed?
**Back:** lag = backlog_events / projector_throughput. After a 1-hour broker outage at 60 events/s with 400 events/s throughput, lag is ~9 minutes.

## Front: Should projector capacity be sized on average or peak?
**Back:** Peak. If sized at average, a 3x peak outruns capacity and lag grows without bound until read models are visibly wrong.

## Front: What is a poison event?
**Back:** One the projector cannot handle. It must not stop the stream: catch per apply, route to a dead-letter with payload and reason, alert on lag.

## Front: What belongs in a dead-letter record?
**Back:** The full payload, the failure reason, the aggregate id and version, and the projector version. Enough to fix and replay it.

## Front: Why must projections be idempotent?
**Back:** Redelivery and replay both re-apply events. Versioned upserts are naturally idempotent; delta-style updates ("balance += x") double-apply.

## Front: How does event sourcing conflict with GDPR erasure?
**Back:** The log is immutable and retained indefinitely; erasure demands deletion. You cannot satisfy both with PII in the log.

## Front: What is the resolution for the GDPR conflict?
**Back:** Never put erasable PII in events. Events carry customerRef; personal data lives in a separate mutable store. Erasure deletes from that store.

## Front: What is crypto-shredding?
**Back:** Encrypt PII fields with a per-customer key held in a separate boundary. Erasure deletes the key, so events remain but content is unreadable.

## Front: When must the GDPR decision be made?
**Back:** At design time. Retrofitting means rewriting history, which an immutable log by definition does not allow.

## Front: What are the three storage cost levers, in order?
**Back:** (1) encoding efficiency — compact binary roughly halves storage and rebuild I/O; (2) retention policy — the dominant term; (3) projection shape count.

## Front: Does storage compression help rebuild time?
**Back:** No. It reduces cost at rest (3-6x) but not working-set size, so rebuild time and query latency are unaffected.

## Front: How much storage for 1.2M events/day at 400 B with 1.4x overhead?
**Back:** 672 MB/day, so 60 GB for 90 days and ~0.72 TB for 3 years. JSON with field names would be roughly double.

## Front: What partitions the event log?
**Back:** aggregate_id, which gives per-aggregate ordering and scales writes linearly. A global sequence is a hotspot that buys nothing.

## Front: How is causal ordering across aggregates achieved?
**Back:** Commands carry the expected version of every aggregate they touch, so any concurrent change fails the precondition and the caller retries coherently.

## Front: What is a concurrency conflict exception and how do you handle it?
**Back:** The UNIQUE (aggregate_id, version) constraint fired. Cap retries at 5-8 with backoff and jitter, then return 409 — more retries is not the fix.

## Front: What should happen when an aggregate rehydrates and finds a version gap?
**Back:** Fail loudly. A silently skipped event produces a balance that is wrong forever and cannot be detected later.

## Front: Why must business rules live in the aggregate rather than the store?
**Back:** A replay re-validates every historical decision. Rules in the store mean the rules were never checked for past events.

## Front: How do corrections work in an event-sourced system?
**Back:** As a new appended event (CorrectionApplied). You never edit history, even to fix a mistake.

## Front: What is the difference between synchronous and asynchronous projections?
**Back:** Synchronous updates the read model in the same transaction as the append (immediately consistent, but couples write path to read schema). Async appends then projects.

## Front: Why is asynchronous projection the usual choice?
**Back:** It decouples the write path from the read model's schema, which is the coupling event sourcing exists to remove, and it allows multiple independent projections.

## Front: What must a checkpoint record?
**Back:** Last processed event id/offset, processed count, and projector version — written atomically with the projection batch or a crash desynchronises them.

## Front: Why is partitioning by aggregate_id the right log partition key?
**Back:** It gives per-aggregate total order, distributes hot and cold aggregates, and makes hot-aggregate isolation possible. Ordering by time would not.

## Front: What is the relationship between read projections and a business transaction?
**Back:** They are separate. A cross-aggregate business transaction is a saga (see lab 07-transactions); projections are pure reads of the log.

## Front: What is the single most important property of an event-sourced system?
**Back:** That the projection is rebuildable from the log. Everything else — audit, temporal queries, blue-green deploys — depends on it.

## Front: What is the test for whether your projection is truly rebuildable?
**Back:** Delete the read model entirely, rebuild from the log, and diff against the previous state. The diff must be empty, verified routinely, not assumed once.