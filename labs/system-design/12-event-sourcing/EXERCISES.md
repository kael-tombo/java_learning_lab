# Event Sourcing - Exercises

Twelve exercises ordered by difficulty. Solutions follow.

---

## Exercise 1: Event Sourced or Event Driven? (Easy)

A system stores `account.balance` in a table (source of truth) and publishes
`AccountUpdated` to Kafka. Consumers update a search index and send emails.

Which pattern is this? Can you rebuild the search index from the log?

<details>
<summary>Solution</summary>

**Event-driven, not event-sourced.** The table is the source of truth; the
events are notifications. You **cannot** rebuild the search index from the log:
the log contains only balance-change notifications, not account openings,
closures, corrections, or the currency — so a rebuild produces an incomplete,
incorrect index.

The test is precise: *delete every projection and rebuild from the log; is
anything lost?* Here, yes.
</details>

---

## Exercise 2: Storage Growth (Easy)

1.2M events/day, 400 B/event compact binary, 1.4x index/WAL overhead. What is
storage for 90 days and for 3 years?

<details>
<summary>Solution</summary>

Per day: `1.2M * 400 * 1.4 = 672 MB/day`

- **90 days**: `672 MB * 90 = 60.5 GB`
- **3 years (1,095 days)**: `672 MB * 1,095 = 736 GB ≈ 0.72 TB`

Now the interesting comparison: JSON with field names averages 350-600 B, so
moving to compact binary roughly halves the bill — and on a 3-year retention
that is a real, recurring saving. Schema efficiency is a cost lever, not a
detail.

Also note: compression helps at rest (3-6x) but does **not** reduce working-set
size, so it does not help projection rebuild time or query latency.
</details>

---

## Exercise 3: Temporal Query Feasibility (Easy)

Can you answer "balance of account A on 14 March last year"? What index makes
it fast?

<details>
<summary>Solution</summary>

Yes — **this is the capability that justifies event sourcing**, and it is
impossible in a CRUD system unless you separately keep history.

The index that makes it real: `(aggregate_id, version)` or
`(aggregate_id, effective_at)`. Without it, the query is a full table scan —
technically possible, practically unusable.

Cost: seek plus a scan of the events in the account's history up to that date.
At ~6 events/account/day, a year back is ~2,200 events — trivial.

Bonus: order by `version`, **never** by timestamp. Clocks are unsynchronised and
NTP steps reorder events.
</details>

---

## Exercise 4: Optimistic Concurrency (Medium)

An account receives 500 withdrawals/s. Each append reloads the aggregate (2 ms).
Estimate the conflict rate and propose fixes.

<details>
<summary>Solution</summary>

`conflict_rate = 1 - e^(-r * t_reload) = 1 - e^(-500 * 0.002) = 1 - e^-1 = 63%`

63% of appends conflict and must retry. Expected attempts for 95% success:
`ln(0.05)/ln(1-0.63) = 3.0/1.0 = 3` — but wasted work is 63% of all appends.

Fixes, in order:

1. **Shard the aggregate** (e.g. one sub-aggregate per statement line) — reduces
   `r` proportionally.
2. Give the hot aggregate its own log partition.
3. Cap retries with backoff and jitter, and document the aggregate as hot.
4. If it is fundamentally a counter (a balance), move it to a dedicated
   compare-and-set store and emit an event asynchronously.

**Do not** solve it with retries. Above roughly 100 writes/s the aggregate
boundary is wrong.
</details>

---

## Exercise 5: Snapshot Trigger (Medium)

Aggregate: 50,000 events, 2 KB snapshot. Replay costs 50 µs/event, serialisation
2 ns/byte. How often should you snapshot?

<details>
<summary>Solution</summary>

Using the working rule: **snapshot when log bytes since the last snapshot exceed
K times the state size** (K ~ 1-4).

`n_trigger = K * S / bytes_per_event = 2 * 2000 / 400 = 10 events`

That is very frequent, and the cost model in `MATH_FOUNDATION.md` explains why:
for this aggregate, replay per event (50 µs) is ~25x more expensive than
serialising the whole 2 KB snapshot (4 µs), so the maths genuinely favours
frequent snapshots.

Practical form: for a **hot** aggregate, every 10-50 events is reasonable. For a
**cold** one (a few events per month), never snapshot at all. The
`log_bytes > K * state_bytes` rule self-tunes, so use it and measure rather than
tuning a constant.
</details>

---

## Exercise 6: Determinism (Medium)

A projector writes `last_seen_at = Instant.now()` into a read model and computes
`interest = balance * 0.05 * (now - openedAt)`. What breaks on a rebuild?

<details>
<summary>Solution</summary>

Two failures:

1. **`last_seen_at` changes on every rebuild.** The rebuilt read model differs
   from the live one, so the verification diff never comes back empty — which
   means you can never safely cut over a new projection.

2. **Interest recomputed against the rebuild time.** A rebuild tomorrow produces
   different interest for every account than the live projection did today. The
   read model silently becomes wrong.

Fix: projections must be a pure function of the stream. Projected values come
from event fields (`occurred_at`, amounts, rates). Time-varying business logic
(interest accrual) must be modelled as a **scheduled event** (`InterestAccrued`)
so it is in the log and therefore reproducible.

Projection metadata (`processed_at`, checkpoint) is stored separately and is
explicitly allowed to change.
</details>

---

## Exercise 7: Upcast or Tolerant Reader? (Medium)

You rename `amount` to `amountMinor` in `Deposited`, changing its type from
decimal to long. Which technique, and why?

<details>
<summary>Solution</summary>

**Upcaster**, because this is a rename plus a *type change*, and it is
semantically meaningful (`"125.50"` -> `12550`).

