# How Data Warehousing Works

## ETL into Warehouse
`java
@Component
public class WarehouseEtl {
    public void loadDimension(Dataset<Row> source, String table, String key) {
        source.createOrReplaceTempView("src");
        spark.sql(String.format("""
            MERGE INTO wh.%s t
            USING src s ON t.%s = s.%s
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
            """, table, key, key));
    }

    public void loadFact(Dataset<Row> source, String table) {
        source.write()
            .mode("append")
            .format("delta")
            .partitionBy("year", "month")
            .saveAsTable("wh." + table);
    }
}
`

## Query Optimization
`java
// Materialized views for common queries
spark.sql("""
    CREATE MATERIALIZED VIEW wh.mv_monthly_sales AS
    SELECT d.region, d.category,
           DATE_TRUNC('month', f.date) as month,
           SUM(f.amount) as revenue
    FROM wh.fact_sales f
    JOIN wh.dim_store d ON f.store_id = d.id
    GROUP BY d.region, d.category, DATE_TRUNC('month', f.date)
""");
`

## Partition Pruning
`java
// Partition-aware queries
Dataset<Row> result = spark.table("wh.fact_sales")
    .filter("year = 2024 AND month = 6 AND day BETWEEN 1 AND 7")
    .agg(sum("amount").as("weekly_revenue"));
// Only scans 7 partitions instead of full table
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# Data Warehouse Internals

## Storage Architecture
`java
// Columnar storage format (Parquet/ORC)
// Data organized by column, not row
/*
Column: customer_id     Column: amount     Column: date
[1001, 1002, 1003]     [50.0, 75.0, 30.0]  [2024-01-01, ...]
*/
// Benefits: better compression, faster aggregation
`

## Query Engine Components
`java
@Component
public class QueryOptimizer {
    public QueryPlan optimize(String sql) {
        // 1. Parse SQL to AST
        // 2. Bind to catalog (resolve tables, columns)
        // 3. Apply optimizations (predicate pushdown, column pruning)
        // 4. Generate physical plan (join order, partition pruning)
        // 5. Execute plan
        return optimizer.execute(analyzer.resolve(parser.parse(sql)));
    }
}
`

## Indexing Strategies
`java
// Different indexing approaches
spark.sql("CREATE INDEX idx_fact_date ON wh.fact_sales USING BLOOM (date)");
spark.sql("CREATE INDEX idx_dim_region ON wh.dim_store USING ZORDER (region)");

// Bitmap indexes for low-cardinality columns
spark.sql("CREATE BITMAP INDEX idx_gender ON wh.dim_customer (gender)");
`
"@

System.Collections.Hashtable["MATH_FOUNDATION.md"] = @"
# Math Foundation for Data Warehousing

## Dimensional Modeling Math

### Star Join Performance
`
Query Cost = ScanCost(Fact) + LookupCost(Dim1) + ... + LookupCost(Dimn)
ScanCost(Fact) = FactRows * RowSize / IORate
LookupCost(Dim) = DictionaryLookup + (CacheHit? 0 : DiskRead)
`

### Aggregation Performance
`
Aggregation Cost = Scan + Shuffle + Reduce
- Scan: O(n) where n = fact rows
- Shuffle: O(n log n) for sort-based, O(n) for hash-based
- Reduce: O(m) where m = group count
`

### Storage Calculations
`
Raw Size = Sum(row sizes) * RowCount * ReplicationFactor
Columnar Compression = 3x to 10x reduction
Partition Pruning Savings = 1 - (QueriedPartitions / TotalPartitions)

Star Schema Size = FactSize + Sum(DimSizes)
 - Fact = ~60-80% of total warehouse size
`

## Cube Operations
`
OLAP Cube Cells = Cardinality(Dim1) * ... * Cardinality(Dimn)
Sparsity = (NonEmptyCells / TotalCells) * 100
Rollup = GroupBy(Dim1, ..., Dimn-1)
Drilldown = GroupBy(Dim1, ..., Dimn, Dimn+1)
`
"@

System.Collections.Hashtable["VISUAL_GUIDE.md"] = @"
# Visual Guide to Data Warehousing

## Star Schema Visualization
`
                          +------------------+
                          |   dim_date       |
                          +------------------+
                          | date_key PK      |
                          | date             |
                          | year             |--------+
                          | quarter          |        |
                          | month            |        |
                          | day              |        |
                          +------------------+        |
                                                      |
