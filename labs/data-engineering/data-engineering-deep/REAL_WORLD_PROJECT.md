# data-engineering-deep — REAL WORLD PROJECT

## Context

A subscription media company is migrating 900 tables from raw Parquet to a
lakehouse, split across four teams who each built their own pipelines. The
state today: 3.4PB, 1,200 daily tasks, no shared freshness definition, four
different definitions of "a day", a $2.1M/month warehouse bill, and a finance
close that depends on numbers nobody can reproduce. You are the first data
platform lead. There is no mandate to standardize everything, and you have
90 days to prove the platform works.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Data | 3.4PB, 1.2B rows/day, 900 tables, 4 producing teams |
| Pipelines | 1,200 daily tasks, 12 Flink jobs, 340 Airflow DAGs |
| Engines | Spark 3.5, Flink 1.18, Trino, Snowflake (BI), Athena (ad-hoc) |
| Freshness | undefined; 41% of tables have a consumer-impacting lag > 24h |
| Bill | $2.1M/month: 46% compute, 31% scan, 18% storage, 5% requests |
| Correctness | no reconciliation; 2 known historical mis-statements |
| Compliance | 7y retention, SOX, EU residency for 3 datasets, GDPR erasure |
| Constraint | 90 days, 2 platform engineers, no migration freeze |

## Architecture (target, and it is deliberately partial)

```
              +-- ONE registry (owner, class, retention, lineage, freshness SLO)
              +-- ONE policy engine (CI + runtime)
   platform --+-- ONE table format default (Iceberg), Delta allowed for 40 tables
              +-- ONE cost model per team budget
                    |
   +----------------+----------------+----------------+
   |                |                |                |
 team A         team B           team C           team D
 (ingest)        (transform)     (streaming)      (BI/serving)
   |                |                |                |
   +--> bronze (raw, immutable, 400d, file-health monitored)
          |
        silver (conformed, one grain per table, SLO'd)
          |
   +------+--------------------------------------+
   |                    |                       |
 gold (marts)     ml features              semantic layer
 (pre-aggregated)  (point-in-time)        (one metric definition)
```

The important decision: **standardize the three things that are expensive to
get wrong, and leave the rest alone.** Table format, freshness definition, and
cost attribution are the three.

## Key Implementation — the 90-day plan, and what it deliberately leaves

| Days | Work | Why first |
|---|---|---|
| 1-14 | Freshness SLO per *dataset*, not per task. Registry populated from engines automatically. | Freshness is what the business feels, and it is measurable without changing any pipeline. |
| 15-30 | Reconciliation loop for the 12 finance-facing metrics against the ledger. | Establishes trust, and finds the existing mis-statements before they compound. |
| 31-50 | Cost model and per-team budgets. Query tags mandatory. Warehouse lifecycle. | Cost is the argument that buys the remaining 40 days. |
| 51-75 | Table format for new tables; 3 pilot migrations; MERGE-scope guard shipped platform-wide. | Prevents the problem growing faster than it is fixed. |
| 76-90 | Policy engine for classification and owner; 90-day owner attestation campaign. | The thing that must start on day 91 to be credible. |

Explicitly not attempted in 90 days: migrating the 40 Delta tables, rebuilding
the 340 DAGs, decomposing team-owned domains, or standardizing the BI tool.

## Key Implementation — the four decisions, with the numbers

**Decision 1: freshness is a per-dataset SLO with a business owner, not a task
status.** Before, "the DAG succeeded" was the freshness signal. It is the least
useful one.

```java
public record FreshnessSlo(String datasetId, Duration target, Duration p50Actual,
                            Duration p99Actual, String owner, String consequence) {
    public boolean breached() { return p99Actual.compareTo(target) > 0; }
    /**
     * The consequence field is what makes this stick. "Late by 2h" is an
     * engineering metric; "the morning revenue email uses this" is a business
     * one, and it is what the owner is accountable for.
     */
}
```

Result: 41% of tables with > 24h lag became 12%, because a named owner with a
consequence attached fixed the ones that mattered and deliberately deprioritised
the ones that did not.

**Decision 2: reconciliation for 12 metrics, not 900 tables.** The full-scope
version is unaffordable and unnecessary — the trust problem is concentrated.

```java
public final class FinanceReconciliation {
    /**
     * Twelve metrics, chosen because they are contractual or because a
     * mis-statement has already happened. Everything else gets spot checks.
     * The ledger is the authority because it is produced by a different system
     * with different code, which is the only kind of check that can catch a
     * shared bug.
     */
    static final List<MetricSpec> SPECS = List.of(
        new MetricSpec("revenue_recognised", ledger.glDailyRevenue(), 0.5),
        new MetricSpec("subscriber_count", ledger.glActiveSubs(), 0.01),
        new MetricSpec("churn_rate", ledger.glChurn(), 0.05),
        new MetricSpec("ad_revenue", ledger.glAdRevenue(), 0.5),
        // ... 8 more
    );

    public Verdict compare(String metric, Instant day) {
        double ours = mart(metric, day);
        double theirs = ledger(metric, day);
        double diff = theirs == 0 ? 0 : 100 * (ours - theirs) / Math.abs(theirs);
        return new Verdict(metric, day, ours, theirs, diff,
                Math.abs(diff) <= tolerance(metric) ? VerdictCode.OK : VerdictCode.BREACH);
    }
}
```

The 2 known mis-statements were found in week 2, both from decimal-to-double
conversion, both exactly the class of bug the 12 metrics now watch for.

**Decision 3: cost attribution first, reduction second.** Nobody reduces a bill
they cannot attribute.

