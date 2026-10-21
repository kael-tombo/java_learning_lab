# ETL Processes

## Overview
ETL (Extract, Transform, Load) is the core process of data engineering - extracting data from sources, transforming it into a usable format, and loading it into a target system.

## Key Concepts
- **Extraction**: Reading data from various source systems
- **Transformation**: Cleaning, enriching, and restructuring data
- **Loading**: Writing processed data to the target destination

## Java/Spark Example
`java
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.functions;

public class EtlJob {
    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
            .appName("ETLJob")
            .master("local[*]")
            .getOrCreate();

        // Extract
        Dataset<Row> source = spark.read()
            .option("header", "true")
            .csv("s3://source-bucket/raw/");

        // Transform
        Dataset<Row> transformed = source
            .withColumn("processed_date", functions.current_date())
            .withColumn("amount_cleaned",
                functions.regexp_replace(functions.col("amount"), "[$,]", "").cast("decimal(10,2)"))
            .filter("amount_cleaned > 0")
            .dropDuplicates("transaction_id");

        // Load
        transformed.write()
            .mode("append")
            .parquet("s3://target-bucket/etl-output/");

        spark.stop();
    }
}
`
"@

System.Collections.Hashtable["THEORY.md"] = @"
# Theory of ETL Processes

## ETL Architecture
ETL pipelines follow a three-phase architecture:

### 1. Extract Phase
- **Full Extraction**: Read entire source data each run
- **Incremental Extraction**: Read only changed data since last run
- **Change Data Capture**: Capture inserts, updates, deletes

### 2. Transform Phase
- **Cleaning**: Remove nulls, deduplicate, standardize formats
- **Validation**: Check data types, ranges, referential integrity
- **Enrichment**: Join with reference data, calculate derived fields
- **Aggregation**: Summarize, compute metrics

### 3. Load Phase
- **Full Load**: Truncate and reload entire target
- **Incremental Load**: Append only new/changed records
- **Upsert/Merge**: Insert or update based on key match

## ELT vs ETL
| Aspect | ETL | ELT |
|--------|-----|-----|
| Transform location | Staging area | Target warehouse |
| Data volume | Lower | Higher |
| Transformation power | Dedicated engine | Warehouse compute |
| Schema flexibility | Transform before load | Transform after load |
| Typical tools | Spark, Spring Batch | dbt, Snowflake, BigQuery |