+------------------+         +------------------+     |
|   dim_customer   |         |   fact_sales     |     |
+------------------+         +------------------+     |
| customer_key PK  |<--------| customer_key FK  |     |
| name             |         | product_key FK   |     |
| email            |         | date_key FK      |<----+
| region           |         | store_key FK     |--+
| segment          |         | amount           |  |
+------------------+         | quantity         |  |
                             | discount         |  |
+------------------+         +------------------+  |
|   dim_product    |               ^               |
+------------------+               |               |
| product_key PK   |<--------------+               |
| product_name     |                               |
| category         |                               |
| brand            |                               |
+------------------+                               |
                                                   |
+------------------+                               |
|   dim_store      |                               |
+------------------+                               |
| store_key PK     |<------------------------------+
| store_name       |
| city             |
| state            |
| region           |
+------------------+
`

## Warehouse Architecture Layers
`
+--------------------------------------------------+
|                   BI / Analytics                   |
|  Tableau | Power BI | Looker | Custom Dashboards  |
+--------------------------------------------------+
|                 Semantic Layer                     |
|  Metric definitions | Business logic | Calculated  |
+--------------------------------------------------+
|              Data Warehouse (Core)                 |
|  Fact Tables | Dimension Tables | Aggregations    |
+--------------------------------------------------+
|                Staging Layer                       |
|  Raw Tables | Temp Tables | Error Records         |
+--------------------------------------------------+
|               Source Systems                       |
|  OLTP | APIs | SaaS | Files | Streams             |
+--------------------------------------------------+
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: Data Warehousing

## Building a Star Schema

### 1. Dimension Table DDL
`java
@Component
public class DimensionBuilder {
    public void createDimension(String name, List<DimensionAttribute> attrs) {
        StringBuilder ddl = new StringBuilder("CREATE TABLE IF NOT EXISTS wh.dim_")
            .append(name).append(" (");
        ddl.append("  ").append(name).append("_key BIGINT GENERATED ALWAYS AS IDENTITY,");
        ddl.append("  ").append(name).append("_id VARCHAR(50) NOT NULL,");
        for (DimensionAttribute attr : attrs) {
            ddl.append("  ").append(attr.getName()).append(" ")
               .append(attr.getType()).append(",");
        }
        ddl.append("  effective_date DATE NOT NULL DEFAULT CURRENT_DATE,");
        ddl.append("  end_date DATE,");
        ddl.append("  is_current BOOLEAN DEFAULT TRUE,");
        ddl.append("  PRIMARY KEY (").append(name).append("_key)");
        ddl.append(") USING DELTA");
        spark.sql(ddl.toString());
    }
}
`

### 2. Fact Table DDL
`java
@Component
public class FactTableBuilder {
    public void createFactTable(String name, List<String> dimensionKeys,
                                List<FactMeasure> measures) {
        StringBuilder ddl = new StringBuilder(
            "CREATE TABLE IF NOT EXISTS wh.fact_").append(name).append(" (");
        for (String dimKey : dimensionKeys) {
            ddl.append("  ").append(dimKey).append(" BIGINT NOT NULL,");
        }
        ddl.append("  fact_id BIGINT GENERATED ALWAYS AS IDENTITY,");
        for (FactMeasure measure : measures) {
            ddl.append("  ").append(measure.getName()).append(" ")
               .append(measure.getType()).append(",");
        }
        ddl.append("  etl_batch_id BIGINT,");
        ddl.append("  etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,");
        ddl.append("  PRIMARY KEY (fact_id)");
        ddl.append(") USING DELTA PARTITIONED BY (etl_batch_id)");
        spark.sql(ddl.toString());
    }
}
`

