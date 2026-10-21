# How Data Lakes Work

## Medallion Architecture Implementation
`java
public class MedallionPipeline {

    public void bronzeToSilver() {
        // Bronze: Read raw data
        Dataset<Row> bronze = spark.read().format("delta")
            .load("s3://lake/bronze/events/");

        // Silver: Clean and validate
        Dataset<Row> silver = bronze
            .filter(col("event_type").isNotNull())
            .withColumn("event_date", to_date(col("timestamp")))
            .dropDuplicates("event_id")
            .withColumn("etl_processed_at", current_timestamp());

        silver.write().format("delta")
            .mode("append")
            .partitionBy("event_date")
            .save("s3://lake/silver/events/");
    }

    public void silverToGold() {
        Dataset<Row> silver = spark.read().format("delta")
            .load("s3://lake/silver/events/");

        Dataset<Row> gold = silver
            .groupBy("event_date", "event_type")
            .agg(
                count("*").as("event_count"),
                countDistinct("user_id").as("unique_users")
            );

        gold.write().format("delta")
            .mode("overwrite")
            .save("s3://lake/gold/event_aggregates/");
    }
}
`

## Delta Lake Time Travel
`java
// Read as of specific version
spark.read().format("delta")
    .option("versionAsOf", 25)
    .load("/delta/table");

// Read as of timestamp
spark.read().format("delta")
    .option("timestampAsOf", "2024-01-15")
    .load("/delta/table");

// Vacuum old versions
spark.sql("VACUUM delta./delta/table RETAIN 168 HOURS");
`

## Iceberg Tables
`java
spark.conf().set("spark.sql.catalog.my_catalog", "org.apache.iceberg.spark.SparkCatalog");
spark.conf().set("spark.sql.catalog.my_catalog.type", "hadoop");
spark.conf().set("spark.sql.catalog.my_catalog.warehouse", "s3://lake/iceberg/");

Dataset<Row> df = spark.read().json("input/");
df.writeTo("my_catalog.db.events")
    .partitionedBy(Expressions.days("timestamp"))
    .create();
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# Data Lake Internals

## Delta Lake Transaction Log
`java
/*
Delta Lake uses a transaction log (JSON files in _delta_log/) to track:
- Add/remove file actions
- Schema changes
- Commit info
- Checkpoint files

_log/00000000000000000001.json
_log/00000000000000000002.json
...
_log/00000000000000000010.checkpoint.parquet
*/
`

## File Layout
`
s3://data-lake/
  bronze/
    events/
      event_date=2024-01-01/
        part-00001.snappy.parquet
        part-00002.snappy.parquet
      _delta_log/
        00000000000000000001.json
  silver/
    events/
      event_date=2024-01-01/
        part-00001.snappy.parquet
      _delta_log/
        00000000000000000001.json
`

## Iceberg Manifest Files
`java
/*
Iceberg metadata:
metadata/v1.metadata.json  - Table schema, partition spec, snapshots
metadata/snap-123.avro     - Manifest list (pointing to manifest files)
metadata/manifest-456.avro - Data file locations and stats
*/
`
"@

System.Collections.Hashtable["MATH_FOUNDATION.md"] = @"
# Math Foundation for Data Lakes

## Storage Calculations
`
Raw Capacity = Sum(SourceDataSizes) * Replication
Compressed = RawCapacity / CompressionRatio (3-10x)
Effective = Compressed * (1 + MetadataOverhead)

Bronze: Raw (stays at Raw)
Silver: Compressed (clean, deduplicated)
Gold: Aggregated (much smaller)
`

## Cost Analysis
`
Storage Cost = DataSize * $/GB/month * Replication
Compute Cost = ScanCost * QueryCount + TransformCost * PipelineRuns
Total Cost = StorageCost + ComputeCost + MetadataCost + EGRESS

Data Lake Cost vs Warehouse:
- Storage: 10-100x cheaper
- Compute: Same or higher (more raw data scanned)
- Net: 2-5x cheaper overall
`

## File Size Optimization
`
OptimalFileSize = HDFSBlockSize * 1.5 = ~192MB
FileCount = TotalData / OptimalFileSize
SmallFileProblem = Files < BlockSize * 0.5

