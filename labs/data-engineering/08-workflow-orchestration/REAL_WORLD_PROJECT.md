# Workflow Orchestration — REAL WORLD PROJECT

## Context

An online travel company runs ~600 Airflow DAGs with 4,200 daily tasks, forked
across 4 schedulers over 3 years. The pain: DAGs overlap, retry storms, backfills
recompute months of data and take down shared tables, and no one can answer
whether a metric is fresh. There is also a hard regulatory deadline: booking
data must be reproducible for 7 years. You are consolidating this.

## Scale & Constraints

| Dimension | Value |
|---|---|
| DAGs / tasks | 620 DAGs, 4,200 tasks/day, peak 900 concurrent slots |
| Schedulers | 4 Airflow schedulers, Celery executor, Postgres metadata DB |
| Critical DAG | 320 tasks, must finish before 07:00 UTC (booking recon) |
| Backfill need | up to 24 months, must not disturb production tables |
| Tenancy | 12 teams, no per-team isolation today |
| Constraint | no big-bang cutover; migrate team by team |
| Compliance | 7-year reproducibility of booking revenue |

## Architecture (target)

```
                 +-- scheduler pool: "critical" (8 slots, reserved for SLO DAGs)
scheduler tier --+-- pool: "standard" (60 slots)
                 +-- pool: "backfill"   (30 slots, off-peak, no prod writes)
                            |
                        metadata DB (Postgres, read-replica for UI)
                            |
        task execution -> compute cluster (K8s) -- OR -- warehouse SQL
                            |
   observability: metrics (task duration, success, queue depth, SLA miss)
                  lineage: DAG -> table -> dashboard
```

Three design choices did the heavy lifting.

**1. Every task declares what it reads and writes.** That single annotation
drives freshness dashboards, impact analysis ("which DAGs break if I change
this table?"), and safe backfill (skip downstream tasks whose inputs are
unchanged).

```java
public record TaskSpec(String id, String pool, Duration timeout, int retries,
                       List<String> reads, List<String> writes,
                       boolean writesProd, TaskBody body) {
    public static Builder task(String id) { return new Builder(id); }

    public static final class Builder {
        private final String id; private String pool = "standard";
        private Duration timeout = Duration.ofHours(2);
        private int retries = 2; private List<String> reads = List.of();
        private List<String> writes = List.of(); private boolean writesProd = true;

        public Builder reads(String... t)  { reads = List.of(t); return this; }
        public Builder writes(String... t) { writes = List.of(t); return this; }
        public Builder pool(String p)      { pool = p; return this; }
        public Builder timeout(Duration d){ timeout = d; return this; }
        public Builder retries(int r)      { retries = r; return this; }
        /** Backfill-safe tasks write to a date-suffixed shadow table instead of prod. */
        public Builder shadowOnBackfill()   { writesProd = false; return this; }

        public TaskSpec build(String id, TaskBody body) {
            return new TaskSpec(id, pool, timeout, retries, reads, writes, writesProd, body);
        }
    }
}
```

**2. Production writes are gated by a lease, not by convention.**

```java
public final class WriteLease {
    private final String table;
    private final LocalDate businessDate;
    private final Duration ttl;

    public void assertHeld(LocalDate logicalDate) {
        Lease l = store.get(table);
        boolean backfill = ctx.isBackfill();
        if (backfill && l.active() && !l.holder().equals(ctx.dagId())) {
            throw new LeaseConflict("backfill would overwrite " + table + " for " + logicalDate
                    + "; held by " + l.holder() + " until " + l.expiresAt());
        }
    }
}
```

**3. Freshness is a data product, not a hope.** The metric is the time between
the business event and its availability in the serving table, per table, p50
and p99, with an owner.

```java
public record FreshnessSlo(String table, Duration p99Target, Duration p50Actual, Duration p99Actual) {
    public boolean breached() { return p99Actual.compareTo(p99Target) > 0; }
    public Duration remaining() { return p99Target.minus(p99Actual); }
}
```

## Migration Plan (18 weeks)

1. **Weeks 1-3 — Foundation.** Pools, task-level logging, `reads`/`writes` annotation
   as a lint rule. No DAG changes; just visibility.
2. **Weeks 4-8 — Isolation.** Critical DAGs to the reserved pool. Backfill tasks to
   the backfill pool with shadow writes. Measure: peak concurrent queue depth fell 61%.
3. **Weeks 9-14 — Consolidation.** Merge the 620 DAGs to ~140 by domain. Collapse
   `bash -c` monoliths into Airflow-native tasks so retries are per-step. Expected
   effect: retry storms stop re-running successful work.
4. **Weeks 15-18 — Contract.** Freshness SLOs published, owners assigned, plus a
   deprecation path for cron-only jobs.

## Failure Modes and the Runbook

1. **Metadata DB saturation.** Symptom: scheduler lag, UI timeouts. Cause: one
   scheduler's queue view. Fix: reduce scheduler count or move the UI to the
   read-replica, and cap `max_active_runs_per_dag`.
2. **Backfill collides with production.** Symptom: wrong numbers for a hot table.
   Fix: the write lease above; backfill writes shadow tables and reconciles before swap.
3. **Retry storm.** Symptom: a broken upstream causes 40x downstream task failures in
   minutes. Fix: `all_done` trigger only where independence exists, exponential
   backoff, and a circuit breaker on a failing table.
4. **Long-running task blocks a pool.** Symptom: whole pool stalls. Fix: `timeout`
   enforced by the task wrapper (not the DAG), plus pool-level priority.
5. **Sensor waits forever.** Symptom: a DAG queued for hours waiting on data.
   Fix: sensors have a bounded deadline and fail the DAG, which is more visible
   than a silent wait.
6. **Clock skew / wrong logical date.** Symptom: a run processes the wrong day.
   Fix: logical date passed explicitly to every task; `now()` banned in task code.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Airflow is a platform to programmatically author, schedule, and monitor
  workflows; a workflow is a DAG of tasks, and the scheduler runs tasks according
  to dependencies, with data intervals and backfill as first-class concepts.
  - Reference: https://airflow.apache.org/docs/apache-airflow/stable/index.html
  - Reference: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html
  - Reference: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#backfill
- Airflow's own best-practice guidance is that tasks should be idempotent and
  should not pass large data between tasks (XCom is for small metadata), because
  the orchestrator is not the data transport.
  - Reference: https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html

## Deliverables
- [ ] Target architecture with pool/concurrency design and slot numbers
- [ ] TaskSpec with `reads`/`writes` annotation powering impact analysis
- [ ] Write-lease implementation with a collision test
- [ ] Freshness SLO definitions and a published dashboard
- [ ] 18-week migration plan with measurable exit criteria per phase
- [ ] Runbook for the six failure modes
