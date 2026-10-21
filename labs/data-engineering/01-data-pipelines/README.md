# Data Pipelines

## Overview
A data pipeline is a series of data processing steps that move data from sources to destinations, transforming and enriching it along the way.

## Key Concepts
- **Batch Processing**: Processing data in discrete chunks at scheduled intervals
- **Stream Processing**: Processing data in real-time as it arrives
- **Pipeline Patterns**: Fan-out, Fan-in, Lambda architecture, Kappa architecture

## Java/Spark Example
`java
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.streaming.StreamingQuery;

public class DataPipelineExample {
    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
            .appName("DataPipelineExample")
            .master("local[*]")
            .getOrCreate();

        Dataset<Row> sourceData = spark.read()
            .option("header", "true")
            .csv("input/data.csv");

        Dataset<Row> transformed = sourceData
            .filter("value IS NOT NULL")
            .groupBy("category")
            .agg(org.apache.spark.sql.functions.avg("value").as("avg_value"));

        transformed.write()
            .mode("overwrite")
            .parquet("output/results/");

        Dataset<Row> streamData = spark.readStream()
            .format("kafka")
            .option("kafka.bootstrap.servers", "localhost:9092")
            .option("subscribe", "input-topic")
            .load();

        StreamingQuery query = streamData
            .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
            .writeStream()
            .format("console")
            .outputMode("append")
            .start();

        query.awaitTermination();
    }
}
`
"@

System.Collections.Hashtable["THEORY.md"] = @"
# Theory of Data Pipelines

## Foundational Concepts
Data pipelines are the backbone of modern data engineering, enabling the movement and transformation of data across heterogeneous systems.

### Batch vs Streaming
| Aspect | Batch | Streaming |
|--------|-------|-----------|
| Latency | Minutes to hours | Milliseconds to seconds |
| Data Volume | Large, bounded | Continuous, unbounded |
| Processing | Periodic jobs | Continuous processing |
| Complexity | Lower | Higher |

### Pipeline Architecture Patterns
1. **Extract-Load-Transform (ELT)** - Extract raw data, load to warehouse, transform in place
2. **Extract-Transform-Load (ETL)** - Extract, transform before loading to target
3. **Data Lakehouse** - Combine data lake flexibility with warehouse reliability

## Java Implementation Patterns
`java
@Configuration
@EnableConfigurationProperties(PipelineProperties.class)
public class PipelineConfig {

    @Bean
    public DataSource sourceDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:postgresql://source:5432/database")
            .username("reader")
            .password("password")
            .build();
    }

    @Bean
    public JdbcCursorItemReader<Transaction> reader() {
        return new JdbcCursorItemReaderBuilder<Transaction>()
            .name("transactionReader")
            .dataSource(sourceDataSource())
            .sql("SELECT * FROM transactions WHERE processed = false")
            .rowMapper(new TransactionRowMapper())
            .build();
    }
}
`
"@

System.Collections.Hashtable["WHY_IT_EXISTS.md"] = @"
# Why Data Pipelines Exist

## The Problem
Organizations collect data from databases, APIs, logs, IoT devices, and SaaS platforms. Without pipelines, this data remains siloed and unusable for analytics.

## Root Cause
Raw data is rarely queryable, joinable, or analyzable in its native format. Pipelines exist to:
1. **Centralize** data from distributed sources
2. **Standardize** formats and schemas
3. **Clean** and validate data quality
4. **Enrich** with business context
5. **Deliver** to consumption tools

## Real-World Analogy
A data pipeline is like a city's water system - raw water (data) is collected from reservoirs (sources), treated (transformed), and distributed through pipes (channels) to consumers.

## Java/Spark Perspective
Pipelines bridge the gap between transactional systems (OLTP) and analytical systems (OLAP). Spring Batch provides robust batch processing while Spark Streaming handles real-time needs.

`java
Pipeline pipeline = PipelineBuilder.newInstance()
    .source(new PostgresSource("jdbc:postgresql://oltp-db:5432/orders"))
    .transform(new EnrichmentTransform("customer-360-api"))
    .sink(new SnowflakeSink("ANALYTICS.WAREHOUSE.FACT_ORDERS"))
    .schedule(CronExpression.EVERY_5_MINUTES)
    .build();
pipeline.start();
`
"@

System.Collections.Hashtable["WHY_IT_MATTERS.md"] = @"
# Why Data Pipelines Matter

## Business Impact
1. **Data-Driven Decisions** - Clean, reliable data enables accurate analytics and ML models
2. **Operational Efficiency** - Automated pipelines replace manual data movement
3. **Real-Time Insights** - Streaming pipelines enable instant response to business events
4. **Data Quality** - Pipelines enforce validation, deduplication, and schema enforcement
5. **Cost Optimization** - Properly designed pipelines reduce storage and compute costs

