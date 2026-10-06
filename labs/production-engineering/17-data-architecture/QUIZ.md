# Lab 17: Data Architecture & Migration Patterns — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. What is the expand-and-contract pattern, and why does it exist?**
- A) A way to rename columns quickly
- B) A multi-release sequence that keeps the schema valid for both the currently deployed code and the previous version: add the new shape → dual-write → backfill → switch reads → drop the old shape in a *later* release after the rollback window closes
- C) A migration tool
- D) A backup strategy

**Answer: B** — It exists because during a rolling update both code versions run, and a rollback may redeploy the old version after the migration is applied. The schema must satisfy both, in both directions, for the whole window.

---

**Q2. What is the exact danger of renaming a column in one migration?**
- A) None, `RENAME COLUMN` is atomic
- B) The rename is atomic but the *meaning* is not: the old code fails immediately with `column does not exist` on any pod that has not yet restarted, and rollback redeploys code that cannot read the new name. It converts a deploy into an outage with no safe rollback
- C) It takes a table lock
- D) The index is dropped

**Answer: B** — `RENAME COLUMN` in PostgreSQL is metadata-only (fast) and still unsafe. Fast is not the same as safe.

---

**Q3. Why is a `NOT NULL DEFAULT` column on a large table risky?**
- A) It is always safe
- B) On a rewrite-requiring form it takes an `ACCESS EXCLUSIVE` lock for the duration of the rewrite; queries queue behind it, and pooled connections all block, so the app times out in seconds while the DDL runs for minutes. Nullable without a default is metadata-only and instant
- C) It cannot be indexed
- D) It requires a trigger

**Answer: B** — The safe default is: add nullable, backfill in batches, then add the `NOT NULL` constraint in a separate step (which can use a `NOT VALID` check constraint plus `VALIDATE CONSTRAINT` to avoid the scan lock). Always set `lock_timeout` so a lock failure is fast and visible rather than a silent pile-up.

---

**Q4. What is the dual-write problem, and what does it do to a transaction?**
- A) It doubles write throughput
- B) Writing to two systems (a DB and a broker, or a DB and a search index) in one logical operation has no shared atomicity: one succeeds and the other fails. It forces the transaction to span systems, which means holding the DB transaction open across a network call — longer locks, replication lag, and pool pressure
- C) It is required for sharding
- D) It improves consistency

**Answer: B** — The outbox pattern removes it by writing the intent in the same DB transaction and publishing asynchronously.

---

**Q5. What is the correct way to add an index on a large table in production?**
- A) `CREATE INDEX` in the migration
- B) Concurrently (`CREATE INDEX CONCURRENTLY` in PostgreSQL, online DDL elsewhere), outside a transaction, with a statement timeout, followed by a check for an invalid index left behind by a failure. It takes two table scans but does not block writes
- C) Add it after the release, manually
- D) Use a hash index

**Answer: B** — Two caveats worth knowing: it cannot run inside a transaction block, and a failed concurrent build leaves an `INVALID` index that must be dropped and rebuilt.

---

**Q6. What is the problem with a long-running backfill, and what are the mitigations?**
- A) It only affects performance
- B) One transaction over hundreds of millions of rows holds locks, bloats WAL, and starves replication. Mitigate: batch it (1,000–10,000 rows per transaction), pause between batches, rate-limit against replica apply lag, run it outside the release, and make it resumable (record the last processed key)
- C) It cannot be interrupted
- D) It locks the table

**Answer: B** — And compute whether the duration is acceptable at all: at a chosen batch size and cycle time, a 400M-row table can be 50+ hours, which makes it a project, not a migration.

---

**Q7. What does `NOT VALID` + `VALIDATE CONSTRAINT` buy you?**
- A) Nothing
- B) It lets you add a `CHECK`/`NOT NULL` constraint without scanning the table (taking only a brief lock), then validate it with a scan that holds only a `SHARE UPDATE EXCLUSIVE` lock — so writes continue. A plain `ADD CONSTRAINT` blocks writes for the whole scan
- C) It skips validation entirely
- D) It only works on partitioned tables

**Answer: B** — The two-phase constraint pattern is the standard trick for large tables in PostgreSQL. Verify availability in your database version.

---

