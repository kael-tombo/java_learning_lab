# Lab 05: Databases in Production — Real World Project

## Scenario: "The checkout outage with a 40-minute diagnosis and a 3-hour fix"

You are the senior engineer on a subscription platform team. Java 21 / Spring Boot / JPA + some JDBC, PostgreSQL 14 primary with one read replica, Kubernetes, 40 pods.

**The incident** — Thursday 14:05: A marketing email triggers a 6x traffic spike (2,400 → ~14,000 req/s peak, not the projected 5,000). Within 8 minutes:

1. `HikariCP` logs `Connection is not available, request timed out after 3000ms`.
2. Checkout `POST` failures climb to 40%.
3. Postgres `max_connections = 200` is hit; new app connections are rejected.
4. On-call scales to 90 pods, each opening up to its pool max — making the connection storm *worse*.
5. Diagnosis takes 40 minutes (a lot of it spent on heap/GC before anyone looked at the DB).
6. Root cause is three-fold: (a) an unbounded N+1 query on the order-confirmation path that was fine at 2,400 req/s and fatal at 14,000; (b) pool sizing that assumed 40 pods, not 90; (c) no statement/transaction timeouts, so a single slow report query held a lock and 40 connections for 20 minutes.
7. Fix took 3 hours (kill the report, patch the N+1, add pgbouncer).

**Postmortem**: "The database was the bottleneck and nobody could see it. We have no query-level visibility, no pool metrics on dashboards, and no safe way to change the schema quickly."

**Your job over 4 weeks**: make the database a first-class, observable, capacity-planned production system — and prove the same spike is survivable.

**Time**: 25–35 hours | **Difficulty**: Advanced

---

## Phase 1 — Full database audit (Day 1–4)

### 1.1 Query inventory and top-offender analysis

Enable and use `pg_stat_statements` (already loaded?), plus statement logging. Produce a report of:

- Top 20 statements by **total** time (not mean) — with calls, mean, total, rows, and shared block hit/read ratio.
- The 10 endpoints whose database time per request is highest.
- Any statement with a large `rows` vs returned-rows mismatch (missing index or over-fetching).

**Deliverable 1 — Query health report**: the top-20 table with diagnosis per statement (missing index / N+1 / over-fetch / inherently slow), plus the arithmetic for the estimated improvement of each fix.

### 1.2 Connection budget

```
current: pods × pool_max = ?  vs  max_connections = 200
```

Produce a tier-by-tier budget (web, workers, batch, admin, replication, monitoring) and the honest conclusion about whether a pooler is required.

**Deliverable 2 — Connection budget** with current vs safe numbers, and a decision on pgbouncer (transaction pooling) with the specific settings and caveats (prepared statements, session state, advisory locks).

### 1.3 Transaction & lock hygiene

- Where transactions are opened/committed in code (list every `@Transactional` boundary and its typical duration).
- Every place a `ResultSet`/`Connection` may leak (list them; these become the leak tests).
- Every long-running query pattern (reports, exports, analytics) that could hold locks/snapshots.

**Deliverable 3 — Transaction hygiene audit** with a fix list and, for each leak candidate, the regression test you will add.

### 1.4 Migration inventory

List all schema changes applied in the last 12 months, and for each: was it `CONCURRENTLY`? Was it batched? Would it have blocked at peak? Rate each as safe / risky / dangerous.

**Deliverable 4 — Migration risk assessment** for the historical set, and a new policy.

---

## Phase 2 — Instrument the database (Day 4–7)

### 2.1 Dashboards (three, one per question)

1. **"Is the DB the bottleneck right now?"** — connections in use vs limit, per-pod pool utilization, pool wait time (acquisition), active queries by `wait_event_type`, DB CPU, I/O.
2. **"Which query is hurting?"** — `pg_stat_statements` total time trend, slow-query log rate, locks held/waiting, replication lag, cache hit ratio.
3. **"Is maintenance keeping up?"** — dead tuples, last autovacuum/analyze age, `age(datfrozenxid)`, bloat estimates, replication lag.

### 2.2 Alerts (thresholds derived from the audit)

