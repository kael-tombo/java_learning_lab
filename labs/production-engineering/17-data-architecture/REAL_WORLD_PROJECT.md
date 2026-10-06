# Lab 17: Data Architecture & Migration Patterns — Real World Project

## Scenario: "The Column We Renamed and the Table We Locked"

You are a principal engineer at a subscription e-commerce platform: 14 Spring Boot 3 services, Java 21, PostgreSQL 14 primary + 2 read replicas, 1.4 TB of data. ~90 engineers, 6 squads.

**The incident** — Wednesday 11:20, a routine release window for `order-service`.

**What happened over 3 days**:

1. **11:20** — `order-service` 4.2.0 deploys, including migration `V31__standardise_amount_columns.sql`, which renames `total_cents` to `amount_minor`. Migration tooling runs it at the start of the rollout, before the pods are replaced.
2. **11:20:40** — Every `order-service` pod still running 4.1.0 fails immediately with `column "total_cents" does not exist`. Error rate goes to 100%. The rollout aborts because pods are not becoming ready.
3. **11:24** — The responder considers rolling back. `kubectl rollout undo` would restore 4.1.0, which also expects `total_cents` — which no longer exists. Rollback would produce the same failure. They do not try it, and instead deploy a hotfix that reads `amount_minor`.
4. **11:58** — Hotfix live. **Total impact: 38 minutes of complete order-creation outage at peak. 1,900 orders lost from the checkout funnel.**
5. **Postmortem finding**: the migration was reviewed by two engineers, both of whom knew "don't rename columns" and neither of whom had the lock-duration arithmetic or the compatibility-matrix habit to make the review meaningful.

**The deeper problem found during the postmortem investigation**:

6. **A second near-miss, two weeks earlier** — `V29__add_status_index.sql` created an index on `orders(status)` without `CONCURRENTLY` on a 380M-row table. It blocked writes for **94 seconds**. Nobody noticed because the deploy was at 02:00 and traffic is 5% of peak at that hour. The same migration in `customer-service` on a 90M-row table would block for **~25 seconds at peak**.
7. A `NOT NULL DEFAULT` migration in `subscription-service` on a 120M-row table holds an `ACCESS EXCLUSIVE` lock for an estimated 3–8 minutes, with no `lock_timeout` set.
8. The `orders` table has 4 concurrent writers (order-service, refund-service, fulfilment-worker, and a data-fix script run by hand). Nobody can enumerate which migrations are safe.

**Your job over 4 weeks**: make schema change a governed, measured, reviewable activity. Build the migration safety standard, implement expand-contract on the real pending changes, add the CI enforcement, and prove the estate can absorb a shape change with zero downtime.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Know your schema risk (Day 1–4)

### 1.1 Schema inventory

For every service: every table, row count, total size, index list, and the number of writers.

**Deliverable 1 — Schema inventory** with the size/row-count table and the multi-writer map (the `orders` four-writer case must be explicit).

### 1.2 Migration inventory and risk classification

Every migration in every service: statement type, lock type, table size, estimated duration, whether it is shape-changing, whether it is safe with the previous code version deployed, and whether rollback remains valid afterwards.

**Deliverable 2 — Migration risk register**, ranked by `duration × impact`, with the top 10 called out. Include the 94-second blocking index and the 3–8 minute constraint as the two headline entries.

### 1.3 Estimate durations from table sizes

Use your database's actual observed rewrite/index-build rates (measure them on a copy of a 50M-row table) rather than a generic constant, and produce a duration estimate per dangerous migration.

**Deliverable 3 — Duration estimates** with the measured per-row rates and the arithmetic shown, so a reviewer can check them in under a minute.

### 1.4 Reconstruct the incident

Timeline, the compatibility failure, the rollback trap (why `rollout undo` would have made it worse), and the queue-growth arithmetic explaining why 38 minutes of impact came from an instant metadata-only rename.

**Deliverable 4 — Causal analysis** with the timeline, the rollback-trap explanation, and the two near-misses.

---

## Phase 2 — Write the standard (Day 4–7)

### 2.1 The four questions every migration must answer

```
1. What lock does it take, and for how long?  (state the number, from the table size)
2. Is it valid for BOTH the currently deployed version and the version a rollback would deploy?
3. Is rollback available after this migration? If not, what is the fix-forward path?
4. What is the backfill rate and duration, and how is replica lag protected?
```

