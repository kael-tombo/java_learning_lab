# Event Sourcing - Quiz

15 questions. Answer before checking the key.

---

## Section A: Foundations (Q1-5)

**Q1.** What is the difference between event sourcing and event-driven architecture?

**Q2.** What is the single test that distinguishes them?

**Q3.** What is an aggregate, and what is it responsible for?

**Q4.** Why does an aggregate *record* events rather than mutate its own state?

**Q5.** Why is optimistic concurrency usually preferable to locking for event-sourced aggregates?

---

## Section B: Schema and Storage (Q6-9)

**Q6.** Why must old events remain readable forever, and what technique bridges old shapes?

**Q7.** When should you use upcasting versus tolerant readers?

**Q8.** Why can an event-sourced schema never have a field removed?

**Q9.** Your event log grows 672 MB/day. What are the three cost levers, in order of impact?

---

## Section C: Projections (Q10-12)

**Q10.** What does it mean for a projection to be deterministic, and why is it required?

**Q11.** A projection calls `Instant.now()`. What breaks?

**Q12.** Why should projections not emit external side effects like emails?

---

## Section D: Operations (Q13-15)

**Q13.** What is blue-green projection deployment and why is it safer than migrating?

**Q14.** Which metric should you alert on for a lagging projection, and why is error rate wrong?

**Q15.** Reconcile an immutable audit log with a GDPR erasure request.

---

## Answer Key

**A1.** **Event sourcing** means the event log *is* the state, and current state
is a projection computed from it. **Event-driven** means events notify other
systems while state still lives in a table that remains the source of truth. The
confusion is common because most systems doing the latter describe themselves
with the former's vocabulary.

**A2.** *Delete every projection and rebuild it from the log — is anything lost?*
If yes, you are event-driven. The test is exact: a system where the log contains
only "balance changed" notifications, with no account-opened, closed, or
corrected events, cannot rebuild its search index. It has lost information, and
the information lives in the table.

**A3.** An aggregate is a **consistency boundary with an identity that events
attach to** — `Account(accountId)` with a version and a sequence of events. Its
responsibilities are narrow: enforce business invariants, validate a command
against current state, and emit the events that should happen. It is explicitly
**not** responsible for storing state durably, invoking other aggregates, or
performing I/O beyond the store's append.

**A4.** Separating decision from persistence is what makes a rebuild work: there
is no hidden state anywhere except in the events. If the aggregate mutated
itself and wrote to storage directly, the state would exist in two places
(the fields and the log), they could diverge, and a replay would produce a
different result. The aggregate decides; the store appends; a projector reads.

**A5.** Three reasons. (1) Aggregates are usually low-contention, so conflicts
are rare and retries cheap. (2) A pessimistic lock here would be held across
event appends *and* projection dispatch, reintroducing exactly the coupling
event sourcing exists to remove. (3) The lock boundary is a guess — you do not
know in advance which aggregates a future command will touch. Optimistic
concurrency confines the failure to the append itself, with a cheap retry.
Above roughly 100 writes/s on one aggregate, however, the boundary is wrong and
should be sharded rather than retried harder.

**A6.** Because the log is the source of truth and it is retained indefinitely —
for audit, regulatory, and temporal-query requirements. So the schema you wrote
in year one must remain interpretable in year five. Upcasting bridges this by
**interpreting** an old event in the current shape at read time (`Deposited`
with `amount: "125.50"` becomes `amountMinor: 12550`), never by mutating the
stored event. Stored events are immutable; only the reader changes.

**A7.** **Upcasting** for renames and semantic or type changes — these are
meaningful and every consumer needs the same conversion, so a single central
transform is better than N drifting copies. **Tolerant readers** for additive
changes — accepting both `amountMinor` if present, otherwise computing from
`amount` — because they need no central transform and cannot drift. In practice
systems converge on tolerant readers for additions and upcasting for renames.
Note the asymmetry: the *aggregate* should upcast strictly (it must not silently
ignore an unknown shape), while a read projection can be tolerant.

