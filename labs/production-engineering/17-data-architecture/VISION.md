# VISION — Lab 17: Data Architecture & Migration Patterns

> From "run the migration" to "here is the lock it takes, the rollback it preserves, and the window during which you must not drop anything."

---

## The Arc

1. **The four questions** — lock and duration, backward compatibility, rollback availability, backfill rate. Everything else is detail.
2. **Lock behaviour** — metadata-only versus rewrite DDL, `lock_timeout`, why an outage starts in seconds not minutes.
3. **Expand-and-contract** — the sequence, the compatibility matrix, and the drop date arithmetic.
4. **Indexing and constraints without blocking** — concurrent index builds, `NOT VALID` + `VALIDATE`, and the failure modes.
5. **Backfills as projects** — batching, resumability, replica-lag guards, and computing the duration before you start.
6. **The dual-write problem** — outbox, read-your-writes, and when eventual consistency is acceptable.
7. **CQRS and projections** — what it buys, what it obliges, and the freshness SLO.
8. **Event sourcing obligations** — upcasting, snapshots, rebuildability, and the erasure conflict.
9. **Partitioning and sharding** — vertical and horizontal, retention, and the price of a query that does not fit the key.
10. **Lifecycle, archival, and erasure** — retention tiers, legal hold, and propagating an erasure honestly.

---

## Why this lab exists

The schema is the one thing in a service that cannot be rolled back by redeploying, and the one place where a small mistake is a total outage. Most migration practices are folklore: "add columns nullable", "avoid renames" — correct, but without the mechanism, so they are not applied under pressure.

The specific goal here: **you can take any migration, state its lock and duration, prove it is safe for both deployed code versions, and define the date on which it becomes safe to remove the old shape.**

---

## Milestones (checkable)

- [ ] M1: Take a real service's schema and classify every migration by lock type, duration, and safety; produce the ranked list of dangerous migrations.
- [ ] M2: Migrate a real (or faithfully reproduced 380M-row) table under production-shaped load, demonstrating `lock_timeout` behaviour and zero blocked writes.
- [ ] M3: Run a full expand-contract cycle — add, dual-write, backfill, switch reads, drop — with the compatibility matrix filled in and the drop date computed.
- [ ] M4: Compute a backfill's duration and replica-lag impact before running it, then demonstrate the lag guard pausing the job.
- [ ] M5: Add a constraint to a large table using `NOT VALID` + `VALIDATE`, and measure the difference in blocked writes versus the blocking form.
- [ ] M6: Design a CQRS read model for one real query shape, with the freshness SLO, projection rebuild test, and lag alert.
- [ ] M7: Produce an erasure propagation plan across all data surfaces, with the coverage arithmetic and a statement of what you can honestly claim.

---

## Anti-Goals

- `RENAME COLUMN`, `DROP COLUMN`, or type changes in a release that still runs the old code.
- DDL without `lock_timeout`.
- A single-transaction backfill of hundreds of millions of rows.
- A migration reviewed without a table size and an estimated lock duration.
- Dual-writing to two systems inside one transaction.
- Event sourcing adopted for "the audit trail" without accepting upcasting, snapshots, and rebuild.
- Sharding chosen for headroom rather than for a ceiling actually in the way.
- Answering an erasure request before every surface has confirmed.

---

## Interview Lens

- "How do you rename a column with zero downtime?"
- "What happens when a migration runs longer than expected?"
- "How do you backfill 400 million rows?"
- "When would you use CQRS, and what does it cost?"
- "How do you delete a user's data across twelve systems?"

---

## 30-Day Plan

- **Week 1** — THEORY + ARCHITECTURE_DECISIONS: lock behaviour, expand-contract, rollback window; hands-on with a large table and `lock_timeout`. M1–M2.
- **Week 2** — EXERCISES: lock duration, backfill rate, shard cost, erasure coverage; QUIZ to 13/15; FLASHCARDS daily. M3–M4.
- **Week 3** — MINI_PROJECT: perform the full expand-contract migration, add a read model, and test projection rebuild. M5–M6.
- **Week 4** — REAL_WORLD_PROJECT war story; produce a migration plan for a real schema; teach-back: "our lock budget and our rollback window, defended" in 10 minutes.

---

## Artifacts you should be able to show

1. A migration inventory with lock type, duration estimate, and safety verdict per migration.
2. A load-tested migration with zero blocked writes and the `lock_timeout` demonstration.
3. An expand-contract timeline with the compatibility matrix and the computed drop date.
4. A backfill plan with duration, replica-lag guard, and resumability.
5. A CQRS design with freshness SLO and a tested rebuild path.
6. An erasure propagation plan with coverage arithmetic.

---

## Done = You Can

- State a migration's lock, duration, and rollback story before running it.
- Explain why a fast DDL can still be an unsafe DDL.
- Compute whether a backfill is a release step or a project.
- Decide when eventual consistency is acceptable and write the bound down.