**Q8. What is CQRS, and what does it buy and cost?**
- A) A pattern to avoid a database
- B) Separate write and read models, so reads can be shaped for queries (denormalised, indexed, precomputed) and scaled independently. Cost: two stores to keep consistent, eventual consistency, a projection/rebuild path, and more operational surface
- C) A caching strategy
- D) A partitioning scheme

**Answer: B** — Adopt it where the read and write shapes genuinely diverge; do not adopt it as a default, because the consistency window is a real product decision.

---

**Q9. What is the actual obligation you take on with event sourcing?**
- A) Better auditability, free of charge
- B) The event log becomes the source of truth, so: every state change must be expressible as an event; schemas must be upcastable forever; projections must be rebuildable; "what is the current state?" becomes a query over projections; and deleting data becomes a hard problem (GDPR erasure versus immutable log)
- C) Faster queries
- D) No schema changes needed

**Answer: B** — Those obligations are permanent. The auditability benefit is real but it is not the whole price.

---

**Q10. When is eventual consistency acceptable?**
- A) Never
- B) When the user-visible workflow tolerates a bounded staleness window and the business has agreed to it: derived views, search indexes, recommendation feeds, analytics, notifications. Not acceptable for: balance checks, authorisation decisions, inventory reservation, uniqueness enforcement, anything a user will immediately dispute
- C) Only for analytics
- D) Only in microservices

**Answer: B** — Write the bound down (e.g. "search results may be up to 30 s stale") and enforce it with a freshness metric, or it becomes an unbounded, undocumented staleness.

---

**Q11. How do you shard, and what breaks when you do?**
- A) By table
- B) By a shard key chosen for access patterns (usually the tenant or aggregate id), so that a query touches one shard. What breaks: cross-shard queries (joins, aggregates) become scatter-gathers, unique constraints span shards (you need a global uniqueness service), transactions spanning shards are not atomic, rebalancing requires data movement, and per-shard capacity planning replaces global planning
- C) By row
- D) By index

**Answer: B** — Choose the shard key from the dominant query and the tenancy model, and be honest that you are trading the ability to ask arbitrary questions.

---

**Q12. What is the difference between vertical and horizontal partitioning, and when do you use each?**
- A) They are the same
- B) Vertical partitioning = split columns across tables (moving blobs/JSON out of the hot table); horizontal partitioning = split *rows* (native partitioning by time/tenant/hash). Vertical reduces row width and cache pressure on the hot path; horizontal is for retention, isolation, and scale
- C) Vertical is for reads
- D) Horizontal is deprecated

**Answer: B** — Native time partitioning plus a retention/drop-partition policy is the cheapest answer to a growing append-only table, and it beats deleting rows.

---

**Q13. How do you handle GDPR erasure in an append-only or event-sourced design?**
- A) Delete the rows
- B) Cryptographic erasure (encrypt PII with a per-subject key, delete the key), plus soft-delete/tombstones in operational stores, plus propagation to caches, search indexes, replicas, and analytics — with a documented position on backups, where erasure is usually deferred under legitimate interest or legal retention
- C) Ignore it, data is anonymised anyway
- D) Ask the user to opt out

**Answer: B** — The design decision must be made when the schema is created, because retrofitting erasure into an immutable log is painful.

---

**Q14. What is a zero-downtime migration's rollback story, and when does it not exist?**
- A) Roll back by running the migration in reverse
- B) Rollback means redeploying the previous application version against the current schema. That is available only while the previous version can read the new schema. It does not exist once you have dropped a column, irreversibly transformed data, changed an event contract consumers read, or changed a uniqueness constraint's implementation
- C) Rollback is always possible
- D) Rollback means restoring the backup

**Answer: B** — Deciding the rollback story *before* writing the migration is the discipline. Expand-contract exists to keep it available for as long as you might need it.

---

**Q15. The single most common cause of a migration-caused outage is?**
- A) A typo in the SQL
- B) A migration that takes a lock or rewrites the table, combined with no `lock_timeout` and no rollback plan — so a slow DDL silently queues every query in the application
- C) Running out of disk
- D) A missing index

**Answer: B** — The fix is procedural and cheap: `lock_timeout` on every migration, expand-contract for anything shape-changing, and a review step that computes the lock duration from the table size.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and migrate a real schema safely.
- 12–10: revisit expand-contract, lock behaviour, and backfill mechanics; redo EXERCISES 2–5.
- <10: re-read THEORY + `RAFT_CONSENSUS_ENGINE` cold and retake in 48 hours.