### 3. SCD Type 2 Implementation
`java
@Component
public class ScdType2Processor {
    public void processSlowlyChangingDimension(Dataset<Row> source,
                                                String table, List<String> trackedCols) {
        source.createOrReplaceTempView("src");
        spark.sql(String.format("""
            MERGE INTO wh.%s t
            USING src s ON t.%s_id = s.%s_id AND t.is_current = TRUE
            WHEN MATCHED AND (%s) THEN UPDATE SET
                t.end_date = CURRENT_DATE,
                t.is_current = FALSE
            WHEN NOT MATCHED THEN INSERT (
                %s_id, %s, effective_date, is_current
            ) VALUES (
                s.%s_id, %s, CURRENT_DATE, TRUE
            )
            """,
            table, table, table,
            trackedCols.stream()
                .map(c -> String.format("t.%s != s.%s", c, c))
                .collect(Collectors.joining(" OR ")),
            table, String.join(", ", trackedCols),
            table, String.join(", ",
                trackedCols.stream().map(c -> "s." + c)
                    .collect(Collectors.toList()))));
    }
}
`

### 4. OLAP Query Service
`java
@RestController
@RequestMapping("/api/olap")
public class OlapController {
    private final SparkSession spark;

    @PostMapping("/query")
    public ResponseEntity<QueryResult> executeOlap(@RequestBody OlapQuery query) {
        String sql = buildOlapQuery(query);
        Dataset<Row> result = spark.sql(sql);
        List<Row> rows = result.collectAsList();
        return ResponseEntity.ok(new QueryResult(
            rows.size(), rows, result.columns()));
    }

    private String buildOlapQuery(OlapQuery q) {
        return String.format(
            "SELECT %s FROM %s WHERE %s GROUP BY %s ORDER BY %s",
            q.getMeasures() + ", " + q.getDimensions(),
            q.getFactTable() + " " + q.getJoins(),
            q.getFilters(),
            q.getDimensions(),
            q.getOrderBy());
    }
}
`
"@

System.Collections.Hashtable["STEP_BY_STEP.md"] = @"
# Step-by-Step Data Warehouse Setup

## Step 1: Source Analysis
1. Identify business processes (Sales, Inventory, HR)
2. Define grain for each fact table
3. Identify dimensions and hierarchies
4. Map source fields to warehouse schema

## Step 2: Schema Design
`sql
-- Design conformed dimensions
CREATE TABLE dim_customer (
    customer_key BIGINT IDENTITY,
    customer_id VARCHAR(50),
    name VARCHAR(200),
    email VARCHAR(200),
    segment VARCHAR(50),
    effective_date DATE,
    is_current BOOLEAN
);

CREATE TABLE fact_orders (
    order_key BIGINT IDENTITY,
    customer_key BIGINT REFERENCES dim_customer,
    product_key BIGINT REFERENCES dim_product,
    date_key BIGINT REFERENCES dim_date,
    store_key BIGINT REFERENCES dim_store,
    order_amount DECIMAL(12,2),
    quantity INT,
    discount DECIMAL(5,2)
);
`

## Step 3: Build ETL Pipeline
`java
@Component
public class WarehousePipeline {
    public void execute() {
        loadDimensions();
        establishForeignKeys();
        loadFactTables();
        buildAggregations();
        refreshMaterializedViews();
    }
}
`

## Step 4: Create Aggregations
`java
// Pre-aggregate for performance
spark.sql("CREATE TABLE wh.agg_daily_sales AS " +
    "SELECT date, store_id, SUM(amount) as daily_total " +
    "FROM wh.fact_sales GROUP BY date, store_id");
`

## Step 5: Set Up Access Control
`sql
GRANT SELECT ON wh.fact_sales TO role_analyst;
GRANT SELECT ON wh.agg_daily_sales TO role_analyst;
GRANT SELECT, INSERT, UPDATE ON wh.dim_customer TO role_etl;
`
"@

System.Collections.Hashtable["COMMON_MISTAKES.md"] = @"
# Common Data Warehousing Mistakes

