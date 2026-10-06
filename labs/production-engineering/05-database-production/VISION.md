# VISION — Lab 05: Databases in Production

> From "add an index" to running the database as a capacity- and failure-budgeted production system.

---

## The Arc

1. **Query discipline** — plans, `EXPLAIN (ANALYZE, BUFFERS)`, selectivity, sargable predicates, N+1 elimination.
2. **Index thinking** — when an index pays, covering/partial/function indexes, index-only scans, write cost, bloat.
3. **Transaction & lock literacy** — isolation levels, `FOR UPDATE` without indexes, lock queues, deadlock avoidance, long-transaction poison.
4. **Pool economics** — sizing from Little's Law and the concurrency cliff, `max_connections` budgeting across pods, pgbouncer.
5. **Replication & staleness** — lag math, read-your-own-writes, split-brain, when replicas don't help.
6. **Vacuum, bloat, wraparound** — the maintenance loop most teams forget until it's an emergency.
7. **Safe migrations** — expand-contract, `CONCURRENTLY`, batched backfills, rollback stories.
8. **Operational ownership** — the DB metrics you alert on, backup/restore rehearsal, migration risk budget.

---

## Why this lab exists

The database is the one component where a bad decision is expensive, hard to reverse, and shared by every service. Yet most database knowledge in application teams is "add an index." The specific goal here: **you can look at a service's pool config, transaction boundaries, and migrations and predict whether it will survive peak, a slow report query, or a schema change — before it happens.**

---

## Milestones (checkable)

- [ ] M1: Read an `EXPLAIN (ANALYZE, BUFFERS)` plan and name the estimate-vs-actual mismatch that caused a bad plan.
- [ ] M2: Take a real slow query and fix it with evidence (index, predicate rewrite, or batching), showing the before/after plan and timing.
- [ ] M3: Compute correct pool sizes for a multi-pod service against a `max_connections` budget, and identify when a pooler is mandatory.
- [ ] M4: Reproduce `SELECT ... FOR UPDATE` without an index and observe the full-table lock blocking writers.
- [ ] M5: Explain how a long read transaction causes bloat and then slower queries (the poison loop), and break the loop.
- [ ] M6: Design an expand-contract migration for a 200M-row table and prove no long `ACCESS EXCLUSIVE` lock with `pg_locks` monitoring.
- [ ] M7: Define read-your-own-writes routing for your service and show it working against a deliberately lagged replica.

---

## Anti-Goals

- Increasing pool size to "fix" a latency problem during an incident.
- `SELECT *`, offset pagination, and N+1 queries in hot paths.
- Unbounded transactions or missing `idle_in_transaction_session_timeout`.
- Long blocking migrations during peak traffic with no rehearsal on production-sized data.
- Treating a nightly backup as a recovery plan you never tested with a restore.
- Believing replicas fix read-after-write bugs without solving staleness explicitly.

---

## Interview Lens

- "Your API is slow; the DB CPU is 40%. Where do you look, in order?"
- "How do you size a connection pool for 40 pods?"
- "Why does adding an index sometimes make things slower?"
- "Walk me through a zero-downtime migration of a heavily-read table."
- "A user says their save disappeared. What could cause that, and how do you prevent it?"

---

## 30-Day Plan

- **Week 1** — THEORY on plans, indexes, transactions/locks; hands-on `EXPLAIN (ANALYZE)` on 20 queries. M1–M2.
- **Week 2** — EXERCISES: pool math, lock experiments, bloat/vacuum drills; QUIZ to 13/15; FLASHCARDS daily. M3–M5.
- **Week 3** — MINI_PROJECT: build the migration + pool-sizing + replica-staleness harness. M6–M7.
- **Week 4** — REAL_WORLD_PROJECT war story; produce a runbook and a migration plan for a real table; teach-back: "our database, defended" in 10 minutes.

---

## Artifacts you should be able to show

1. A before/after plan pair with buffers and the diagnosis stated in one sentence.
2. A pool-sizing worksheet across tiers with the `max_connections` budget.
3. A lock-wait experiment transcript showing `FOR UPDATE` without an index.
4. A bloat/vacuum measurement over time with the intervention that helped.
5. A rehearsed expand-contract migration with lock monitoring evidence.
6. A runbook covering pool exhaustion, lock storms, replication lag, and restore.

---

## Done = You Can

- Diagnose a slow query from evidence and explain the fix in planner terms.
- Size pools and reason about total connection budgets across a fleet.
- Design a migration that is safe under peak traffic and has a rollback story.
- Explain, quantitatively, how one bad query becomes a database-wide incident.
