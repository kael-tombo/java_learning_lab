# Apache Spark

## Overview
Apache Spark is a unified, distributed data processing engine for large-scale data analytics, supporting batch processing, streaming, SQL, machine learning, and graph processing.

## Key Concepts
- **RDD**: Resilient Distributed Dataset - immutable, partitioned collection
- **DataFrame**: Distributed collection of rows with schema
- **Spark SQL**: SQL interface for structured data
- **Catalyst Optimizer**: Query optimization engine
- **Tungsten**: Off-heap memory and code generation

## Java Example
`java
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

public class SparkExample {
    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
            .appName("SparkExample")
            .config("spark.sql.adaptive.enabled", "true")
            .getOrCreate();

        Dataset<Row> df = spark.read()
            .option("header", "true")
            .csv("data.csv");

        df.createOrReplaceTempView("data");
        Dataset<Row> result = spark.sql(
            "SELECT category, AVG(value) as avg_value " +
            "FROM data GROUP BY category ORDER BY avg_value DESC");
        result.show();
    }
}
`
"@

System.Collections.Hashtable["THEORY.md"] = @"
# Apache Spark Theory

## Architecture
- **Driver**: Main program, creates SparkContext, converts code to tasks
- **Cluster Manager**: Allocates resources (Standalone, YARN, Kubernetes)
- **Executors**: Worker processes running tasks
- **Tasks**: Units of work sent to executors

## Core Abstractions
### RDD (Resilient Distributed Dataset)
- Immutable, partitioned collection of records
- Can be operated in parallel
- Automatically recovers from failures (lineage)
- Created from data sources or transforming other RDDs

### DataFrame
- RDD + Schema
- Optimized via Catalyst
- Supports SQL queries
- Columnar access

### Dataset
- DataFrame with type safety (Java/Scala)
- Compile-time type checking
- Encoder-based serialization

## Execution Model
1. **DAG Scheduler**: Creates stages from RDD lineage
2. **Task Scheduler**: Launches tasks on executors
3. **Shuffle**: Data redistribution across partitions
