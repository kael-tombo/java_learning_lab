# Event Sourcing - Theory

## 1. Two Different Things Called "Event Sourcing"

This distinction is the single most useful thing in the lab.

```
  EVENT SOURCING          the event log IS the state. State is a projection.
  EVENT-DRIVEN            events notify other systems. State still lives in
                          a table that is the source of truth.
```

Most systems claiming to be event-sourced are event-*driven*: they write to a
table and publish a notification. That is a perfectly good design, much less
demanding, and it does **not** give you the properties event sourcing is famous
for (temporal queries, guaranteed auditability, rebuild-from-nothing).

Event sourcing means: **you can throw away every projection and rebuild it
from the log, and nothing is lost.** If you cannot state that, you are
event-driven.

## 2. The Core Trade

```
  EVENT SOURCING                        CRUD
  ---------------                       ----
  full history, always                 only current state
  temporal queries: yes                 no
  audit: free                          built separately, expensively
  schema changes: painful              easy
  read performance: projected           direct
  delete/correct: append a correcting   update the row
    event, never mutate
  GDPR erasure: conflicts              easy
```

Every benefit has a cost. The question is which side of this table your domain
lives on. Banking, trading, audit, and anything with a legal record obligation
belongs on the left. A blog post belongs on the right.

## 3. Aggregates: The Unit of Consistency

An **aggregate** is a consistency boundary with an identity that events are
attached to.

```
  aggregate: Account(accountId)
    version: 47
    events:  [AccountOpened, Deposited, Withdrawn, Deposited, ...]
```

Rules that keep this workable:

1. **One aggregate is modified by one transaction at a time**, enforced with
   optimistic concurrency (expected version).
2. **Events reference exactly one aggregate**, and a command may emit events for
   only one aggregate. Cross-aggregate invariants require a saga, not a
   transaction (see lab 07-transactions).
3. **Small aggregates.** A large aggregate is a hotspot and a latency problem.
   If the whole order must be loaded to append one line item, the aggregate is
   too big.
4. **Identity, not equality.** Two events with the same aggregate and version
   are the same event. That is the idempotency mechanism.

## 4. Optimistic Concurrency

The write path is a compare-and-set:

```java
append(aggregateId, expectedVersion, events)
  -> INSERT ... WHERE aggregate_id = ? AND version = expectedVersion
  -> 0 rows affected means someone else won. RETRY with a reloaded aggregate.
```

Why optimistic rather than pessimistic:

- Aggregates are usually low-contention, so retries are rare.
- Pessimistic locking across aggregates means locks in a system where the lock
  boundary is a guess.
- A retry is cheap; a lock held across event appends plus projection updates is
  not.

You must still handle the retry loop, and for high-contention aggregates you
need a documented strategy (shard the aggregate, or accept retries with backoff
and a cap).

## 5. Event Schema Versioning

The log is immutable and permanent, so **old events must remain readable
forever**. Two techniques:

### Upcasting (rewrite on read)

Transform an old event into the current shape at read time:

```java
interface EventUpcaster { Event upcast(Event e); }

// v1: {accountId, amount}
// v2: {accountId, amountMinor, currency}
```

You never mutate stored events; you interpret them. Upcasting works well while
the number of old versions is small.

### Tolerant Readers (widen on read)

Consumers accept both shapes:

```java
long amountMinor = e.has("amountMinor") ? e.getLong("amountMinor")
                                        : toMinor(e.getDecimal("amount"));
```

This is more robust than upcasting because it does not require a central
transform that must be updated for every consumer. In practice most systems
converge on tolerant readers for additive changes and upcasting for renames and
semantic changes.

**Event types must be additive.** Removing a field from an event means every
historical event still has it — you cannot delete data that is the source of
truth. Every field is forever `null`-able or defaulted.

## 6. Projections: Where Reads Come From

A projection consumes the log and maintains a read model.

```
  Event log  ->  Projector  ->  Read model (SQL table / doc store / cache)
```

Three flavours:

- **Synchronous**: update the read model in the same transaction as the append.
  Simple, immediately consistent, and it couples the write path to the read
  model's schema — which reintroduces the coupling event sourcing was meant to
  remove.
- **Asynchronous**: append, publish, project. Decoupled, eventually consistent,
  and the usual choice.
- **Rebuildable**: delete the read model and replay. This is the property that
  justifies the complexity, and it is only available if the projection is
  **deterministic**.

### Determinism Is the Requirement

A projection must be a pure function of the event stream. No `now()`, no
random, no reads of external mutable state. Otherwise a rebuild produces a
different answer and you have lost the guarantee.

