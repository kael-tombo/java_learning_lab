# Feature Stores

## Overview
A feature store is a centralized platform for managing, serving, and reusing machine learning features across an organization, providing consistency between training and serving.

## Key Concepts
- **Feature**: Input variable used by ML models (e.g., user_avg_order_value)
- **Online Store**: Low-latency feature serving for real-time inference
- **Offline Store**: Batch feature computation for model training
- **Feature Engineering**: Transforming raw data into ML features
- **Point-in-Time Correctness**: Joining features without data leakage

## Java/Spark Example
`java
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import static org.apache.spark.sql.functions.*;

public class FeatureEngineering {
    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
            .appName("FeatureEngineering")
            .getOrCreate();

        Dataset<Row> transactions = spark.read().parquet("s3://data/transactions/");
        Dataset<Row> customers = spark.read().parquet("s3://data/customers/");

        // Compute user features
        Dataset<Row> userFeatures = transactions
            .groupBy("customer_id")
            .agg(
                count("*").as("total_transactions"),
                sum("amount").as("total_spend"),
                avg("amount").as("avg_order_value"),
                max("amount").as("max_order_value"),
                datediff(current_date(), max("transaction_date"))
                    .as("days_since_last_purchase")
            );

        // Compute rolling features
        Dataset<Row> rollingFeatures = transactions
            .groupBy("customer_id",
                window(col("transaction_date"), "30 days"))
            .agg(sum("amount").as("30day_spend"))
            .select(col("customer_id"),
                col("30day_spend"),
                col("window.end").as("window_end"));

        // Write to feature store (offline)
        userFeatures.write().mode("overwrite")
            .parquet("s3://feature-store/offline/user_features/");
        rollingFeatures.write().mode("append")
            .parquet("s3://feature-store/offline/rolling_features/");
    }
}
`
"@

System.Collections.Hashtable["THEORY.md"] = @"
# Feature Store Theory

## Core Components

### Online Store
- Low-latency (milliseconds) feature retrieval
- Uses Redis, DynamoDB, Cassandra, or similar
- Serves real-time inference endpoints
- Pre-computed features for serving

### Offline Store
- Batch feature computation (Spark)
- Stores historical feature values
- Used for training data generation
- Typically on data lake (Parquet/Delta)

### Feature Registry
- Catalog of all features
- Metadata: owner, type, transformation logic
- Versioning and lineage tracking

## Key Problems Feature Stores Solve
1. **Feature Reuse**: No more duplicated feature engineering
2. **Consistency**: Training and serving use same features
3. **Point-in-Time Correctness**: No data leakage in training
4. **Feature Discovery**: Find and share features
5. **Governance**: Track feature lineage and ownership