A migration whose review comment answers these four is reviewable in five minutes. One that does not is not.

**Deliverable 5 — Migration review standard** with the template, the four questions, and a worked example of a passing and a failing review.

### 2.2 The required controls

- `SET lock_timeout` and `SET statement_timeout` on every migration; no exceptions.
- Additive-only DDL in a release that still runs the previous code.
- Concurrent index creation, outside a transaction block.
- Constraints added `NOT VALID` then validated.
- Backfills batched, resumable, and rate-limited against replica lag.
- A `REQUIRES-NO-DOWNTIME` marker in the file name or header for anything that may rewrite, forcing explicit review.

**Deliverable 6 — Standard** plus the CI enforcement (Section 4).

### 2.3 The expand-contract procedure for shape changes

A worked procedure with the timeline, the compatibility matrix, the dual-write implementation, and the drop-date arithmetic (`release + max rollback age + time to release a fix`).

**Deliverable 7 — Procedure** with the template migration files and the compatibility matrix template.

---

## Phase 3 — Fix the real migrations (Week 2)

### 3.1 Remediate the top 10 dangerous migrations

For each, one of:
- Rewrite as expand-contract (multi-release).
- Rewrite as concurrent index creation.
- Rewrite as `NOT VALID` + `VALIDATE`.
- Mark as requiring an offline window (if no online form exists), with an approved window and a maintenance-mode plan.

**Deliverable 8 — Remediation PRs** for the top 10, each with before/after lock analysis.

### 3.2 Execute the pending shape change properly

`total_cents`/`currency` → `amount_minor`/`currency_code`, done the expand-contract way:

| Release | Change | Safe with previous version deployed? |
|---|---|---|
| R1 | add nullable columns; dual-write; composite concurrent index | yes |
| — | resumable, lag-guarded backfill | n/a |
| R2 | switch reads; keep dual-write | yes (R1 rollback still valid) |
| — | 30-day window | — |
| R3 | drop old columns | R1 no longer rollback-deployable after this point |

**Deliverable 9 — Completed migration** with: lock measurements during each step, backfill rate and duration versus prediction, replication-lag curve, read-switch verification, and the drop date with its arithmetic.

### 3.3 Add the missing index safely

Replace the blocking `V29` pattern with concurrent creation, and document the `INVALID`-index cleanup procedure.

**Deliverable 10 — Index migration** with the measured difference in blocked writes (0 versus 94 s) and the cleanup runbook.

---

## Phase 4 — Enforce in CI (Week 2)

A migration linter, as a required check on every repository:

1. No migration without `lock_timeout`.
2. No `RENAME COLUMN` / `DROP COLUMN` without an ADR and a `drop_safe_date` comment.
3. No `CREATE INDEX` without `CONCURRENTLY` (outside transaction blocks).
4. No `ADD CONSTRAINT` on a table over a size threshold without `NOT VALID` + `VALIDATE`.
5. No `ADD COLUMN ... NOT NULL DEFAULT <volatile>` on a large table.
6. No single-statement backfill over a row-count threshold.
7. No migration that both changes shape and changes behaviour (must be split).

Each failure names the incident it prevents.

**Deliverable 11 — CI enforcement** blocking eight deliberately bad migrations, each with a specific message, plus the escape hatch (ADR + owner + expiry).

---

## Phase 5 — Data architecture decisions (Week 2–3)

### 5.1 Read/write shape analysis

For the three slowest queries per service, compare the write model to the read model. Where they genuinely diverge, propose a read model (CQRS) with a freshness SLO.

**Deliverable 12 — Read/write analysis** with the divergence matrix and the proposals.

### 5.2 Implement one read model

For the highest-value query, build the projection with:
- the freshness SLO (`p99 projection lag < 5 s`),
- the lag alert, plus the "lag will exceed retention" alert,
- a **tested rebuild path** (full replay from the event log, diffed against the incremental projection, must be zero).

**Deliverable 13 — Read model** with the freshness SLO, both alerts, the measured rebuild time, and the zero-diff verification.

### 5.3 Partitioning decisions

For the three largest append-only/growing tables: evaluate native time partitioning, state the pruning benefit and the cost (queries without a time predicate), and implement partitioning plus a `DROP PARTITION` retention job for the highest-volume one.

