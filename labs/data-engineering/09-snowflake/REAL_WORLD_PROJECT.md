# Snowflake — REAL WORLD PROJECT

## Context

A retail group consolidated 6 subsidiaries onto Snowflake in 18 months. The
platform now costs $1.4M/month, up 3.1x while data grew only 1.9x. Two teams
have `OWNERSHIP` on the whole database "because they needed access once", one
analyst runs unfiltered full-table scans in the morning, and the finance
close depends on a dashboard that takes 22 minutes to load. You own cost,
performance, and governance together.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Storage | 1.4PB compressed, 3.2PB uncompressed |
| Credits | ~1.15M credits/month (~$1.4M) |
| Warehouses | 34, of which 19 always-on |
| Users | 480 (60 analysts, 340 services, 80 ad-hoc) |
| Critical path | month-end close, 04:00-07:00 UTC, 340 concurrent |
| Compliance | PCI for card data, SOX for financial reporting |
| Constraint | no migration to another platform; fix in place |

## Architecture (target)

```
RAW            external stage only, no tables (cheapest landing, 7d retention)
CURATED        internal tables, clustered, owned by data engineering
ANALYTICS      marts + materialized views for the 14 top dashboards
SEMANTIC       one governed metric layer; metrics defined once, consumed everywhere

warehouses by workload, not by team:
  WH_ETL_*        XL, auto-suspend 60s, off-peak schedule
  WH_BI_*         S, auto-suspend 300s, business hours only
  WH_SCIENCE_*    M, elastic for notebooks
  WH_CRITICAL_*   reserved slots, tagged + cost-tracked

RBAC: ANALYST -> BI_SERVICE -> no ownership; per-schema access via roles
```

## Key Implementation — cost control is mostly warehouse lifecycle

**Measure first.** The first 10 minutes of any bill investigation is one query.

```sql
-- where did the credits go, by tag, in the last billing period?
SELECT TAG_NAME, SERVICE_NAME, WAREHOUSE_NAME,
       SUM(CREDITS_USED)                          AS credits,
       SUM(CREDITS_USED) / NULLIF(EXPIRY_TIME,0)  AS credits_per_second,
       AVG(BYTES_SCANNED)                          AS avg_bytes
  FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
 WHERE START_TIME BETWEEN DATEADD('day',-30,CURRENT_DATE()) AND CURRENT_DATE()
   AND EXECUTION_STATUS = 'SUCCESS'
 GROUP BY 1,2,3
 ORDER BY credits DESC
 FETCH FIRST 25 ROWS ONLY;

-- idle time is pure waste
SELECT WAREHOUSE_NAME, SUM(CREDITS_USED) AS idle_credits
  FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_LOAD_HISTORY
 WHERE START_TIME BETWEEN DATEADD('day',-30,CURRENT_DATE()) AND CURRENT_DATE()
   AND CREDITS_USED > 0
   AND STATE = 'IDLE'            -- the warehouse was up and nobody used it
 GROUP BY 1 ORDER BY 2 DESC;
```

**The three changes that cut 41% of spend**, in order of impact:

| Change | Mechanism | Measured saving |
|---|---|---|
| `INITIALLY_SUSPENDED` + auto-resume on all 34 warehouses | 19 always-on warehouses were idle ~86% of the time | $415k/yr |
| Query tags mandatory on service roles (`ALTER USER ... SET QUERY_TAG`) | attributed spend; found one ETL looping 40x | $260k/yr |
| Clustering keys on 6 largest CURATED tables | minutes of scan -> seconds; fewer retries and reruns | $95k/yr |

```sql
-- a warehouse that cannot be left running by accident
ALTER WAREHOUSE WH_BI_PM SET INITIALLY_SUSPENDED = TRUE;
ALTER WAREHOUSE WH_BI_PM SET AUTO_SUSPEND = 300;      -- 5 min of grace for humans
ALTER WAREHOUSE WH_BI_PM SET AUTO_RESUME = TRUE;
ALTER WAREHOUSE WH_BI_PM SET RESOURCE_MONITOR = 'credit';  -- cap runaway queries
ALTER WAREHOUSE WH_BI_PM SET STATEMENT_QUEUED_TIMEOUT_IN_SECONDS = 30;
```

## Performance: the 22-minute dashboard

The dashboard joined 9 tables without a clustering strategy, so pruning was
effectively random.

