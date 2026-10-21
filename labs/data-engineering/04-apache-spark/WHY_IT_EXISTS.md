# Why Apache Spark Exists

## The Problem
MapReduce (Hadoop) was too slow for iterative algorithms and interactive queries. Each job writes to disk between stages, making ML training and repeated queries extremely slow.

## Root Cause
- Disk-based shuffle between MapReduce stages
- No in-memory caching
- Limited to batch processing only
- Complex to write (lots of boilerplate)

## Spark's Solution
- **In-memory processing**: Cache data across operations
- **Unified engine**: Batch + Streaming + SQL + ML + Graph
- **Fault tolerance**: RDD lineage for recovery
- **Lazy evaluation**: Optimize execution plan before running

## Java/Spark Benefits
`java
// Spark's DataFrame API is much simpler than raw MapReduce
Dataset<Row> result = spark.read().parquet("data/")
    .filter("age >= 18")
    .groupBy("city")
    .agg(avg("income"), count("*"));
// Spark optimizes this into an efficient execution plan
`
"@

System.Collections.Hashtable["WHY_IT_MATTERS.md"] = @"
# Why Apache Spark Matters

## Impact
- **Speed**: 100x faster than Hadoop MapReduce for iterative algorithms
- **Unified**: One engine for batch, streaming, SQL, ML, graph
- **Ecosystem**: Integration with Hive, HBase, Kafka, Cassandra, S3
- **Language Support**: Java, Scala, Python, SQL, R

## Adoption
- Used by 80%+ of Fortune 500 companies
- De facto standard for big data processing
- Core of Databricks Lakehouse platform
- Active community with 2000+ contributors

## Performance Metrics
- Process 100TB+ datasets
- Stream millions of events/second
- Sub-second latency for streaming
- Optimized via Catalyst + Tungsten
