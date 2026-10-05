# Snowflake — MINI PROJECT

## Project: Analytics Warehouse on Snowflake (or DuckDB Fallback)

A working schema, load, transform, and query suite with a credit-cost
accounting layer. Runs against Snowflake with `SNOWFLAKE_*` env vars; falls back
to DuckDB locally so the code is runnable without an account.

### Scope
- Schemas: `RAW`, `STAGE_LANDING`, `CURATED`, `ANALYTICS`, `SEMANTIC`.
- External stage over Parquet, internal table from the stage.
- Transformations: SQL models with `MERGE`-style idempotency.
- Serving: materialized view + dynamic table with a refresh policy.
- Governance: role hierarchy, masking policy, row access policy.
- Cost: per-query credit attribution harness.

### Architecture

```
s3://bucket/raw/orders/*.parquet
   |
@RAW_STAGE (external stage + file format, no copy)
   |
raw_orders (internal table, cluster by (order_date, country))
   |
curated_orders  (cleaned, SCD2 customer join)
   |
mv_curated_orders            (materialized view, DDL-based, incremental refresh)
   |
analytics.daily_revenue     (dynamic table, TARGET_LATENCY = '5 minutes')
   |
semantic layer -> BI
```

### Loading with a stage and file format

```sql
CREATE OR REPLACE FILE FORMAT ff_parquet
  TYPE = PARQUET
  COMPRESSION = AUTO
  BINARY_AS_TEXT = FALSE;

CREATE OR REPLACE STAGE RAW_STAGE
  URL = 's3://acme-lake/raw/orders/'
  STORAGE_INTEGRATION = si_lake_readonly
  FILE_FORMAT = (FORMAT_NAME = ff_parquet);

-- Query the staged files with no copy at all: the cheapest exploration there is.
SELECT DATE_TRUNC('day', $1:order_ts::timestamp_ntz) AS d,
       SUM($1:amount::number(12,2))                     AS revenue,
       COUNT(*)                                         AS orders
  FROM @RAW_STAGE/orders
 WHERE $1:order_ts::timestamp_ntz >= '2026-01-01'
 GROUP BY 1 ORDER BY 1;

-- Materialize only what earns its storage.
CREATE TABLE raw_orders (
  order_id        VARCHAR,
  customer_id     VARCHAR,
  order_ts        TIMESTAMP_NTZ,
  amount          NUMBER(12,2),
  country         VARCHAR,
  currency        VARCHAR,
  ingested_at     TIMESTAMP_NTZ DEFAULT SYSDATE()
) CLUSTER BY (TO_DATE(order_ts), country);

COPY INTO raw_orders FROM @RAW_STAGE/orders
  FILE_FORMAT = (FORMAT_NAME = ff_parquet)
  ON_ERROR = CONTINUE;                -- a few malformed rows must not kill a 200M-row load
```

### Idempotent transform

```sql
MERGE INTO curated_orders AS t
USING (
  SELECT o.order_id, o.customer_id, o.amount, c.segment, o.order_ts
    FROM raw_orders o
    LEFT JOIN dim_customer c
      ON c.customer_id = o.customer_id
     AND c.is_current = TRUE
   WHERE o.order_ts >= DATEADD('day', -7, CURRENT_DATE())
) AS s
ON t.order_id = s.order_id
WHEN MATCHED AND (t.amount <> s.amount OR t.segment <> s.segment) THEN
  UPDATE SET t.amount = s.amount, t.segment = s.segment, t.updated_at = SYSDATE()
WHEN NOT MATCHED THEN
  INSERT (order_id, customer_id, amount, segment, order_ts)
  VALUES (s.order_id, s.customer_id, s.amount, s.segment, s.order_ts);
```

### Dynamic table for freshness

```sql
CREATE OR REPLACE TABLE analytics.daily_revenue
  TARGET_LATENCY = '5 minutes'
  CLUSTER BY (d)
  AS
SELECT TO_DATE(order_ts)                        AS d,
       country,
       COUNT(*)                                  AS orders,
       SUM(amount)                               AS revenue
  FROM curated_orders
 GROUP BY 1, 2;
```

### Masking and row access policies

```sql
CREATE OR REPLACE MASKING POLICY mp_email AS
  (val STRING) RETURNS STRING ->
    CASE WHEN CURRENT_ROLE() IN ('ANALYST', 'BI_SERVICE') THEN val
         ELSE REGEXP_REPLACE(val, '(.{2}).*(.+)@', '\\1***\\2@') END;

ALTER TABLE curated_orders
  MODIFY COLUMN customer_email SET MASKING POLICY mp_email;

CREATE OR REPLACE ROW ACCESS POLICY rap_region AS (country STRING) RETURNS BOOLEAN ->
  'REGION_EU' = CURRENT_ROLE() OR country IN ('DE','FR','NL','ES','IT');

ALTER TABLE curated_orders ADD ROW ACCESS POLICY rap_region ON (country);
```

### Cost attribution

```java
public record QueryCost(String statementId, String warehouse, String role,
                        String queryTag, long credits, double wallSeconds) {
    public double creditsPerMillionRows(double rows) {
        return rows == 0 ? 0 : credits / (rows / 1_000_000d);
    }
}

public final class CostHarness {
    private final Map<String, Double> byTag = new TreeMap<>();
    private final Map<String, Double> byWarehouse = new TreeMap<>();
    private final Map<String, Double> byRole = new TreeMap<>();

    void record(QueryCost c) {
        byTag.merge(c.queryTag(), c.credits(), Double::sum);
        byWarehouse.merge(c.warehouse(), c.credits(), Double::sum);
        byRole.merge(c.role(), c.credits(), Double::sum);
    }

    public String report() {
        return "by tag:        " + top(byTag)
             + "\nby warehouse: " + top(byWarehouse)
             + "\nby role:       " + top(byRole);
    }
}
```

```sql
-- attribute everything, from the start
ALTER SESSION SET QUERY_TAG = 'lab09_load_orders';
ALTER WAREHOUSE wh_load SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE wh_load SET AUTO_RESUME = TRUE;
ALTER WAREHOUSE wh_load SET INITIALLY_SUSPENDED = TRUE;
```

### Stretch
- Compare a materialized view against a dynamic table on cost and latency.
- Add a `CLUSTER BY` on a second key and measure write amplification.
- Build a credit budget alert at 50% / 80% / 100% of the month.

## Deliverables
- [ ] Five schemas with a documented layer contract each
- [ ] Stage + file format, then a clustered internal table
- [ ] Idempotent `MERGE` transform, re-runnable with zero net change
- [ ] Dynamic table with a 5-minute target latency
- [ ] Masking + row access policy proving least privilege
- [ ] Cost harness attributing credits by tag, warehouse, and role
- [ ] Warehouse sizing note for ELT vs BI
