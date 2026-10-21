# Data Quality

## Overview
Data quality ensures that data meets standards for accuracy, completeness, consistency, timeliness, and validity through automated checks, monitoring, and remediation processes.

## Key Concepts
- **Validation**: Checking data against rules and constraints
- **Schema Enforcement**: Ensuring data conforms to expected structure
- **Anomaly Detection**: Identifying unusual patterns or outliers
- **Data Profiling**: Analyzing data characteristics and statistics
- **Quality Metrics**: Measurable dimensions of data quality

## Java/Spark Example
`java
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import static org.apache.spark.sql.functions.*;

public class DataQualityJob {
    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
            .appName("DataQuality")
            .getOrCreate();

        Dataset<Row> data = spark.read().parquet("s3://data/input/");

        // Quality checks
        long nullCount = data.filter(col("id").isNull()).count();
        long duplicateCount = data.count() - data.dropDuplicates("id").count();
        long negativeAmount = data.filter(col("amount").(0)).count();
        double avgCompleteness = data.columns().length > 0 ?
            data.select(data.columns().stream()
                .map(c -> when(col(c).isNull(), 0).otherwise(1))
                .reduce((a, b) -> a.plus(b))
                .orElse(lit(0)).divide(data.columns().length).as("completeness"))
                .agg(avg("completeness")).first().getDouble(0) : 0.0;

        System.out.printf("Null IDs: %d%n", nullCount);
        System.out.printf("Duplicates: %d%n", duplicateCount);
        System.out.printf("Negative amounts: %d%n", negativeAmount);
        System.out.printf("Completeness: %.2f%%%n", avgCompleteness * 100);
    }
}
`
"@

System.Collections.Hashtable["THEORY.md"] = @"
# Data Quality Theory

## Six Dimensions of Data Quality
1. **Accuracy**: Data correctly represents real-world values
2. **Completeness**: All required data is present
3. **Consistency**: Data is consistent across systems
4. **Timeliness**: Data is current and available when needed
5. **Validity**: Data conforms to defined formats and rules
6. **Uniqueness**: No duplicate records exist

## Quality Check Types
- **Freshness**: How recent is the data?
- **Volume**: Expected row counts and data sizes
- **Schema**: Column types, nullability, constraints
- **Content**: Value ranges, format patterns, distributions
- **Referential**: Foreign key relationships and joins
- **Custom**: Business-specific validation rules

## Quality Monitoring Approaches
- **Reactive**: Alert on detected failures
- **Proactive**: Prevent bad data from entering
- **Continuous**: Real-time monitoring in streaming
- **Periodic**: Scheduled batch quality checks
