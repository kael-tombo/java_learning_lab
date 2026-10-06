# Lab 17: Data Architecture & Migration Patterns — Flashcards

~60 cards. Most answers are a rule, a statement, or a sequence.

---

## Migration safety

Q: The four questions for any migration?
A: What lock does it take, for how long? Is it backward-compatible with the currently deployed code? Is rollback available? What is the backfill rate and duration?

Q: `lock_timeout` — why always?
A: Without it a slow DDL queues every subsequent query behind it, exhausting connection pools and turning a 5-minute lock into a total outage. With it, the migration fails in seconds, visibly, and can be retried off-peak.

Q: `statement_timeout` — why also?
A: A backfill or `VALIDATE` that will not finish in time should abort rather than run for hours. Set it deliberately (e.g. 30 s for DDL, longer for a chunked job).

Q: Expand-and-contract sequence?
A: add → dual-write → backfill → switch reads → (release boundary) → drop old.

Q: `RENAME COLUMN` — fast or safe?
A: Fast (metadata-only in PostgreSQL) but never safe during a rolling update: old pods break instantly and rollback is impossible. Use add + switch + drop instead.

Q: Add-column forms, ranked by safety?
A: 1) nullable, no default — instant, metadata-only. 2) nullable with a constant default — usually metadata-only, verify for your version. 3) `NOT NULL DEFAULT` — may rewrite and lock. 4) volatile default (a function) — rewrites.

Q: `CREATE INDEX CONCURRENTLY` — caveats?
A: Cannot run inside a transaction block; does two table scans; a failure leaves an `INVALID` index that must be dropped and rebuilt.

Q: `NOT VALID` + `VALIDATE CONSTRAINT`?
A: Adds the constraint without scanning (brief lock), then validates with a scan that permits writes. The standard large-table trick.

Q: Backfill batching?
A: ~1,000–10,000 rows per transaction, a pause between batches, ordered by an indexed key so it is resumable, and rate-limited against replica lag.

Q: Backfill resumability?
A: Record the last processed key (or a high-water mark) so a crash restarts from there rather than from zero. Bounded batches also bound the transaction length.

Q: Replica lag guard?
A: The backfill generates WAL like any write; if the replica cannot keep up, lag grows unboundedly and reads from the replica go stale. Pause when lag exceeds a threshold.

Q: Is a big backfill ever a release step?
A: Only if the computed duration is minutes. `rows / (batch/cycle)` decides: a 400M-row table at 2,000 rows/s is 55 hours — a project, not a migration.

---

## Expand/contract in code

Q: Dual-write without a dual-write problem?
A: Do not write to two systems in one transaction. Use the outbox: record the intent in the same DB transaction, publish asynchronously (Lab 11).

Q: Read-old/write-both, then switch reads — order?
A: Write both first, then switch reads, then stop writing the old shape only after the rollback window. Switching reads before the dual-write lands is a data-loss bug.

Q: Compatibility matrix for a rollout?
A: At every moment, the schema must satisfy: the version being deployed to (new), the version still serving (old), and the version that a rollback would deploy. If any cell is invalid, the migration is not safe.

Q: How do you know when it is safe to drop the old column?
A: When the previous version is no longer deployable — i.e. the rollback window has closed and every running pod is on the new version. Record that as a date in the migration plan, not as a judgement call.

---

## Schema design

Q: Surrogate key vs natural key?
A: Surrogate (UUID/sequence) as the primary key: immutable, compact, joinable. Keep natural keys as unique constraints. Note UUIDv4 index locality — random UUIDs fragment B-tree indexes; UUIDv7/time-ordered or a sequence is often better for write-heavy tables.

Q: `TIMESTAMPTZ` not `TIMESTAMP`?
A: `TIMESTAMP WITHOUT TIME ZONE` loses the offset and silently misinterprets across regions. Store UTC.

Q: `NUMERIC` for money, or `BIGINT` minor units?
A: `BIGINT` minor units avoids floating-point error entirely and is what most payment systems use. `NUMERIC` is fine but slower and bulkier. Never `FLOAT`/`DOUBLE` for money.

Q: Enum vs lookup table vs check constraint?
A: A native enum alters require DDL to add values; a lookup table is flexible but needs a join; a `CHECK` on a text column with a documented allowed set is a pragmatic middle. Whatever you pick, adding a value must be backward compatible for readers.

Q: `NULL` semantics and partial indexes?
A: Use partial indexes for the queries you actually run (`WHERE status = 'PENDING'`), and be deliberate about whether `NULL` means "absent" or "unknown".

Q: Row width and `TOAST`?
A: Wide rows (blobs, large JSON) push data to out-of-line storage, adding a second read on every access. Move large attributes to a side table. This is the classic vertical-partitioning win.

Q: JSONB: when?
A: For genuinely variable, rarely-queried attributes. Not for anything you filter, sort, or aggregate on — and not as an escape from modelling, because indexes on JSONB expressions are a maintenance burden.

---

## Consistency

Q: What is eventual consistency's contract?
A: A *bounded* staleness window, written down and enforced with a freshness metric. "Eventually" is not a contract.

Q: Where it is acceptable?
A: Derived views, search indexes, recommendation feeds, analytics, notifications, dashboards.

Q: Where it is not?
A: Balance/availability checks, authorisation, inventory reservation, uniqueness enforcement, anything a user will immediately dispute or that money depends on.