## Key Metrics
| Metric | Without Pipeline | With Pipeline |
|--------|-----------------|---------------|
| Time to insight | Days | Minutes |
| Data freshness | Stale | Near real-time |
| Error rate | High | < 0.1% |
| Engineering overhead | 80% data wrangling | 20% data wrangling |

## Java/Spark Advantages
Spring Boot + Apache Spark provides a battle-tested stack for enterprise data pipelines with type safety, schema enforcement, fault tolerance via checkpointing, and exactly-once semantics.

`java
SparkSession spark = SparkSession.builder()
    .config("spark.sql.streaming.schemaInference", true)
    .config("spark.sql.streaming.checkpointLocation", "/checkpoints")
    .getOrCreate();
`
"@

System.Collections.Hashtable["HISTORY.md"] = @"
# History of Data Pipelines

## Evolution Timeline
- **1970s**: Batch processing with mainframe COBOL programs
- **1980s**: ETL tools emerge (Informatica, DataStage)
- **1990s**: Data warehousing popularized by Bill Inmon and Ralph Kimball
- **2000s**: Hadoop ecosystem revolutionizes big data processing
- **2010s**: Spark unifies batch and streaming; Kafka enables real-time
- **2020s**: Lakehouse architecture, Data Mesh, DataOps

## Key Milestones
1. **2004**: Google MapReduce paper published
2. **2006**: Hadoop created by Doug Cutting
3. **2010**: Apache Kafka created at LinkedIn
4. **2014**: Apache Spark becomes top-level Apache project
5. **2016**: Apache Flink emerges for stream processing
6. **2019**: Delta Lake open-sourced by Databricks

## Java's Role
Java has been central to the data pipeline ecosystem:
- Apache Hadoop, Spark, Kafka, Flink are all JVM-based
- Spring Batch (est. 2007) standardizes enterprise batch processing
- Java 8+ streams influenced pipeline processing concepts

`java
@Bean
public Job pipelineJob(JobRepository repository, Step step) {
    return new JobBuilder("dataPipeline", repository)
        .start(step)
        .listener(new PipelineJobExecutionListener())
        .build();
}
`
"@

System.Collections.Hashtable["MENTAL_MODELS.md"] = @"
# Mental Models for Data Pipelines

## 1. The Assembly Line Model
Each stage of a pipeline adds value:
- **Stage 1** (Extraction): Raw materials arrive
- **Stage 2** (Cleaning): Parts are inspected
- **Stage 3** (Transformation): Components are assembled
- **Stage 4** (Loading): Finished product delivered

## 2. The Water Flow Model
- **Source** = Reservoir (data originates)
- **Pipeline** = Pipes (data moves through channels)
- **Transform** = Filtration/Chemical treatment (data is cleaned)
- **Sink** = Storage tank (data consumed)

## 3. The DAG Model (Directed Acyclic Graph)
Every pipeline is a DAG where:
- **Nodes** = Processing steps
- **Edges** = Data dependencies
- **No cycles** = Prevents infinite processing

## 4. The Pipes and Filters Pattern
Each filter operates independently, pipes connect them:
`java
public class FilterProcessor {
    public Dataset<Row> process(Dataset<Row> input) {
        return input
            .filter("age >= 18")
            .filter("status = 'ACTIVE'")
            .filter("region IS NOT NULL");
    }
}
`
"@

System.Collections.Hashtable["HOW_IT_WORKS.md"] = @"
# How Data Pipelines Work

## Core Mechanism
Data pipelines operate through interconnected processing stages:

### 1. Source Connectors
`java
@Repository
public class OrderRepository {
    private final JdbcTemplate jdbc;

    public List<Order> fetchUnprocessedOrders() {
        return jdbc.query(
            "SELECT * FROM orders WHERE processed_at IS NULL",
            new BeanPropertyRowMapper<>(Order.class)
        );
    }
}
`

### 2. Transformation Layer
`java
Dataset<Row> enriched = orders
    .join(customers, orders.col("customer_id").equalTo(customers.col("id")))
    .withColumn("total_value",
        functions.expr("quantity * unit_price * (1 - discount)"))
    .withColumn("segment",
        functions.when(functions.col("total_value").(1000), "PREMIUM")
                 .otherwise("STANDARD"));
`

### 3. Sink Connectors
`java
enriched.write().mode("append").jdbc(jdbcUrl, "fact_orders", props);
enriched.write().mode("append").json("s3://data-lake/orders/");
`

### Processing Semantics
- **At-most-once**: Fast but may lose data
- **At-least-once**: Reliable but may duplicate
- **Exactly-once**: Most reliable, highest overhead