| Alert | Threshold (justify) |
|---|---|
| `db_connections_near_limit` | in-use > 80% of `max_connections` (5 min) → warn; > 90% → page |
| `pool_acquisition_wait` | HikariCP `pending` > 0 for 2 min → warn (earliest app-side signal) |
| `long_running_transaction` | any `pg_stat_activity` transaction older than 60 s → warn (this is the poison-loop trigger) |
| `lock_queue` | any query waiting on a lock > 5 s → warn |
| `replication_lag` | > 30 s → warn; > 120 s → page (breaks read-your-writes SLO) |
| `dead_tuple_growth` | dead/live > 50% on any table → warn |
| `xid_age` | `age(datfrozenxid)` > 100M → warn; > 1B → page |
| `cache_hit_ratio` | < 95% → warn |
| `db_cpu_saturation` | > 80% sustained 10 min → warn |

**Deliverable 5 — Observability set**: dashboard links, alert list with the arithmetic behind each threshold, and the runbook link per alert.

---

## Phase 3 — Fix the root causes (Week 2)

1. **N+1 on the confirmation path** — rewrite as a single joined query (or DataLoader-style batching). Verify with `pg_stat_statements` before/after and a load test.
2. **Kill the leak(s)** — try-with-resources everywhere; add regression tests that exercise the failing path 10,000 times against a pool of size 2 and assert it returns to idle; add a CI lint rule.
3. **Kill the long transactions** — `statement_timeout = 5s`, `idle_in_transaction_session_timeout = 60s`, `lock_timeout = 3s` (set per session via Hikari `connection-init-sql` or in the DB role). Move reports to a replica + a read-only role + `default_transaction_read_only`.
4. **Pool right-sizing** — reduce `maximumPoolSize`, set `minimumIdle` low, add `leakDetectionThreshold`, `maxLifetime` < upstream idle-kill. With 40+ pods this alone likely means pgbouncer.
5. **Fix the report query** that held the lock (add index, `SKIP LOCKED` worker pattern, or move to async export).

**Deliverable 6 — Fix set** with before/after evidence (query counts, pool utilization, lock waits, p99 under load).

---

## Phase 4 — Deployment and schema-safety program (Week 2–3)

### 4.1 Migration policy (new)

- Every migration: **expand-contract**, batched backfills, `lock_timeout` set on the migration session, `CONCURRENTLY` for indexes, no long `ACCESS EXCLUSIVE` at peak (state a rule: no lock > 100 ms during business hours).
- Every migration: a **rollback or compensating** plan written *before* merge.
- Every migration: rehearsed on production-sized data in staging; timing recorded.

### 4.2 CI gates

- `pg_stat_statements` diff: fail the build if a changed endpoint increases total DB time by > 20% or query count per request increases.
- Migration lint: fail if a migration creates an index without `CONCURRENTLY` (or has a non-batched backfill on a table > 1M rows).
- Pool config lint: fail if `maximumPoolSize × replicas > 0.7 × max_connections`.
- A staging smoke test that runs each new query under a latency-injecting proxy.

**Deliverable 7 — Policy + gates** merged, with a break-glass process.

---

## Phase 5 — Replay the spike (Week 3)

Run the full incident again, in staging, at production scale:

1. **Baseline** — 2,400 req/s (normal peak).
2. **The spike** — ramp to 14,000 req/s over 10 minutes, hold 20 minutes, ramp down (the real shape of a marketing blast).
3. **Spike + slow report** — a "report" query runs concurrently with a 20 s lock, as in the incident.
4. **Spike + 90 pods** — scale-out during the spike (the amplifying mistake), now with pgbouncer in place.

**Pass criteria**: p99 < 400 ms, error < 0.5%, connections never exceed 80% of limit, no lock waits > 5 s, no long transactions, replica lag < 30 s.

**Deliverable 8 — Load test report** with the four scenarios, criteria met/missed, and any fix needed.

---

## Phase 6 — Provisioning for the next spike (Week 3–4)