Compaction = Merge small files into optimal sizes
Target: Files between 64MB and 1GB
`
"@

System.Collections.Hashtable["VISUAL_GUIDE.md"] = @"
# Visual Guide to Data Lakes

## Medallion Architecture
`
Source Data
   |
   v
+---------------------------------------+
|  BRONZE (Raw)                         |
|  S3://lake/bronze/                    |
|  events/ event_date=YYYY-MM-DD/       |
|  logs/   event_date=YYYY-MM-DD/       |
|  - Immutable, schema-on-read          |
|  - Original format preserved          |
+---------------------------------------+
   |
   | Cleaning, dedup, validation
   v
+---------------------------------------+
|  SILVER (Cleaned)                     |
|  S3://lake/silver/                    |
|  events/ event_date=YYYY-MM-DD/       |
|  - Deduplicated, schema enforced      |
|  - Joined across sources              |
|  - Standardized data types            |
+---------------------------------------+
   |
   | Aggregation, business logic
   v
+---------------------------------------+
|  GOLD (Aggregated)                    |
|  S3://lake/gold/                      |
|  daily_active_users/                  |
|  revenue_by_region/                   |
|  - Business-level metrics             |
|  - Denormalized for BI               |
|  - Read-optimized                     |
+---------------------------------------+
`

## Delta Lake Transaction Log
`
Time -->
v1: INSERT file1.parquet -> add file1
v2: INSERT file2.parquet -> add file2
v3: UPDATE -> remove file1, add file3.parquet
v4: DELETE -> remove file2
v5: COMPACTION -> remove files, add big-file.parquet

Read at v2: file1 + file2
Read at v4: file3 (after update and delete)
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: Data Lake Operations

## Delta Lake Operations
`java
public class DeltaLakeOperations {

    // Upsert (Merge)
    public void upsertEvents(Dataset<Row> updates, String tablePath) {
        updates.createOrReplaceTempView("updates");
        spark.sql(String.format("""
            MERGE INTO delta.%s t
            USING updates s ON t.event_id = s.event_id
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
            """, tablePath));
    }

    // Time travel query
    public Dataset<Row> readAsOf(String tablePath, long version) {
        return spark.read().format("delta")
            .option("versionAsOf", version)
            .load(tablePath);
    }

    // Vacuum (clean up old files)
    public void vacuum(String tablePath, int retentionHours) {
        spark.sql(String.format("VACUUM delta.%s RETAIN %d HOURS",
            tablePath, retentionHours));
    }

    // Describe history
    public Dataset<Row> getHistory(String tablePath) {
        return spark.sql(String.format("DESCRIBE HISTORY delta.%s", tablePath));
    }

    // Optimize (compact small files)
    public void optimizeTable(String tablePath) {
        spark.sql(String.format("OPTIMIZE delta.%s", tablePath));
    }

    // Z-order clustering
    public void zorderBy(String tablePath, String... columns) {
        String cols = String.join(", ", columns);
        spark.sql(String.format("OPTIMIZE delta.%s ZORDER BY (%s)",
            tablePath, cols));
    }
}
`

## Schema Evolution
`java
public class SchemaEvolution {
    public void evolveSchema() {
        // Auto-merge schema
        spark.sql("SET spark.databricks.delta.schema.autoMerge.enabled = true");

        // Manual schema evolution
        spark.sql(String.format("""
            ALTER TABLE delta.%s ADD COLUMNS (new_column STRING AFTER existing_column)
            """, tablePath));
    }
}
`

## Iceberg API
`java
public class IcebergOperations {
    public void createIcebergTable() {
        spark.sql("CREATE TABLE prod.db.events (" +
            "event_id BIGINT, event_type STRING, ts TIMESTAMP) " +
            "USING iceberg " +
            "PARTITIONED BY (days(ts))");
    }

    public void incrementalRead() {
        Dataset<Row> increment = spark.read()
            .format("iceberg")
            .option("snapshot-id", 123456789L)
            .load("prod.db.events");
    }
}
`
"@