**Deliverable 14 — Partitioning plan** with the before/after query timings and the retention job.

### 5.4 Event sourcing: decide, and record the decision

For one bounded context, evaluate event sourcing (audit needs, audit performance) against an append-only audit table with a hash chain. Record the decision as an ADR, including the obligations accepted (upcasting, snapshots, rebuild, erasure).

**Deliverable 15 — ADR** with the trade-off and the obligations, explicitly stating what you are *not* adopting and why.

---

## Phase 6 — Lifecycle, erasure, and capacity (Week 3–4)

### 6.1 Retention and archival

Per table: a retention class (hot / warm / cold / expired), a lifecycle job, and the storage-cost implication.

**Deliverable 16 — Retention policy** with the lifecycle jobs and the projected storage curve.

### 6.2 Erasure propagation

For the personal-data tables: enumerate every surface (primary, replicas, cache, search, analytics, logs, exports, backups), the mechanism and propagation time for each, and the confirmation method. Implement the primary + cache + search paths; document the rest.

**Deliverable 17 — Erasure plan** with per-surface propagation, coverage at 1 h and 24 h, and the honest statement of what can be claimed and when.

### 6.3 Capacity headroom

Table growth forecast (12 months), storage headroom, connection budget per service under HPA scaling, and the sharding/repartitioning threshold at which you would act — with the trigger defined in advance rather than in an incident.

**Deliverable 18 — Data capacity plan** with the forecast, the thresholds, and the trigger conditions.

---

## Phase 7 — Prove it (Week 3–4)

| Scenario | Injection | Success criteria |
|---|---|---|
| S1 | Replay the `RENAME COLUMN` shape change against the platform | blocked in CI before merge |
| S2 | Same change with an ADR and expand-contract | merges; 0 errors throughout; drop date honoured |
| S3 | Blocking index creation on `orders` (380M rows) | blocked writes = 0 (concurrent); completes with no `INVALID` index |
| S4 | `NOT NULL DEFAULT` on a 120M-row table | blocked in CI; `NOT VALID`+`VALIDATE` form has ~0.1 s lock |
| S5 | The backfill run against the 4,000 writes/s load | replica lag stays under threshold; guard pauses when injected |
| S6 | Rollback to the previous version after the backfill | succeeds; data intact in both shapes |
| S7 | Rebuild the read model from the event log | zero diff; rebuild time within budget |
| S8 | Erase one subject end to end | every surface confirms; coverage stated honestly at 1 h and 24 h |
| S9 | A migration with no `lock_timeout` on a table over 1M rows | fails the CI gate with a specific message |
| S10 | Concurrent migrations from two teams on `orders` | the compatibility matrix in review catches the conflict |

**Deliverable 19 — Migration safety test report** with all ten scenarios, measured outcomes, and fixes for anything missed.

---

## Phase 8 — Quantify and institutionalize (Week 4)

| Metric | Before | After |
|---|---|---|
| Shape-changing migrations via rename/drop | ≥ 3 in 12 months | 0 (CI-blocked) |
| Write-blocking DDL | 94 s observed; 3–8 min latent | 0 |
| Migrations with `lock_timeout` | sporadic | 100% (CI-enforced) |
| Migration incidents in 12 months | 3 (1 outage, 2 near-misses) | 0 |
| Duration of the last shape change | 38 min outage | 0 downtime |
| Backfills with a lag guard | 0 | 100% |
| Tables with a retention/partition policy | 12 of 240 | all tables > 10 GB |
| Read models with a tested rebuild | 0 | all read models |
| Erasure requests with full-surface confirmation | unknown | 100% |
| Data capacity forecast | none | 12-month forecast with defined triggers |
| Migration review time | 30+ min of archaeology | 5 min with the four questions answered |

Institutionalize: the four questions become the migration PR template; the linter is a required check in all 14 repositories; shape-changing migrations require a compatibility matrix in the PR description; the data capacity plan is reviewed quarterly; erasure coverage is reported to compliance, not assumed.

**Deliverable 20 — Business case + institutionalization**, including the incident cost ($ figures from your record) against the cost of the standard, the linter, and the read model.

---

## Deliverables checklist