Decisions to make and defend (each with a cost estimate):
- Pooler (pgbouncer) vs bigger DB vs fewer pods with better code.
- Read replicas for reports/exports (and how to enforce no writes there).
- Vertical/horizontal scaling policy and pre-warmed capacity for known events.
- Connection budget as a *release gate*: if a new service needs connections, something must give.

**Deliverable 9 — Capacity decision record** with cost, risk, and the trigger to revisit.

---

## Phase 7 — Resilience of the data tier (Week 4)

- **Backup/restore rehearsal**: restore to a scratch instance and measure actual RTO; document the procedure so it is not theoretical.
- **Failover plan**: promote-a-replica runbook (fencing the old primary, app reconnection, DNS/pgbouncer behavior) — rehearse once in staging.
- **PITR**: confirm WAL archiving + a tested point-in-time restore.
- **Read-your-writes**: implement and verify sticky-to-writer or a min-LSN read token for the endpoints that need it.

**Deliverable 10 — Data-tier resilience package**: restore test result, failover runbook, PITR proof, read-your-writes implementation.

---

## Phase 8 — Durability (Week 4)

- On-call training: the DB is now on the runbook rotation; new engineers shadow an incident.
- A "DB health" section in the platform README: pool budget, timeouts, migration policy, dashboards, who to page.
- Quarterly: restore rehearsal + failover rehearsal + one load-test replay on the calendar.

**Deliverable 11 — Durability package**: training plan, README section, calendar.

---

## Deliverables checklist

- [ ] Phase 1 audit deliverables 1–4.
- [ ] Phase 2 observability (dashboards + justified alerts).
- [ ] Phase 3 fixes with before/after evidence.
- [ ] Phase 4 migration policy + CI gates.
- [ ] Phase 5 spike replay report (4 scenarios).
- [ ] Phase 6 capacity decision record.
- [ ] Phase 7 resilience package.
- [ ] Phase 8 durability package.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Diagnosis | "The DB was slow" | Top-offender analysis by total time, N+1 identified, lock/statement analysis |
| Visibility | Added a slow-query dashboard | Panels organized by the three incident questions; alerts with derived thresholds |
| Connection strategy | Increased pool size | Tier-by-tier budget + pooler decision + sizing that respects the ceiling |
| Transactions | Set a timeout "somewhere" | All three timeouts + reports moved to replica + regression tests for leaks |
| Migrations | "Be careful" | Expand-contract policy, `CONCURRENTLY`, batched, rehearsed, CI-enforced |
| Proof | Load test at steady state | Replay the actual incident shape (spike + slow report + scale-out) |
| Resilience | "We have replicas" | Tested restore, rehearsed failover, PITR, read-your-writes |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **PostgreSQL `pg_stat_statements` documentation** — https://www.postgresql.org/docs/current/pgstatstatements.html — authoritative definition of `total_exec_time` vs `mean_exec_time` (the distinction that makes top-offender analysis correct), plus the `pg_stat_statements_info` reset semantics you need for before/after comparisons. Verify column names for your PG major version (names changed across versions, e.g. `time` → `total_time` → `total_exec_time`).
2. **PostgreSQL `ALTER TABLE` documentation** — https://www.postgresql.org/docs/current/sql-altertable.html — the source for `NOT VALID` / `VALIDATE CONSTRAINT`, `ADD COLUMN` with a constant default (no rewrite), `SET NOT NULL` fast path via a validated check constraint, and `ACCESS EXCLUSIVE` locking behavior. Verify which operations support a reduced lock level in your specific version (the lock-avoidance list has expanded over releases).

Additional anchors worth verifying: `pg_stat_activity` / `wait_event_type` semantics for your version, and `pgbouncer` transaction-pooling caveats (prepared statements, session state) in the pgbouncer docs for your version — these change between releases.

---

## Reflection questions

1. Scaling 40 → 90 pods made the incident worse. What single rule should govern scale-up during an incident, and why does the DB make it worse than stateless tiers?
2. Which query fix delivered the most improvement per engineering hour, and how did you know?
3. If you could only keep one database alert forever, which one, and what decision does it enable?
4. What would it take to make a schema change so safe that you stopped thinking about it?
5. How would you explain to a stakeholder why the database needs its own capacity plan rather than being treated as "part of the app"?