```java
// WRONG: embeds the processing time
event.setProcessedAt(Instant.now());

// RIGHT: the event already carries its own timestamp
event.occurredAt();   // set when the event was created
```
Timestamps for projections must come from the event, not the projector. Store
the projection's own metadata (processed version, processed at) separately from
the projected values, so a rebuild can overwrite it.

### Rebuild Strategy: Blue-Green

Never rebuild the live read model in place. You cannot serve correct results
while it is half-rebuilt.

```
1. Create projection_v2 (new table/index, empty)
2. Replay the entire log into projection_v2
3. Verify against the live projection (diff must be empty)
4. Atomically switch reads to projection_v2
5. Retain projection_v1 for rollback for one release
```
This is also how you deploy a **projection schema change** safely: the change is
a new projection, not a migration of the old one.

### Checkpointing

A projection records how far it has processed, so a restart resumes rather than
replaying everything:

```
checkpoint = (last_global_offset, last_event_id, projection_version)
```
A checkpoint without an offset is useless for a shared log. Checkpoints must be
written atomically with the projection batch, or a crash leaves them inconsistent
with the data.

## 7. Snapshots and Compaction

A snapshot is a materialised state at a version, stored to avoid replaying the
whole log:

```java
record Snapshot(AccountId id, long version, long balanceMinor, Instant takenAt) {}
```

Load path: load the latest snapshot, then replay events after its version.

**Snapshots are a cache, not the source of truth.** If a snapshot is corrupt,
delete it and replay. If you cannot rebuild a snapshot from the log, you have
made the snapshot authoritative — which breaks the whole design.

Sizing (see `MATH_FOUNDATION.md`): snapshot when the log exceeds a multiple of
the state size. Snapshot too often and you pay serialisation repeatedly; too
rarely and restarts and rebuilds are slow.

**Compaction**: once events are older than the retention you need for replay,
they can be archived. Be precise about what compaction means: for an auditable
system you almost never delete events, you move them to cold storage.

## 8. Temporal Queries

The capability that justifies the pattern:

```
  balance(accountId, at: Instant)   <- "what did they have then?"
```

This requires **effective dating** on events and a query that walks to a point
in time. It is impossible in a CRUD system without keeping the history
separately, and impossible in most event-driven systems because the events were
only notifications.

This is the strongest single argument for event sourcing, and it is worth
leading with when justifying the complexity.

## 9. Operational Discipline

### Poison Messages
A projection that cannot handle an event stalls. Requirements:
- Route unhandleable events to a dead-letter view **with the payload and the
  reason**.
- Alert on projection lag, not on error rate.
- A manual replay path per event.

### Replay Safety
Rebuilding a projection re-runs all the side effects. Projections must be
**idempotent** and must not emit external side effects during replay. If a
projection sends emails, a rebuild sends them all again. Emit side effects from
the log *separately*, with their own dedup.

### Schema Registry
Every event type has a registered schema. Publishing a new event type or a
breaking field change requires registering the version, because consumers you
did not know about will read it.

## 10. When NOT to Use Event Sourcing

- You cannot answer "what did this look like last March?" for anyone.
- The data is genuinely mutable and corrections are normal.
- You need the query flexibility of SQL across arbitrary dimensions — projections
  are fixed shapes, and every new query is a new projection.
- GDPR erasure must physically remove data and you cannot retain an immutable
  log. (See §11.)
- The team cannot operate a replay. Rebuild is the safety net; without the
  ability to use it, you have lost the benefit.

## 11. GDPR Erasure vs. Immutability

The genuine conflict, which is not solvable by wishing:

```
  Event log: immutable, retained indefinitely (audit requirement)
  GDPR:      personal data must be erased on request
```

Resolution options, in order of practicality:

1. **Separate identity from personal data.** Store `customerRef` in events;
   personal data lives in a mutable store keyed by `customerRef`. Erasure
   deletes the personal data; events remain valid and auditable because they
   never contained it.
2. **Crypto-shredding**: encrypt personal fields with a per-customer key held
   elsewhere. Erasure deletes the key. Events remain; content is unreadable.
3. **Exemptions**: some jurisdictions allow erasure with a documented lawful
   basis for financial records. Get this in writing from legal, not from
   engineering.

Option 1 is the design decision that prevents the conflict, and it must be made
at the start. Retrofitting it means rewriting history.

## Summary

Event sourcing buys temporal queries, guaranteed audit, and rebuild-from-log.
It costs schema-evolution pain, read-latency engineering, and operational
discipline. It is right when the domain is a ledger of things that happened, and
wrong when the domain is a mutable current-state document. If you choose it,
the three non-negotiables are: **effective-dated events**, **deterministic
projections**, and **a tested rebuild**.