```sql
-- Before: 22.4 min, 3.1TB scanned.
-- Step 1: cluster the two large tables on the columns that are always filtered.
ALTER TABLE curated_orders CLUSTER BY (TO_DATE(order_ts), country);
ALTER TABLE curated_returns  CLUSTER BY (TO_DATE(return_ts), region);

-- Step 2: read from a materialized view instead of re-aggregating 900M rows.
CREATE MATERIALIZED VIEW analytics.mv_daily_channel_perf
  CLUSTER BY (d, channel)
  AS SELECT TO_DATE(order_ts) AS d, channel, country,
             COUNT(*) AS orders, SUM(amount) AS revenue
      FROM curated_orders GROUP BY 1,2,3;
```

Result: 4.1 min cold, 38s warm, 210GB scanned. The remaining cost of
clustering is write amplification — measurable, and worth it here because
these tables are read far more than written.

## Governance Without Blocking Analysts

Six subsidiaries, four card-data environments, SOX sign-off. The pattern that
worked: **role hierarchy + views, never table grants.**

```java
/** Effective permission resolution used to validate the access model in CI. */
public final class AccessReview {
    public record Grant(String role, String objectName, Set<String> privileges) {}

    public List<String> violations() {
        List<String> out = new ArrayList<>();
        for (Grant g : grants) {
            if (g.role().equals("ANALYST") && g.privileges().contains("OWNERSHIP"))
                out.add("ANALYST must never hold OWNERSHIP on " + g.objectName());
            if (g.privileges().contains("SELECT") && g.privileges().contains("DELETE"))
                out.add("mixed SELECT/DELETE grant on " + g.objectName() + " for " + g.role());
        }
        return out;
    }
}
```

Layered so the same objects serve different consumers:

```sql
CREATE OR REPLACE VIEW analytics.v_orders_masked   AS SELECT * FROM curated_orders;
CREATE OR REPLACE VIEW analytics.v_orders_pci      AS SELECT * FROM curated_orders
  WHERE card_last4 IS NULL OR FALSE;         -- analysts never see card data
CREATE OR REPLACE VIEW analytics.v_orders_finance AS SELECT * FROM curated_orders
  WHERE region = 'NA';                      -- SOX entity scoping
GRANT SELECT ON analytics.v_orders_masked   TO ROLE ANALYST;
GRANT SELECT ON analytics.v_orders_pci      TO ROLE PCI_BI;
```

## Failure Modes and the Runbook

1. **A runaway query consumes a warehouse.** Symptom: credit burn, BI timeouts.
   Fix: `RESOURCE_MONITOR`, statement timeout, and a `QUERY_TAG`-scoped cancel
   policy; plus a 2x burn-rate alert against the daily baseline.
2. **Data team downsize blocked by a month-end requirement.** Fix: reserved
   critical-path pools with a scheduled window, and a documented emergency
   warehouse size for close.
3. **Table bloat in CURATED** — 3.2PB uncompressed, 68% of it dropped columns
   nobody queries. Fix: drop unused columns, re-cluster (which rewrites without
   a re-ingest), and set a per-table storage budget.
4. **Clustering on a high-cardinality key.** Symptom: clustering metadata itself
   is expensive, and the rewrite time is measured in hours. Fix: cardinality
   rule of thumb — cluster on low-to-medium cardinality, filter on high.
5. **Semi-structured JSON scanned wholesale.** Symptom: slow queries, large
   `BYTES_SCANNED`. Fix: project into typed columns at ingest; keep JSON only
   for genuinely variable payloads.
6. **Query history itself becomes a cost.** Symptom: `QUERY_HISTORY` queries slow
   as volume grows. Fix: query `ACCOUNT_USAGE` for reporting, `QUERY_HISTORY`
   only for recent debugging, and materialize daily cost rollups.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Snowflake's architecture separates storage from compute: data lives once in
  cloud storage, and virtual warehouses provide independent, elastic compute
  that can be sized, started, and suspended per workload.
  - Reference: https://docs.snowflake.com/en/user-guide/intro-architecture
  - Reference: https://docs.snowflake.com/en/user-guide/intro-workspaces
- Snowflake's cost model is credit-based: warehouses consume credits per second
  while running, which is why auto-suspend and workload separation are the
  primary cost levers rather than storage alone.
  - Reference: https://docs.snowflake.com/en/guides-overview-cost
  - Reference: https://docs.snowflake.com/en/user-guide/warehouses-considerations

## Deliverables
- [ ] Cost investigation query set (top consumers, idle time, failure spend)
- [ ] Warehouse lifecycle config for all 34 warehouses with before/after credits
- [ ] Clustering + materialized view fix for the 22-minute dashboard
- [ ] RBAC hierarchy with a CI access review that fails on OWNERSHIP grants
- [ ] Metric layer plan (one definition per metric, consumed by all 14 dashboards)
- [ ] Per-team credit budgets with 50/80/100% alerting
- [ ] Runbook for the six failure modes