## 1. Wrong Grain
`sql
-- WRONG: Too coarse
CREATE TABLE fact_sales (date, total_amount);

-- RIGHT: Right grain for business process
CREATE TABLE fact_sales (date, product_id, store_id, customer_id, amount, quantity);
`

## 2. No Conformed Dimensions
`sql
-- WRONG: Different definitions across marts
dim_customer.segment = 'VIP' | 'Regular'  -- Sales mart
dim_customer.tier = 'Gold' | 'Silver' | 'Bronze'  -- Marketing mart

-- RIGHT: Conformed definition
dim_customer.segment = 'Premium' | 'Standard' | 'Basic'
`

## 3. Over-Normalization
`sql
-- WRONG: Too many joins
fact -> dim_address -> dim_city -> dim_state -> dim_country

-- RIGHT: Denormalized for query performance
fact -> dim_address (includes city, state, country)
`

## 4. Ignoring Historical Changes
`sql
-- WRONG: Overwrites history
MERGE INTO dim_customer ... WHEN MATCHED THEN UPDATE SET ...

-- RIGHT: SCD Type 2 for tracked attributes
MERGE INTO dim_customer ... WHEN MATCHED AND has_changes THEN
    UPDATE SET end_date = today, is_current = false
`
"@

System.Collections.Hashtable["DEBUGGING.md"] = @"
# Debugging Data Warehouse Issues

## Common Problems

### Slow Queries
`sql
-- Check query plan
EXPLAIN ANALYZE
SELECT region, SUM(amount)
FROM fact_sales JOIN dim_store USING (store_key)
WHERE date >= '2024-01-01'
GROUP BY region;

-- Look for: Full table scans, missing partition pruning, bad join order
`

### Data Integrity Issues
`java
// Check for orphan facts
Dataset<Row> orphans = spark.sql("""
    SELECT COUNT(*) FROM fact_sales f
    LEFT JOIN dim_customer c ON f.customer_key = c.customer_key
    WHERE c.customer_key IS NULL
""");
`

### Refresh Issues
`java
// Verify materialized view freshness
spark.sql("SELECT MAX(etl_loaded_at) FROM wh.fact_sales").show();
// Compare to source max timestamp
spark.sql("SELECT MAX(updated_at) FROM source.orders").show();
`

### Space Issues
`sql
-- Identify large tables
SELECT table_name, size_in_bytes / 1073741824 as size_gb
FROM information_schema.tables
WHERE table_schema = 'wh'
ORDER BY size_in_bytes DESC;
`
"@

System.Collections.Hashtable["REFACTORING.md"] = @"
# Refactoring Data Warehouse

## Before: Flat Tables
`sql
CREATE TABLE sales_wide (
    transaction_id, date, customer_name, customer_email,
    customer_region, product_name, product_category,
    store_name, store_city, store_state, amount, quantity
);
-- Problems: Data redundancy, update anomalies, high storage
`

## After: Star Schema
`sql
CREATE TABLE dim_customer (customer_key, customer_id, name, email, region);
CREATE TABLE dim_product (product_key, product_id, name, category);
CREATE TABLE dim_store (store_key, store_id, name, city, state);
CREATE TABLE fact_sales (customer_key, product_key, store_key, date_key, amount, quantity);
`

## Before: No Partitions
`sql
SELECT ... FROM fact_sales WHERE date >= '2024-01-01';
-- Full table scan on 5TB table
`

## After: Partitioned
`sql
CREATE TABLE fact_sales (...) PARTITIONED BY (year, month);
SELECT ... FROM fact_sales WHERE year = 2024 AND month >= 1;
-- Scans only 1/12 of data
`
"@

System.Collections.Hashtable["PERFORMANCE.md"] = @"
# Data Warehouse Performance

## Query Optimization Techniques

### Materialized Views
`java
// Create pre-computed aggregations
spark.sql("CREATE MATERIALIZED VIEW wh.mv_product_monthly AS " +
    "SELECT product_key, DATE_TRUNC('month', date) as month, " +
    "SUM(amount) as revenue, COUNT(*) as transactions " +
    "FROM wh.fact_sales GROUP BY product_key, DATE_TRUNC('month', date)");
`