Q: Read-your-writes for a user who just posted?
A: Requires either synchronous writes to the read model, a sticky read to the primary, or a "pending" overlay applied client-side until the projection catches up. Pick one; the default (silently stale) is the worst option.

Q. Transactional outbox vs dual write?
A: Outbox for a DB plus a broker. For a DB plus a search index, either an outbox plus an indexer, or an outbox plus a change-data-capture connector.

Q: Two-phase commit across services?
A: Almost never. Use sagas with compensating actions and accept that "exactly once across systems" is not available; get effective-once with idempotency.

---

## CQRS

Q: CQRS buys?
A: Read models shaped for queries, independently indexed, precomputed, and independently scalable; complex reports without hurting the write path.

Q: CQRS costs?
A: Two stores, eventual consistency, projection lag, a rebuild path, more code, more failure modes, and a data-loss risk if projections diverge silently.

Q: When to adopt?
A: When read and write shapes genuinely diverge (reporting, feeds, complex aggregates), not as a default.

Q: Projection rebuild — is it tested?
A: It must be. "We can replay the log and rebuild the projection" is a claim until you have run it. Schedule it as a test.

Q: Read-model freshness SLO?
A: Define it (`p99 projection lag < 5 s`), measure it, and alert on it. Without a freshness metric, staleness is invisible.

---

## Event sourcing

Q: What event sourcing obligates you to?
A: Events are the source of truth: every change is an event, schemas must be upcastable forever, state is a projection, all reads are projection queries, and deletion/erasure becomes a hard problem.

Q: Upcasting vs versioning?
A: Versioning (new event types per change) keeps the write path clean. Upcasting (transform old events on read) keeps one type and pays a cost on every read. Upcasting is the usual choice; dead-letter/ignore unknown events silently is the wrong one.

Q: Snapshots — why?
A: Replaying a long stream per read is O(events). A snapshot every N events makes replay O(N), at the cost of snapshot management.

Q: Is event sourcing required for an audit log?
A: No. An append-only audit table with a hash chain gives you tamper evidence without the state-model obligations. Choose the smaller commitment.

Q: GDPR erasure with an immutable log?
A: Cryptographic erasure (per-subject key deleted) or store PII by reference; otherwise erasure is impossible without rewriting history.

---

## Sharding & partitioning

Q: Choosing a shard key?
A: From the dominant query and the tenancy model: co-locate a query's rows on one shard. Tenant id for B2B, aggregate id for aggregates.

Q: What sharding costs?
A: Cross-shard joins and aggregates, global uniqueness, non-atomic multi-shard transactions, rebalancing with data movement, and per-shard capacity planning.

Q: Global uniqueness with sharding?
A: A separate uniqueness service, a global index table on one shard, or application-assigned ids. Pick one deliberately; "it is fine because ids are UUIDs" is only true if the id is globally unique by construction.

Q: Native partitioning by time — why?
A: Retention becomes `DROP PARTITION` (instant, no bloat) instead of a long `DELETE`, and queries with a time predicate prune partitions. Best first move for a growing append-only table.

Q: Partition pruning requires?
A: The partition key in the predicate (or a constraint the planner can prove). A `WHERE` on a non-key column scans all partitions.

Q: Rebalancing a sharded cluster?
A: Reshard with a dual-write + backfill + cutover (the same expand-contract pattern applied to a whole shard), or use a system that supports online resharding. There is no shortcut.

---

## Archival & lifecycle

Q: Retention tiers for data?
A: Hot (recent, fast storage) → warm (compressed) → cold (object storage) → expired, driven by a lifecycle policy rather than manual `DELETE`s.

Q: Why `DROP PARTITION` over `DELETE`?
A: `DELETE` leaves dead tuples, bloats the table, and generates WAL; dropping a partition is a metadata operation and reclaims space immediately.

Q: Legal hold vs erasure?
A: A legal hold can require retaining data subject to an erasure request. That conflict must be resolved by policy, and the decision must be documented — not discovered.

Q: Backups vs erasure?
A: Backups usually retain data under legitimate interest or statutory retention. Document the position, the maximum retention, and the deletion process for expired backups.

---

## Numbers and defaults to memorize

Q: `lock_timeout` default in a migration?
A: Set it explicitly — 1–5 s is typical. Never leave it unset.

Q: Backfill batch size?
A: 1,000–10,000 rows per transaction, tuned so each transaction is well under a second and the pause keeps replica lag flat.

Q: Rollback window before dropping a column?
A: Longer than the maximum plausible rollback (typically ≥ 30 days), plus the time to get a new release out (a day or two). Compute it, do not guess.

Q: Projection freshness SLO?
A: Usually seconds for interactive, minutes for analytics; measure and alert.

Q: Projection lag alert?
A: `p99(now − max(event_timestamp))` per projection, per consumer group. Also alert when lag exceeds the data-retention horizon (silent loss).

Q: Retention for online events?
A: `max_tolerable_outage × peak_rate × safety` — the same rule as Lab 11.

Q: Partition interval for an append-only table?
A: Monthly or weekly, chosen so partitions are small enough to scan and large enough to avoid planning overhead.

Q: UUID type for a write-heavy table?
A: Time-ordered (UUIDv7) or a sequence — random v4 fragments indexes and inflates write amplification.

Q: Money type?
A: `BIGINT` minor units, or `NUMERIC` with an explicit scale. Never floating point.

Q: Backfill duration calculation?
A: `rows / (batch_size / (transaction_time + pause))`. Compute before writing the migration.
