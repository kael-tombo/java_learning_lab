# Data Warehousing — MINI PROJECT

## Project: Retail Star Schema + Query Workbench

Build a dimensional model in DuckDB (or H2 in column mode) and a CLI that
answers business questions while reporting how many bytes each query touched.

### Scope
- Facts: `fact_sales` (grain: one order line), `fact_inventory_snapshot` (grain: sku x day x warehouse).
- Dimensions: `dim_date`, `dim_product` (SCD2), `dim_customer` (SCD2), `dim_store`, `dim_promotion`.
- Materialized view: `agg_sales_daily_product`.
- Workbench: each question prints answer, runtime, and bytes scanned.

### Architecture

```
dim_date  dim_product  dim_customer  dim_store  dim_promotion
     \          |            |           |             /
      \         |            |           |            /
                [ fact_sales ]  <-- grain: order line
                     |
         [ agg_sales_daily_product ]
                     |
              query_workbench (answers + cost report)
```

### DDL

```sql
CREATE TABLE fact_sales (
  order_line_id  BIGINT,
  order_id       BIGINT,
  date_key       INT,       -- yyyymmdd, FK to dim_date
  product_sk     BIGINT,    -- FK to dim_product (SCD2 surrogate)
  customer_sk    BIGINT,
  store_sk       BIGINT,
  promotion_sk   BIGINT,
  quantity       INT,
  gross_amount   DECIMAL(12,2),
  discount_amount DECIMAL(12,2),
  net_amount     DECIMAL(12,2)
);

CREATE TABLE agg_sales_daily_product AS  -- materialized aggregate
SELECT date_key, product_sk, SUM(quantity) AS units, SUM(net_amount) AS revenue
  FROM fact_sales GROUP BY date_key, product_sk;
```

### The SCD2-aware fact join

A fact row must join to the dimension version valid at the time of the sale.
Getting this wrong silently attributes revenue to the wrong segment.

```java
public record ProductDim(long sk, long productId, String name, String segment,
                         Instant validFrom, Instant validTo) {}

public static Optional<ProductDim> dimAt(ProductDim[] versions, long productId, Instant soldAt) {
    return Arrays.stream(versions)
        .filter(v -> v.productId() == productId)
        .filter(v -> !v.validFrom().isAfter(soldAt))
        .filter(v -> v.validTo() == null || v.validTo().isAfter(soldAt))
        .findFirst();
}
```

### Workbench with cost accounting

```java
public record Answer(String question, String result, long millis, long bytesScanned) {}

public Answer ask(Connection c, String label, String sql) throws SQLException {
    long t0 = System.nanoTime();
    long before = BytesScanned.total();
    try (Statement st = c.createStatement(); ResultSet rs = st.executeQuery(sql)) {
        String result = rs.next() ? rs.getString(1) : "(empty)";
        return new Answer(label, result,
                (System.nanoTime() - t0) / 1_000_000, BytesScanned.total() - before);
    }
}
```

```sql
-- question: top 5 products by revenue in the last 30 days (aggregate, prunes to 30 partitions)
SELECT p.name, SUM(a.revenue) AS rev
  FROM agg_sales_daily_product a
  JOIN dim_date d    ON d.date_key = a.date_key
  JOIN dim_product p ON p.product_sk = a.product_sk
 WHERE d.full_date >= CURRENT_DATE - 30
 GROUP BY p.name ORDER BY rev DESC LIMIT 5;
```

### Stretch
- Swap the aggregate for the raw fact and plot runtime vs scanned bytes.
- Add a `COUNT(DISTINCT customer_sk)` metric and explain why the number moved.
- Compress the fact with dictionary encoding for low-cardinality columns and re-measure.

## Deliverables
- [ ] Star schema with the grain documented per fact table
- [ ] Two SCD2 dimensions and a correct time-travel join
- [ ] Workbench printing answers, runtime, and bytes scanned per question
- [ ] One aggregate that measurably beats the raw fact query
- [ ] Storage/row estimate with compression notes