### Optimized Join Order
`java
// Push down filters before join
Dataset<Row> optimized = spark.sql("""
    SELECT /*+ BROADCAST(d) */ f.amount, d.region
    FROM fact_sales f
    JOIN dim_store d ON f.store_key = d.store_key
    WHERE f.year = 2024
""");
`

### Compression
`java
// Optimize storage
spark.sql("ALTER TABLE wh.fact_sales SET TBLPROPERTIES " +
    "('delta.autoOptimize.optimizeWrite' = 'true', " +
    "'delta.autoOptimize.autoCompact' = 'true')");
`

### Clustering
`java
// Optimize data layout for common query patterns
spark.sql("CLUSTER BY (store_key, date)");
spark.sql("OPTIMIZE wh.fact_sales ZORDER BY (customer_key, product_key)");
`
"@

System.Collections.Hashtable["SECURITY.md"] = @"
# Data Warehouse Security

## Access Control
`sql
-- Role-based access
CREATE ROLE analyst;
CREATE ROLE etl_admin;
CREATE ROLE reporting;

GRANT SELECT ON wh.fact_sales TO analyst;
GRANT SELECT, INSERT, UPDATE ON wh.dim_customer TO etl_admin;
GRANT SELECT ON wh.agg_monthly TO reporting;
`

## Column-Level Security
`java
// Mask sensitive columns
spark.sql("CREATE OR REPLACE VIEW wh.vw_customer_safe AS " +
    "SELECT customer_key, name, " +
    "  CONCAT(LEFT(email, 3), '***@***') as email_masked, " +
    "  region, segment " +
    "FROM wh.dim_customer");
`

## Audit Logging
`java
@Component
public class WarehouseAudit {
    @EventListener
    public void onQuery(WarehouseQueryEvent event) {
        auditLog.insert(new AuditRecord(
            event.getUser(), event.getSql(),
            event.getTimestamp(), event.getDuration()));
    }
}
`

## Encryption at Rest
`properties
# Enable encryption
spark.sql.warehouse.encryption.enabled=true
spark.sql.warehouse.encryption.key=
`
"@

System.Collections.Hashtable["ARCHITECTURE.md"] = @"
# Data Warehouse Architecture

## Modern Warehouse Architecture
`
+--------------------------------------------------+
|                  Consumption Layer                 |
|  Dashboards | Reports | ML Models | Data Science  |
+--------------------------------------------------+
|                  Access Layer                      |
|  SQL Endpoint | JDBC/ODBC | REST API | GraphQL    |
+--------------------------------------------------+
|                 Compute Layer                      |
|  Query Engine | MPP Engine | Spark Engine         |
+--------------------------------------------------+
|                 Storage Layer                      |
|  Fact Tables | Dim Tables | Aggregations | Views   |
|  Delta Lake / Iceberg / Parquet / ORC             |
+--------------------------------------------------+
|                Ingestion Layer                     |
|  Batch ETL | Stream Processing | CDC Connectors   |
+--------------------------------------------------+
|                Source Systems                      |
|  OLTP DBs | APIs | SaaS | Files | IoT Streams     |
+--------------------------------------------------+
`

## Spring Boot Integration
`java
@SpringBootApplication
public class WarehouseApplication {
    public static void main(String[] args) {
        SpringApplication.run(WarehouseApplication.class, args);
    }

    @Bean
    public DataSource warehouseDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:spark://warehouse:443/default")
            .driverClass("org.apache.spark.sql.jdbc.SparkDialect")
            .build();
    }
}
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# Data Warehousing Exercises

## Exercise 1: Design a Star Schema
Design a star schema for an e-commerce platform with Customers, Products, Orders, and Payments.

## Exercise 2: Implement SCD Type 2
Build a dimension table that tracks customer address changes over time.

## Exercise 3: Create Materialized Views
Pre-compute monthly sales aggregations by region and product category.

## Exercise 4: Optimize Query Performance
Use explain plans to identify and fix a slow-running query.

## Exercise 5: Build an OLAP API
Create a REST API that supports dynamic dimension drill-down and roll-up operations.