```java
public record TeamBudget(String team, double monthlyBudgetCredits, double spent,
                         List<String> topContributors) {
    public double remaining() { return monthlyBudgetCredits - spent; }
    public boolean atRisk() { return spent / monthlyBudgetCredits > 0.8; }
}
```

Query tags became mandatory for service roles in week 4, and within three days
it identified a single job looping 40x on a retry path — 9% of the total bill,
found without anyone filing a ticket. Lifecycle changes on 34 warehouses
(auto-suspend) removed 22% of compute, the largest single saving available
because most warehouses were idle 86% of the time.

**Decision 4: the MERGE-scope guard, shipped platform-wide, prevents the
problem rather than fixing it.** This is the highest-leverage day of the 90.

```java
public final class MergeScopeGuard {
    /**
     * Every MERGE in the platform passes through this. If it cannot state
     * which partitions/files it can touch, or if that scope exceeds a
     * fraction of the table, it is refused with an actionable message.
     *
     * This is a control, not an optimization: it stops a 6-hour job from
     * blocking an hourly refresh, which is a failure mode that costs a team
     * a day every time it happens.
     */
    public void check(String table, Predicate scope, long candidateBytes,
                      long tableBytes) {
        if (candidateBytes == 0) {
            throw new UnboundedMergeException(table,
                    "MERGE could not be pruned to any partition. "
                    + "Add a partitioning predicate on the leading key, or aggregate earlier.");
        }
        double fraction = (double) candidateBytes / Math.max(1, tableBytes);
        if (fraction > MAX_SCOPE_FRACTION) {
            throw new ScopeTooLargeException(table,
                    "MERGE would touch " + String.format("%.0f%%", 100 * fraction)
                    + " of the table (" + candidateBytes + " of " + tableBytes + " bytes). "
                    + "Partition by the predicate's leading key, or narrow the run window.");
        }
    }
}
```

## Measured outcomes at day 90

| Metric | Day 0 | Day 90 | Note |
|---|---|---|---|
| Datasets with > 24h consumer-impacting lag | 41% | 12% | owners assigned, SLOs published |
| Finance metrics reconciled daily | 0 | 12 | 2 historic mis-statements found |
| Monthly bill | $2.1M | $1.63M | -22%, from lifecycle + one looping job |
| Attribution coverage (credits to a team) | 31% | 96% | mandatory query tags |
| Tables on a table format | 0 | 3 pilots + all new tables | full migration not attempted |
| Unbounded MERGEs in the codebase | unknown | 0 | guard blocks them at build time |
| Datasets with a named owner | 68% | 94% | 90-day attestation campaign running |
| On-call pages for data freshness | not paged | 3/month | burn-rate routing, no alert fatigue |

## The honest assessment

What is not fixed after 90 days, stated plainly:

- The 4 producing teams still own their domains. Data mesh is a two-year
  change, not a quarter.
- 41 Airflow DAGs still have retry storms. The 90 days bought the monitoring
  that would make fixing them safe; the fixes are next quarter's work.
- Storage is 18% of the bill and unchanged. Retention classes were defined but
  not applied, because that requires per-dataset deletion decisions that need
  the owners the campaign is still building.
- 2 of the 12 reconciled metrics have never been within tolerance. Both are
  still under investigation and both involve a source system that has not been
  reverse-engineered yet.

Reporting the unfinished work with the finished work is part of the job. A 90-day
report that claims the bill is down 22% and does not mention two metrics that
still do not reconcile is a report nobody trusts the second time.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Apache Iceberg provides snapshots, hidden partitioning, schema evolution, and
  first-class row deletes, and is supported by multiple engines — which is what
  makes it a viable default for a multi-team lakehouse.
  - Reference: https://iceberg.apache.org/
  - Reference: https://iceberg.apache.org/docs/latest/
  - Reference: https://iceberg.apache.org/docs/latest/evolution/
- Apache Airflow models pipelines as DAGs with data intervals, sensors, and
  backfill; the scheduler runs tasks, so idempotency and freshness remain the
  implementer's responsibility.
  - Reference: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html
  - Reference: https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html
- Apache Spark's physical plan and Adaptive Query Execution determine shuffle
  behaviour and skew handling, which is where most of the compute cost in a
  Spark-based platform originates.
  - Reference: https://spark.apache.org/docs/latest/sql-performance-tuning.html
  - Reference: https://spark.apache.org/docs/latest/job-scheduling.html
- Apache Flink's checkpointing and state backends determine recovery time and
  state cost, which is the core trade-off for long-running streaming jobs.
  - Reference: (link removed)
  - Reference: (link removed)
- OpenLineage provides a standard for lineage metadata, which the freshness SLOs
  and impact analysis depend on.
  - Reference: https://openlineage.io/docs/

## Deliverables

- [ ] Freshness SLO per dataset with a named owner and a stated consequence
- [ ] Reconciliation loop for 12 finance metrics against the ledger, with tolerances
- [ ] Cost model with mandatory query tags and per-team budgets
- [ ] Warehouse lifecycle changes with a measured credit reduction
- [ ] MERGE-scope guard shipped platform-wide, blocking unbounded MERGEs at build time
- [ ] Table format pilot: 3 migrations with dual-write verification
- [ ] Policy engine for classification and ownership, with the attestation campaign
- [ ] 90-day report that states the unfinished work alongside the results
- [ ] Six-month plan covering the 4 items explicitly not fixed
- [ ] Runbook: watermark stall, scope refusal, reconciliation breach, cost
      anomaly, owner churn, engine incompatibility