System.Collections.Hashtable["STEP_BY_STEP.md"] = @"
# Step-by-Step Data Lake Setup

## Step 1: Choose Storage
- AWS S3, Azure ADLS, Google GCS, or HDFS
- Set up bucket/container structure
- Implement lifecycle policies

## Step 2: Set Up Table Format
`java
SparkSession.builder()
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .getOrCreate();
`

## Step 3: Bronze Layer Ingestion
`java
Dataset<Row> raw = spark.read().json("s3://source/");
raw.write().format("delta").mode("append")
    .partitionBy("ingestion_date")
    .save("s3://lake/bronze/data/");
`

## Step 4: Silver Layer Processing
`java
Dataset<Row> bronze = spark.read().format("delta")
    .load("s3://lake/bronze/data/");
Dataset<Row> silver = bronze
    .dropDuplicates("id")
    .filter(col("status").isNotNull())
    .withColumn("etl_ts", current_timestamp());
silver.write().format("delta").mode("append")
    .save("s3://lake/silver/data/");
`

## Step 5: Gold Layer Aggregation
`java
Dataset<Row> gold = spark.read().format("delta")
    .load("s3://lake/silver/data/")
    .groupBy("dimension")
    .agg(sum("metric").as("total"));
gold.write().format("delta").mode("overwrite")
    .save("s3://lake/gold/aggregates/");
`

## Step 6: Set Up Catalog
`sql
CREATE DATABASE IF NOT EXISTS my_catalog.bronze;
CREATE DATABASE IF NOT EXISTS my_catalog.silver;
CREATE DATABASE IF NOT EXISTS my_catalog.gold;
`
"@

System.Collections.Hashtable["COMMON_MISTAKES.md"] = @"
# Common Data Lake Mistakes

## 1. Data Lake = Data Swamp
`java
// WRONG - no organization, no catalog
spark.read().json("s3://data/some-random-path/");

// RIGHT - organized medallion architecture
spark.table("bronze.events");
spark.table("silver.events");
spark.table("gold.daily_metrics");
`

## 2. No Partitioning
`java
// WRONG - no partitioning
data.write().format("delta").save("s3://lake/data/");

// RIGHT - partitioned
data.write().format("delta")
    .partitionBy("year", "month", "day")
    .save("s3://lake/data/");
`

## 3. Too Many Small Files
`java
// WRONG - thousands of tiny files
spark.conf().set("spark.sql.files.maxPartitionBytes", "1MB");

// RIGHT - optimal file sizes
spark.conf().set("spark.sql.files.maxPartitionBytes", "128MB");
// Run compaction
spark.sql("OPTIMIZE delta./path");
`

## 4. No Data Lifecycle
`java
// WRONG - keep everything forever
// Costs grow unbounded

// RIGHT - implement lifecycle
spark.sql("VACUUM delta./bronze RETAIN 30 DAYS");
`
"@

System.Collections.Hashtable["DEBUGGING.md"] = @"
# Debugging Data Lakes

## Common Issues

### Delta Lake Transaction Log Conflicts
`java
// Conflicting writes to same Delta table
// Multiple writers without proper isolation

// Fix: Use separate partition directories
data.write().format("delta").mode("append")
    .partitionBy("event_date")
    .save("s3://lake/events/");
`

### Iceberg Metadata Issues
`java
// Large metadata overhead
// Fix: Regular metadata compaction
spark.sql("CALL iceberg.system.rewrite_manifests('db.table')");
`

### Partition Pruning Not Working
`java
// Check if predicates are pushed down
spark.read().format("delta")
    .load("s3://lake/bronze/events/")
    .filter("event_date = '2024-01-01'")
    .explain("formatted");
// Look for: PushedFilters, PartitionFilters
`
"@

System.Collections.Hashtable["REFACTORING.md"] = @"
# Refactoring Data Lakes

## From Ad-hoc to Medallion
`java
// BEFORE: Random paths, no structure
spark.read().parquet("s3://data/sales_march.parquet");
spark.read().json("s3://data/export_20240301.json");

// AFTER: Structured medallion
spark.table("bronze.sales");
spark.table("bronze.export_logs");
`