**A8.** Because the events are the state and they are immutable and permanent.
Any historical event still carries that field, and a rebuild must interpret it
identically. If the current schema assumed the field was gone, old events would
fail to deserialise or would populate a value that was never present. So every
field is treated as forever-optional: never removed, only added, and always
read defensively. Deleting a field is not a schema change, it is a data
archaeology problem.

**A9.** In order of impact: (1) **encoding efficiency** — moving from JSON with
field names (350-600 B) to a compact binary format with field numbers
(120-250 B) roughly halves both storage and rebuild I/O; (2) **retention
policy** — retention is the dominant term (0.7 TB over 3 years versus 60 GB over
90 days), and archiving must be checked against the audit requirement, not
chosen freely; (3) **projection shape count** — each read model is a separate
table and a separate rebuild, so consolidating projections matters. Note that
storage compression (3-6x) is *not* on this list: it reduces cost at rest but
does not reduce working-set size, so it does not help rebuild time or query
latency.

**B10.** Determinism means a projection is a **pure function of the event
stream**: same events in, same read model out, regardless of when it runs, how
many times, or on which machine. It is required because rebuild, verification,
and cutover all depend on reproducing the current read model from scratch. If a
rebuild differs, you cannot tell whether the difference is a code bug or a real
data bug, so you cannot safely deploy a new projection — and you lose the
verification step that is the entire reason to accept the complexity.

**B11.** Two failures. (1) **Rebuild divergence**: `last_seen_at` changes on
every rebuild, so the rebuilt model never matches the live model, the
verification diff never comes back empty, and no projection change can be safely
cut over. (2) **Time-varying business logic**: any calculation based on `now`
(interest accrual, age-based tiers, expiry) produces different results on
rebuild than on the live path, silently corrupting the read model. Fix:
projected values come only from event fields — use the event's `occurred_at`,
and model time-varying logic as a **scheduled event** (`InterestAccrued`) so it
is in the log and therefore reproducible. Projection metadata such as
`processed_at` is stored separately and is allowed to change.

**B12.** Because a rebuild re-runs the entire log, so a projection that sends
emails or calls webhooks re-sends **all of them** — 1.2M notifications on a
single rebuild, for events that happened three years ago. Recipients act on
those notifications, so this is not just waste; it is a correctness and
reputational incident. Fix: emit side effects from a **separate consumer** of the
same log with its own idempotency key and dedup window, so replaying
projections for a schema change cannot produce external effects. The read model
itself must be a pure projection with no outward behaviour.

**B13.** Blue-green means **building a second projection alongside the live one
rather than migrating the existing one**: create `projection_v2` (new tables,
new projector code), rebuild it from the full log, verify the diff against the
live projection is empty, atomically switch reads, then retain v1 for rollback
for one release. It is safer because the live projection is never in a partial
state — it is never mutated, so a failed rebuild or a bad diff costs nothing
and rollback is a config change rather than a data restoration. It also handles
schema changes that projections are poor at (splitting one table into three)
without any in-place migration.

**B14.** **Projection lag** — the offset between the log's end and the
projector's checkpoint. Error rate is wrong because a projector that is running
perfectly but 9 minutes behind reports **zero** errors while its read model is
visibly stale. From the math: a one-hour broker outage at 60 events/s peak
creates 216,000 events of backlog, which at 400 events/s takes 9 minutes to
clear — during which everything the user sees is out of date and nothing is
failing. Also alert on **DAG (dead-letter) count** and on checkpoint age, and
size capacity on peak rather than average, because lag grows without bound if
the projector cannot keep up.

**B15.** You cannot delete from an immutable log, so the resolution is a
**design-time schema decision**: never put erasable PII in events. Events carry
`customerRef`; name, email, and address live in a separate mutable store keyed
by `customerRef`. An erasure request deletes from that store; events remain
valid, complete, and auditable because they never contained the data, and reads
join to the personal store. Alternatives where the schema cannot change:
**crypto-shredding** (encrypt PII fields with a per-customer key held in a
separate boundary; erasure deletes the key, so events remain but content is
unreadable), or a **documented lawful basis** for financial-record retention,
obtained in writing from legal. The critical point is that this must be decided
before launch — retrofitting it means rewriting history, which an immutable log
by definition does not allow.