- [ ] Phase 1 schema inventory, migration risk register, duration estimates, causal analysis.
- [ ] Phase 2 migration review standard, controls, expand-contract procedure.
- [ ] Phase 3 remediation of the top 10, completed shape change, safe index creation.
- [ ] Phase 4 CI enforcement blocking eight bad migrations.
- [ ] Phase 5 read/write analysis, one read model with tested rebuild, partitioning plan, event-sourcing ADR.
- [ ] Phase 6 retention policy, erasure plan, data capacity plan.
- [ ] Phase 7 ten-scenario migration safety report.
- [ ] Phase 8 before/after business case + institutionalization.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Diagnosis | "We renamed a column" | Compatibility matrix, rollback trap explained, queue arithmetic, both near-misses found |
| Inventory | "We have four services with big tables" | Row counts, sizes, index lists, the multi-writer map |
| Risk | "Some migrations are risky" | Lock type + duration per migration, ranked by `duration × impact`, durations from measured rates |
| Standard | "Be careful with migrations" | Four questions, required controls, worked example, reviewable in five minutes |
| Execution | "We did expand-contract" | Lock measurements, backfill rate vs prediction, lag curve, drop-date arithmetic, read-switch verification |
| Enforcement | "We review migrations" | Linter with eight rules, specific messages, ADR escape hatch with expiry |
| Architecture | "We added a read model" | Read/write divergence analysis, freshness SLO, tested rebuild with zero diff, event-sourcing ADR with obligations |
| Proof | "We migrated a table" | Replays the incident, blocking DDL, backfill under load, rollback after backfill, rebuild, erasure |
| Sustainability | "We wrote a guide" | PR template, required check in 14 repos, quarterly capacity review, compliance reporting |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **PostgreSQL documentation — `ALTER TABLE`, `CREATE INDEX`, and explicit locking** — https://www.postgresql.org/docs/current/sql-altertable.html and https://www.postgresql.org/docs/current/sql-createindex.html — the authoritative source for which operations take `ACCESS EXCLUSIVE` versus `SHARE UPDATE EXCLUSIVE`, the `CONCURRENTLY` caveat that it "cannot be used inside a transaction block", and the explicit-locking chapter's statement that `ACCESS EXCLUSIVE` conflicts with every other lock mode. These are the primary citations for the lock-duration arithmetic in this lab. **Verify carefully against your specific PostgreSQL version**: whether a given `ADD COLUMN ... DEFAULT` form is metadata-only, which `ALTER COLUMN TYPE` rewrites are binary-coercible, and the exact lock level and duration for `VALIDATE CONSTRAINT` all vary by version, and your incident's 94-second index build and 3–8 minute constraint estimate are only valid for the version and hardware you measured.
2. **Pragmatic Engineer / Martin Fowler — zero-downtime schema-change and expand-and-contract patterns** — https://martinfowler.com/bliki/ParallelChange.html — the canonical description of the parallel-change (expand-and-contract) pattern for schema evolution, including the requirement that "the two schemas can be used simultaneously" during the transition. Use it to justify the four-release sequence and the compatibility-matrix review, rather than asserting it. Also relevant to the general argument that schema and code must be deployed as one coordinated unit, which is exactly what failed in this scenario.

Additional anchors worth verifying: `pg_stat_activity.wait_event_type` and `pg_locks` semantics for measuring blocked queries in your version; `pg_stat_replication` for lag measurement; `pg_stat_user_tables.n_dead_tup` and autovacuum thresholds for the bloat implications of large deletes; whether your migration tool supports per-migration transaction control (needed for `CREATE INDEX CONCURRENTLY`, which cannot run inside a transaction — verify Flyway/Liquibase behaviour and any `executeInTransaction` flag); and your ORM's behaviour on unknown columns (`hibernate.jdbc.time_zone`, schema validation settings) since a renamed column can surface as a mapping error rather than a SQL error.

---

## Reflection questions

1. The rename was metadata-only and therefore instant — yet it caused 38 minutes of outage. What does that tell you about which migrations are actually dangerous, and why is "lock duration" only half the risk?
2. Two engineers reviewed the migration and both knew renames were bad. What would have made the review catch it — a checklist, a tool, or a different default?
3. `rollout undo` would have made things worse. How do you make "rollback is available" a declared property of your schema rather than an assumption?
4. The 94-second blocking index ran at 02:00 with no impact. What is your process for noticing that the same migration would be a serious problem at peak?
5. You have four concurrent writers to `orders`. Who owns that table's schema, and what would you need to change to make that ownership real?