## From No ACID to Delta Lake
`java
// BEFORE: Parquet files with no transactions
data.write().mode("overwrite").parquet("s3://data/");

// AFTER: Delta Lake with ACID
data.write().format("delta").mode("append")
    .save("s3://lake/bronze/sales/");
`
"@

System.Collections.Hashtable["PERFORMANCE.md"] = @"
# Data Lake Performance

## Optimization Techniques

### Compaction
`java
// Merge small files
spark.sql("OPTIMIZE delta./path");
spark.sql("OPTIMIZE delta./path WHERE date >= '2024-01-01'");

// Z-order clustering
spark.sql("OPTIMIZE delta./path ZORDER BY (customer_id, product_id)");
`

### Partition Pruning
`java
// Filter on partition columns for performance
Dataset<Row> result = spark.read().format("delta")
    .load("s3://lake/bronze/events/")
    .filter("event_date >= '2024-01-01' AND event_date < '2024-02-01'");
// Only scans January 2024 partitions
`

### File Sizing
`java
// Target: 64MB - 1GB files
spark.conf().set("spark.sql.files.maxPartitionBytes", "134217728"); // 128MB
spark.conf().set("spark.sql.files.openCostInBytes", "134217728");

// Optimal file count
int fileCount = totalDataSize / targetFileSize;
spark.conf().set("spark.sql.shuffle.partitions", fileCount);
`
"@

System.Collections.Hashtable["SECURITY.md"] = @"
# Data Lake Security

## Access Control
`java
// Bucket policies (AWS S3 example)
{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::account:role/DataEngineer"},
    "Action": ["s3:GetObject", "s3:ListBucket"],
    "Resource": ["arn:aws:s3:::lake/bronze/*", "arn:aws:s3:::lake"]
}
`

## Column-Level Security
`java
// Create views with masked columns
spark.sql("CREATE VIEW silver.employees_safe AS " +
    "SELECT id, name, department, " +
    "  CONCAT(LEFT(ssn, 4), '***-****') as ssn_masked, " +
    "  CONCAT(LEFT(email, 3), '***') as email_masked " +
    "FROM silver.employees");
`

## Encryption
`java
// Server-side encryption (S3 SSE-S3 or SSE-KMS)
// Client-side encryption before writing
data.write().format("delta")
    .option("delta.autoOptimize.optimizeWrite", "true")
    .save("s3://lake/silver/pii/");
`

## Audit
`java
// Delta Lake table history
spark.sql("DESCRIBE HISTORY delta./lake/silver/employees");
// Shows who, what, when for all changes
`
"@

System.Collections.Hashtable["ARCHITECTURE.md"] = @"
# Data Lake Architecture

## Lakehouse Architecture
`
+------------------------------------------+
|       BI Tools & Analytics               |
|  Tableau | Power BI | Databricks SQL     |
+------------------------------------------+
|        Catalog & Governance               |
|  Unity Catalog | AWS Glue | Hive Meta    |
+------------------------------------------+
|          Gold Layer (Aggregated)          |
|  Sales Summary | Customer 360 | KPIs      |
+------------------------------------------+
|          Silver Layer (Cleaned)           |
|  Events | Users | Transactions            |
+------------------------------------------+
|          Bronze Layer (Raw)               |
|  Logs | API Events | DB Snapshots         |
+------------------------------------------+
|         Storage (S3 / ADLS / GCS)         |
|  Parquet / Delta / Iceberg / Hudi        |
+------------------------------------------+
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# Data Lake Exercises

## Exercise 1: Bronze Layer Ingestion
Set up a Delta Lake table that ingests JSON events from S3 with proper partitioning.

## Exercise 2: Silver Layer Processing
Clean and deduplicate the bronze data to create a silver layer.

## Exercise 3: Time Travel
Implement a point-in-time query using Delta Lake time travel.

## Exercise 4: Merge/Upsert
Implement upsert logic to handle late-arriving data in Delta Lake.

## Exercise 5: Iceberg Tables
Create and query an Iceberg table with partition evolution.