A tolerant reader is acceptable for additive fields but here every consumer must
convert, and doing it in every consumer means N copies of a conversion rule that
will drift.

Upcasting means interpreting old events into the current shape at read time. The
stored events are never mutated — you rewrite on read. When v1 events age out,
delete the upcaster.

Practical note: for the **aggregate** (which must not silently ignore unknown
shapes) a strict upcaster is safer. For **read projections** a tolerant reader
is more robust because it needs no central transform.
</details>

---

## Exercise 8: Projection Rebuild Time (Hard)

1.75B events retained, 400 events/s projector, 40 parallel projectors. How long
does a full rebuild take? What are the options?

<details>
<summary>Solution</summary>

Single-threaded: `1.75e9 / 400 = 4.375M s = 50.6 days`
40 parallel: `4.375M / 40 = 109,375 s = 30.4 hours`

**30 hours.** Options, in order of preference:

1. **Snapshot-seeded rebuild.** `n_aggregates * (snapshot_load + tail_replay)`.
   With 200k accounts and a snapshot every 100 events (avg tail 50):
   `200k * (20µs + 50*50µs) = 8.4 minutes` — a **35x** improvement. This is the
   single biggest lever, and it only works because snapshots are deterministic
   state at a known version.
2. **Reduce retained events** (archive aggressively) — but check the
   audit requirement first.
3. **Faster projector** — batching, a compact format, parallel partitioning.
4. **Fewer full rebuilds** — blue-green so rebuilds happen only on schema
   change, not on every deploy.

Feasibility gate: if rebuild cannot complete inside a tolerable window, the
design must change. Decide this before committing, not after.
</details>

---

## Exercise 9: Schema Change Deployment (Hard)

You need to add `currency` to a projection and split one table into three. How do
you deploy this without downtime?

<details>
<summary>Solution</summary>

**Never migrate the projection. Build a new one.** Blue-green:

```
1. Create projection_v2 (three new tables, new projector code)
2. Rebuild v2 from the FULL log into the empty tables
3. Verify v2 against the live projection (diff must be EMPTY)
4. Atomically switch reads to v2
5. Retain v1 for rollback for one full release
6. Drop v1
```

This is safe because the projection is a pure function of the log, so v2 is
reproducible from scratch — which is the payoff for accepting event sourcing's
schema pain in the first place.

Watch out for: read amplification (each new projection is a separate rebuild —
five query shapes means 5x), and verification that is genuinely exhaustive rather
than a row-count comparison (row counts match while the contents differ).
</details>

---

## Exercise 10: GDPR Erasure (Hard)

A bank must keep 7-year audit history (immutable) but erase customer PII on
request. Reconcile this.

<details>
<summary>Solution</summary>

The conflict is real: you cannot delete from an immutable log.

**Resolution: never put erasable PII in the log.** Design events to carry
`customerRef`, not `name`, `email`, or `address`:

```
events:   {accountId, customerRef: "cus_8823", amountMinor: 5000}
personal: {customerRef: "cus_8823", name, email, address}   <- mutable store
```

On an erasure request: delete from the personal-data store. Events remain valid
and auditable, and every read joins the personal store — which is usually
acceptable, and which is the cost you accept.

Alternatives if a schema change is impossible:
- **Crypto-shredding**: encrypt PII fields with a per-customer key held
  separately; erasure deletes the key. Events remain; content is unreadable.
- **Documented lawful basis** for financial records, obtained in writing from
  legal — an engineering decision cannot substitute for this.

The key insight: this must be decided at design time. Retrofitting means
rewriting history.
</details>

---

## Exercise 11: Poison Event (Medium)

A projection throws on one malformed event and stops. The read model is now
permanently stale for everything after it. Design the fix.

<details>
<summary>Solution</summary>

Four requirements:

1. **Never let one event stop the stream.** Wrap each `apply` in a try/catch;
   route failures to a dead-letter record with the payload, the reason, and the
   aggregate and version.
2. **Track and expose lag per projection.** Alert on **lag**, not on error rate.
   A projector running perfectly but 9 minutes behind is broken, and its error
   rate is zero. Lag is the metric that catches this.
3. **Manual resolution path**: list dead-lettered events, fix the projector,
   replay from the checkpoint. Replaying from a checkpoint means the projector
   must be idempotent, which is why versioned upserts beat deltas.
4. **Fail loudly at write time where possible**: an aggregate should reject a
   command that would produce an unprojectable event, rather than accepting an
   event that only breaks a reader later.

Also: a malformed event in the log is a **data integrity incident**, not a
consumer bug. Investigate how it got in.
</details>

---

## Exercise 12: Design Review (Hard)

A team proposes event sourcing for a blog. Write the review.

<details>
<summary>Solution</summary>

**Reject.** The domain does not justify it.

1. **No temporal requirement.** Nobody asks "what did this post look like in
   2021?". That is the primary capability, and it is absent.
2. **Audit is not required.** Posts are mutable. Corrections and edits are
   normal, and event sourcing's append-only corrections are worse for this.
3. **Query flexibility is high.** Blogs are queried by arbitrary dimensions —
   author, tag, date range, full-text, popularity. Projections are fixed shapes,
   so every new query is a new projection plus a rebuild. That is a
   disproportionate cost here.
4. **Replay has side-effect risk.** A "notify subscribers" projection re-sends
   every notification on rebuild. This is the operational hazard that eats the
   benefit.
5. **Read performance is the priority** and event sourcing means reads come from
   a projection you now have to build and maintain.
6. **The complexity is not free** and a blog team should spend it on the product.

Better fit for a blog: a relational database with version history on the posts
table (cheap, gives "as of" for the entity that needs it), a search index, and
events only as notifications.
</details>