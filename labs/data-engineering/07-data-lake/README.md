# Data Lake

## Overview
A data lake is a centralized repository that stores all structured and unstructured data at any scale, supporting schema-on-read, diverse data types, and the lakehouse architecture.

## Key Concepts
- **Delta Lake**: ACID transactions on data lakes with time travel
- **Apache Iceberg**: Table format for managing large analytic datasets
- **Apache Hudi**: Incremental processing and record-level updates
- **Lakehouse**: Data lake + warehouse capabilities

## Java/Spark Example
`java
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

public class DataLakeExample {
    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
            .appName("DataLakeExample")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .getOrCreate();

        // Write as Delta table (ACID compliant)
        Dataset<Row> data = spark.read().json("s3://raw-data/events/");
        data.write().format("delta").mode("append")
            .partitionBy("event_date")
            .save("s3://data-lake/bronze/events/");

        // Read historical version (time travel)
        spark.read().format("delta")
            .option("versionAsOf", 5)
            .load("s3://data-lake/bronze/events/")
            .show();
    }
}
`
"@

System.Collections.Hashtable["THEORY.md"] = @"
# Data Lake Theory

## Architecture Layers
### Bronze (Raw)
- Immutable raw data ingestion
- Original format preserved
- Schema-on-read
- Partitioned by ingestion date

### Silver (Cleaned)
- Data cleaned and deduplicated
- Schema enforced
- Joins across datasets
- Quality filtered

### Gold (Aggregated)
- Business-level aggregations
- Denormalized for analytics
- Materialized views
- Ready for consumption

## Table Formats
| Feature | Delta Lake | Iceberg | Hudi |
|---------|-----------|---------|------|
| ACID | Yes | Yes | Yes |
| Time Travel | Yes | Yes | Yes |
| Schema Evolution | Yes | Yes | Yes |
| Partition Evolution | No | Yes | Yes |
| Merge/Upsert | Yes | Yes | Yes |
| Performance | Fast | Fast | Fast |
