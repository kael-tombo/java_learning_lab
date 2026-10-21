# Data Warehousing

## Overview
A data warehouse is a centralized repository optimized for analytics, reporting, and business intelligence, storing integrated data from multiple sources.

## Key Concepts
- **Star Schema**: Central fact table surrounded by dimension tables
- **Snowflake Schema**: Normalized dimension tables
- **OLAP**: Online Analytical Processing for multi-dimensional analysis
- **Dimensional Modeling**: Kimball's approach focusing on business processes

## Java/Spark Example
`java
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import static org.apache.spark.sql.functions.*;

public class WarehouseLoader {
    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
            .appName("WarehouseLoad")
            .config("spark.sql.warehouse.dir", "hdfs://warehouse/")
            .getOrCreate();

        // Load dimension table
        Dataset<Row> dimCustomer = spark.read().parquet("s3://datalake/dim_customer/");
        dimCustomer.write().mode("overwrite").saveAsTable("wh.dim_customer");

        // Load fact table
        Dataset<Row> factSales = spark.read().parquet("s3://datalake/fact_sales/");
        factSales.write().mode("append").saveAsTable("wh.fact_sales");

        // OLAP query
        spark.sql("SELECT d.region, SUM(f.amount) as revenue " +
                  "FROM wh.fact_sales f " +
                  "JOIN wh.dim_customer d ON f.customer_id = d.id " +
                  "WHERE f.date >= '2024-01-01' " +
                  "GROUP BY d.region " +
                  "ORDER BY revenue DESC").show();
    }
}
`
"@

System.Collections.Hashtable["THEORY.md"] = @"
# Data Warehousing Theory

## Dimensional Modeling
- **Fact Tables**: Measures, metrics, foreign keys to dimensions
- **Dimension Tables**: Descriptive attributes, hierarchies
- **Grain**: Level of detail stored in a fact table

## Schema Types
### Star Schema
`
+----------------+     +----------------+
| dim_customer   |     | fact_sales     |
+----------------+     +----------------+
| customer_id PK |<--- | customer_id FK |
| name           |     | product_id FK  |
| region         |     | date_id FK     |
| segment        |     | amount         |
+----------------+     | quantity       |
                       | discount       |
+----------------+     +----------------+
| dim_product    |            ^
+----------------+            |
| product_id PK  |<-----------+
| product_name   |
| category       |
| price          |
+----------------+
`

## OLAP Operations
- **Slice**: Filter on one dimension
- **Dice**: Filter on multiple dimensions
- **Drill-down**: Increase granularity
- **Roll-up**: Decrease granularity (aggregate)
- **Pivot**: Reorient the cube

## Warehouse Architectures
- **Kimball**: Bottom-up, dimensional marts, bus architecture
- **Inmon**: Top-down, normalized 3NF, then dimensional marts
- **Data Vault**: Hub, Link, Satellite tables for auditability
- **Lakehouse**: Delta Lake/Iceberg with warehouse capabilities
