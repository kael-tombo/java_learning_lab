# ETL Processes — REAL WORLD PROJECT

## Context

A B2B SaaS company bills on usage. Their warehouse load was a single Airflow
task running 40 minutes of `INSERT INTO ... SELECT` with no staging, no
history, and no reconciliation. Finance found a $310k revenue miss three weeks
late. Your mandate: rebuild the billing ETL with correctness as the primary
requirement.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Customers | 12k accounts, 9M usage events/day |
| Change rate | customer attributes change ~0.4% per day |
| Load window | finance needs numbers by 06:00 UTC |
| History required | 7 years of plan/price history for audits |
| Late data | usage events arrive up to 36h after the fact |
| Constraint | cannot exceed 3h runtime; warehouse credits are metered |

## Architecture

```
sources (API export, S3 usage dumps, billing DB CDC)
   |
[stage]  -> raw_*, immutable, partitioned by ingest_date
   |
[conformed] -> dim_customer (SCD2), dim_plan (SCD2), dim_date, fact_usage (append)
   |
[billing]  -> fact_invoice_line (immutable, corrected by adjustment rows)
   |
[marts]    -> revenue_mrr_daily, usage_rollup_monthly
   |
[reconciliation] -> finance_signoff report, alerts on imbalance
```

## Key Implementation — watermarked, resumable full-refresh hybrid

Plan and price data is small, so it is re-read fully; usage is enormous, so it
is incremental. The load is resumable at a partition level.

```java
public class BillingEtl {
    private static final Duration MAX_LATENESS = Duration.ofHours(36);
    private final Warehouse warehouse;
    private final Set<LocalDate> lastGoodPartitions = new HashSet<>();

    public void run(LocalDate businessDay) {
        for (LocalDate d : openWindow(businessDay)) {
            if (lastGoodPartitions.contains(d)) continue;      // already reconciled
            warehouse.transactionally(tx -> {
                tx.merge("dim_plan", readPlanSnapshots(), "plan_id");
                tx.merge("dim_customer", readCustomerChangesSince(d), "customer_id, valid_from");
                tx.upsert("fact_usage", readUsagePartition(d));   // partition-scoped idempotent
            });
            lastGoodPartitions.add(d);
        }
    }

    // Open window covers late arrivals; anything older is a restatement, not a load.
    private List<LocalDate> openWindow(LocalDate businessDay) {
        List<LocalDate> days = new ArrayList<>();
        for (int i = (int) MAX_LATENESS.toDays(); i >= 0; i--) {
            days.add(businessDay.minusDays(i));
        }
        return days;
    }
}
```

## Corrections, Not Deletions

Billing facts are never updated in place. A restatement is a compensating row
so the audit trail explains the number.

```sql
-- adjustment pattern: negative original + positive correction, linked by correction_id
INSERT INTO fact_invoice_line
  (invoice_line_id, invoice_id, account_id, metric, amount_cents,
   as_of_date, is_correction, corrects_line_id)
VALUES (:newId, :invoiceId, :accountId, :metric, :originalAmount * -1,
        CURRENT_DATE, true, :originalLineId);
```

## Reconciliation and Sign-off

Finance will not take a number they cannot trace. Three gates before publish:

1. **Row-count parity** — `stage_raw_usage` vs `fact_usage` per partition.
2. **Sum parity** — `SUM(amount_cents)` in staging vs mart, tolerance 0.
3. **Independent recompute** — a slow, simple query written by a second engineer
   must land within $1 of the pipeline result.

```java
boolean publish(Reconciliation r) {
    return r.rowParity() && r.sumDeltaCents() == 0 && r.independentDeltaCents() < 100;
}
```

## Failure Modes and the Runbook

1. **SCD2 gap** — a customer change applied without closing the prior version.
   Symptom: two `is_current = true` rows. Fix: nightly assertion query fails the run.
2. **Late usage beyond 36h** — treated as a new partition by mistake, double
   counting. Fix: partition ownership by `event_date`, not arrival date.
3. **Metered credit overrun** — 3h limit exceeded mid-load. Fix: process newest
   partitions last so the important ones complete; resume next night.
4. **Timezone bug at month boundary** — usage attributed to the wrong month,
   finance close breaks. Fix: store UTC, convert with an explicit `dim_date`
   key, never `LocalDate.now()` in transform code.
5. **Schema drift on plan export** — a new nullable column. Fix: staging is
   text, conformance tolerates extras, alerting on column-count change.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Airflow tasks should be idempotent and use retries/sensors; the orchestrator
  models dependencies and backfill, while data movement stays in the task body.
  - Reference: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html
  - Reference: https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html
- dbt models are materialized as views, tables, or incremental models, and
  incremental models run a merge on a unique key so re-runs do not duplicate.
  - Reference: https://docs.getdbt.com/docs/concepts/materializations
  - Reference: https://docs.getdbt.com/docs/build/incremental-models
- Slowly changing dimensions are a standard warehousing pattern; Type 2 keeps
  full history with effective-dated rows rather than overwriting.
  - Reference: https://en.wikipedia.org/wiki/Slowly_changing_dimension

## Deliverables
- [ ] Layered design doc (stage / conform / mart) with a data contract per layer
- [ ] SCD2 dimension with the two-current-rows assertion
- [ ] Adjustment-row pattern for restatements, with an example query
- [ ] Three-gate reconciliation harness and a signed-off run
- [ ] Restatement runbook with a 30-day open-window policy
