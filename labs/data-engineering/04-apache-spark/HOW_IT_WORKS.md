# How Apache Spark Works

## Execution Pipeline

### 1. DAG Construction
`java
// Spark builds a DAG of stages
Dataset<Row> result = spark.read().parquet("data/")    // Stage 1: Read
    .filter("age > 18")                                  // Narrow dependency
    .groupBy("city")                                     // Stage 2: Shuffle
    .agg(avg("salary").as("avg_salary"))                // Stage 2: Aggregate
    .orderBy(functions.desc("avg_salary"));              // Stage 3: Sort
`

### 2. Stage Division
`java
// Wide dependencies (shuffles) break stages
// narrow: map, filter, union (no shuffle)
// wide: groupBy, join, distinct (shuffle required)

// Stage 0: Read + Filter
// Stage 1: Shuffle + Aggregate
// Stage 2: Sort
`

### 3. Task Execution
`java
SparkSession spark = SparkSession.builder()
    .config("spark.sql.shuffle.partitions", "200")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .getOrCreate();
// Each partition becomes a task
// Tasks are scheduled on available executors
`

### 4. Memory Management
`java
// Spark uses off-heap memory via Tungsten
spark.conf().set("spark.memory.offHeap.enabled", "true");
spark.conf().set("spark.memory.offHeap.size", "4g");
// Execution memory for shuffles, joins, aggregations
// Storage memory for caching
// Unified memory can borrow between both
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# Apache Spark Internals

## Catalyst Optimizer Internals

### Query Planning Pipeline
`java
/*
1. Analysis: Resolve column names, table references
2. Logical Optimization: Predicate pushdown, constant folding
3. Physical Planning: Join strategies, partitioning
4. Code Generation: Generate optimized Java bytecode
*/

// Spark SQL plan
Dataset<Row> plan = spark.sql("SELECT * FROM data WHERE value > 100");
plan.explain("cost");  // Shows optimized plan with cost estimates
`

## Tungsten Engine
`java
// Off-heap memory management
// Cache-friendly data layout
// Whole-stage code generation
spark.conf().set("spark.sql.codegen.wholeStage", "true");
spark.conf().set("spark.sql.unsafe.enabled", "true");
`

## Shuffle Implementation
`java
// Sort-based shuffle (default)
spark.conf().set("spark.shuffle.manager", "sort");
// Tungsten-sort for optimized sorting
spark.conf().set("spark.shuffle.sort.bypassMergeThreshold", "200");
`

## Memory Regions
`java
/*
+------------------+------------------+
|   Execution      |    Storage       |
|   Memory         |    Memory        |
| (joins, sorts,   | (cache,         |
|  aggregations)   |  broadcast)     |
+------------------+------------------+
|         Reserved Memory              |
+--------------------------------------+
*/
spark.conf().set("spark.memory.fraction", "0.6");
spark.conf().set("spark.memory.storageFraction", "0.5");
`
"@

System.Collections.Hashtable["MATH_FOUNDATION.md"] = @"
# Math Foundation for Spark

## Memory Calculations
`
Total Available = spark.executor.memory * spark.executor.instances
Execution Memory = Total * spark.memory.fraction * (1 - spark.memory.storageFraction)
Storage Memory = Total * spark.memory.fraction * spark.memory.storageFraction

Safe Cache Size = Storage Memory / 2
Hash Join Threshold = Execution Memory / RowSize / HashTableOverhead
`

## Shuffle Cost
`
Shuffle Cost = Serialization + Network Transfer + Spill + Deserialization
Serialization = RowCount * RowSize / SerializationBandwidth
Network Transfer = ShuffleSize / NetworkBandwidth
Spill to Disk = ShuffleSize(memory) - AvailableMemory
`

## Parallelism
`
Optimal Partition Count = TotalCores * 2 to 4
Max Parallelism = AvailableCores * ThreadsPerCore
Task Time = DataPerPartition / ProcessingRate
Goal: Task Time = 100-200ms for low latency
`

## Join Costs
`
Broadcast Join = O(n) small table to all executors
Hash Join = O(n + m) with hash table build
Sort Merge Join = O(n log n + m log m + n + m)
Skew Join = O(n * k) where k = skew factor
`
"@

System.Collections.Hashtable["VISUAL_GUIDE.md"] = @"
# Visual Guide to Apache Spark

## Architecture Diagram
`
+-------------------+
|     Driver        |
| +---------------+ |
| | SparkContext  | |
| | DAGScheduler  | |
| | TaskScheduler | |
| +---------------+ |
+--------+----------+
         |
+--------+-----------+-----------+
|        |           |           |
v        v           v           v
+------+ +------+ +------+ +------+
| Exec | | Exec | | Exec | | Exec |
| utor | | utor | | utor | | utor |
| 1    | | 2    | | 3    | | 4    |
+------+ +------+ +------+ +------+
| Cache | | Cache | | Cache | | Cache |
+------+ +------+ +------+ +------+
`

## DAG Visualization
`
Stage 0                         Stage 1
+---------+                    +----------+
| TextFile |-----> Filter ---->| Shuffle  |
+---------+   narrow     +--->| (groupBy)|
                           |    +----+-----+
                           |         |
                           |    +----v-----+
                           |    | Aggregate |
                           |    +----------+
                           |
Stage 2                    |
+---------+                |
| Sort    |<---------------+
+---------+   shuffle
`

## Memory Layout
`
Executor Memory (8GB)
+--------------------------------------------------+
| Reserved (300MB) | User Memory (2GB)  |           |
+------------------+--------------------+           |
   |               | Spark Memory (5.7GB)           |
   |               +-------------------------------+|
   |               | Execution   | Storage         ||
   |               | (3.42GB)    | (2.28GB)        ||
   |               +-------------------------------+|
   +--------------------------------------------------+
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: Apache Spark

## Word Count with RDDs
`java
JavaRDD<String> textFile = spark.sparkContext()
    .textFile("hdfs://...", 4);

JavaPairRDD<String, Integer> counts = textFile
    .flatMap(line -> Arrays.asList(line.split(" ")).iterator())
    .mapToPair(word -> new Tuple2<>(word, 1))
    .reduceByKey(Integer::sum);

counts.saveAsTextFile("hdfs://.../output");
`

## DataFrame API
`java
public class DataFrameOperations {
    public Dataset<Row> analyzeSales(Dataset<Row> sales) {
        return sales
            .select("product_id", "amount", "date")
            .filter(col("amount").(0))
            .withColumn("year", year(col("date")))
            .withColumn("month", month(col("date")))
            .groupBy("product_id", "year", "month")
            .agg(
                sum("amount").as("total_revenue"),
                count("*").as("transaction_count"),
                avg("amount").as("avg_transaction")
            )
            .orderBy(col("year").desc(), col("month").desc());
    }
}
`

## Spark Streaming with Kafka
`java
public class StreamingProcessor {
    public void process(String bootstrapServers) {
        Dataset<Row> stream = spark.readStream()
            .format("kafka")
            .option("kafka.bootstrap.servers", bootstrapServers)
            .option("subscribe", "transactions")
            .option("startingOffsets", "earliest")
            .load()
            .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
            .select(from_json(col("value"), schema).as("data"))
            .select("data.*");

        StreamingQuery query = stream
            .withWatermark("timestamp", "10 minutes")
            .groupBy(
                window(col("timestamp"), "5 minutes"),
                col("category"))
            .agg(sum("amount").as("total"))
            .writeStream()
            .outputMode("complete")
            .format("console")
            .trigger(Trigger.ProcessingTime("10 seconds"))
            .option("checkpointLocation", "/checkpoints")
            .start();

        query.awaitTermination();
    }
}
`

## Custom Aggregation with UDAF
`java
public class MedianUDAF extends UserDefinedAggregateFunction {
    @Override
    public StructType inputSchema() {
        return DataTypes.createStructType(
            new StructField[]{DataTypes.createStructField("value",
                DataTypes.DoubleType, true)});
    }

    @Override
    public StructType bufferSchema() {
        return DataTypes.createStructType(new StructField[]{
            DataTypes.createStructField("values",
                DataTypes.createArrayType(DataTypes.DoubleType), true)});
    }

    @Override
    public DataType dataType() { return DataTypes.DoubleType; }

    @Override
    public boolean deterministic() { return true; }

    @Override
    public void initialize(MutableAggregationBuffer buffer) {
        buffer.update(0, new ArrayList<Double>());
    }

    @Override
    public void update(MutableAggregationBuffer buffer, Row input) {
        if (!input.isNullAt(0)) {
            @SuppressWarnings("unchecked")
            List<Double> values = buffer.getList(0);
            values.add(input.getDouble(0));
            buffer.update(0, values);
        }
    }

    @Override
    public void merge(MutableAggregationBuffer buffer1, Row buffer2) {
        @SuppressWarnings("unchecked")
        List<Double> v1 = buffer1.getList(0);
        @SuppressWarnings("unchecked")
        List<Double> v2 = buffer2.getList(0);
        v1.addAll(v2);
        buffer1.update(0, v1);
    }

    @Override
    public Object evaluate(Row buffer) {
        @SuppressWarnings("unchecked")
        List<Double> values = buffer.getList(0);
        Collections.sort(values);
        int size = values.size();
        if (size == 0) return null;
        if (size % 2 == 0) {
            return (values.get(size/2 - 1) + values.get(size/2)) / 2.0;
        }
        return values.get(size/2);
    }
}
`
"@

System.Collections.Hashtable["STEP_BY_STEP.md"] = @"
# Step-by-Step Spark Development

## Step 1: Setup Project
`xml
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-core_2.12</artifactId>
    <version>3.5.0</version>
</dependency>
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-sql_2.12</artifactId>
    <version>3.5.0</version>
</dependency>
`

## Step 2: Initialize SparkSession
`java
SparkSession spark = SparkSession.builder()
    .appName("MySparkApp")
    .master(System.getProperty("spark.master", "local[*]"))
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .getOrCreate();
`

## Step 3: Load Data
`java
Dataset<Row> jsonData = spark.read().json("s3://bucket/data/");
Dataset<Row> csvData = spark.read().option("header", "true").csv("s3://bucket/data.csv");
Dataset<Row> parquetData = spark.read().parquet("s3://bucket/data.parquet");
Dataset<Row> jdbcData = spark.read().format("jdbc")
    .option("url", "jdbc:postgresql://host/db")
    .option("dbtable", "schema.table").load();
`

## Step 4: Transform
`java
Dataset<Row> transformed = jsonData
    .filter(col("status").equalTo("ACTIVE"))
    .withColumn("year", year(col("created_date")))
    .withColumn("revenue", col("quantity").multiply(col("unit_price")))
    .groupBy("year", "category")
    .agg(sum("revenue").as("total"));
`

## Step 5: Write Output
`java
transformed.write()
    .mode("overwrite")
    .partitionBy("year")
    .parquet("s3://output/");

// Or write to JDBC
transformed.write()
    .mode("append")
    .format("jdbc")
    .option("url", jdbcUrl)
    .option("dbtable", "analytics.sales_summary")
    .save();
`

## Step 6: Submit Job
`ash
spark-submit --class com.example.SparkJob \
  --master yarn \
  --deploy-mode cluster \
  --executor-memory 8g \
  --num-executors 10 \
  --conf spark.sql.shuffle.partitions=200 \
  app.jar
`
"@

System.Collections.Hashtable["COMMON_MISTAKES.md"] = @"
# Common Spark Mistakes

## 1. Collecting Large Datasets
`java
// WRONG - OOM
List<Row> all = dataset.collectAsList();

// RIGHT
dataset.foreachPartition(partition -> {
    while (partition.hasNext()) process(partition.next());
});
`

## 2. Not Broadcasting Small Tables
`java
// WRONG - shuffle join
largeDF.join(smallDF, "key");

// RIGHT - broadcast join
largeDF.join(smallDF.hint("broadcast"), "key");
`

## 3. Creating Too Many Tasks
`java
// WRONG - too many small tasks
spark.conf().set("spark.sql.shuffle.partitions", "10000");

// RIGHT - match cluster size
spark.conf().set("spark.sql.shuffle.partitions",
    spark.sparkContext().defaultParallelism() * 2);
`

## 4. Not Caching Reused Data
`java
// WRONG - recompute every time
for (int i = 0; i < 10; i++) {
    Dataset<Row> filtered = data.filter(...);
}

// RIGHT - cache once
Dataset<Row> filtered = data.filter(...).cache();
`

## 5. Serialization Issues
`java
// WRONG - class not serializable
class MyClass { Object nonSerializable = new NonSerializable(); }
data.map(x -> myClass.method(x));

// RIGHT - use mapPartitions
data.mapPartitions(it -> {
    MyClass mc = new MyClass(); // Created per partition
    ...
});
`
"@

System.Collections.Hashtable["DEBUGGING.md"] = @"
# Debugging Apache Spark

## Common Issues

### Out of Memory
`java
// Check executor memory usage
spark.conf().set("spark.executor.memory", "8g");
spark.conf().set("spark.memory.offHeap.enabled", "true");
spark.conf().set("spark.memory.offHeap.size", "4g");

// Monitor in Spark UI: Executors tab -> Memory
// Look for: Shuffle Spill (Disk), GC Time
`

### Skew
`java
// Check for data skew
dataset.groupBy("key").count()
    .orderBy(functions.desc("count"))
    .show(10);

// Fix with salting
dataset.withColumn("salt",
    (functions.rand()).multiply(10).cast("int"))
    .withColumn("salted_key",
        functions.concat(col("key"), lit("_"), col("salt")))
    .groupBy("salted_key")
    .agg(...);
`

### Slow Tasks
`java
// Tasks that take much longer than others = skew
// Check Spark UI: Stages -> Task Time Distribution
// Fix: Increase partitions, add salting, use AQE
spark.conf().set("spark.sql.adaptive.skewJoin.enabled", "true");
`

### Debugging Commands
`java
// Print execution plan
dataset.explain("formatted");
dataset.explain("cost");

// Show physical plan
spark.sql("EXPLAIN COST SELECT * FROM data").show(false);
`
"@

System.Collections.Hashtable["REFACTORING.md"] = @"
# Refactoring Spark Applications

## RDD to DataFrame
### Before: RDD-based
`java
JavaRDD<String> lines = spark.textFile("data.txt");
JavaPairRDD<String, Integer> counts = lines
    .flatMap(l -> Arrays.asList(l.split(" ")).iterator())
    .mapToPair(w -> new Tuple2<>(w, 1))
    .reduceByKey(Integer::sum);
`

### After: DataFrame-based
`java
Dataset<Row> df = spark.read().text("data.txt");
Dataset<Row> counts = df
    .select(functions.explode(
        functions.split(col("value"), " ")).as("word"))
    .groupBy("word")
    .count();
`

## SQL to Dataset API
### Before: String-based SQL
`java
spark.sql("SELECT * FROM sales JOIN products USING (product_id)");
`

### After: Type-safe Dataset API
`java
salesDF.join(productsDF, "product_id");
`

## Batch to Streaming
### Before: Batch
`java
Dataset<Row> daily = spark.read().parquet("s3://data/2024/01/01/");
`

### After: Streaming
`java
Dataset<Row> stream = spark.readStream()
    .format("kafka")
    .option("subscribe", "topic")
    .load();
`
"@

System.Collections.Hashtable["PERFORMANCE.md"] = @"
# Spark Performance Optimization

## AQE (Adaptive Query Execution)
`java
SparkSession.builder()
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.minPartitionNum", "1")
    .config("spark.sql.adaptive.coalescePartitions.initialPartitionNum", "200")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "10")
    .config("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")
    .config("spark.sql.adaptive.localShuffleReader.enabled", "true")
    .getOrCreate();
`

## Data Serialization
`java
// Use Kryo serialization
spark.conf().set("spark.serializer",
    "org.apache.spark.serializer.KryoSerializer");
spark.conf().set("spark.kryo.registrationRequired", "true");
spark.conf().set("spark.kryo.classesToRegister",
    "com.example.MyClass,com.example.Result");
`

## File Format Optimization
`java
// Use columnar formats with compression
df.write()
    .option("compression", "snappy")
    .parquet("output/");

// Optimize file sizes
spark.conf().set("spark.sql.files.maxPartitionBytes", "134217728"); // 128MB
`

## Join Optimization
`java
// Broadcast joins for small tables
import org.apache.spark.sql.functions.broadcast;
Dataset<Row> result = largeDF.join(broadcast(smallDF), "key");

// Bucketed joins for repeated joins
largeDF.write().bucketBy(42, "key").saveAsTable("fact_bucketed");
smallDF.write().bucketBy(42, "key").saveAsTable("dim_bucketed");
`
"@

System.Collections.Hashtable["SECURITY.md"] = @"
# Apache Spark Security

## Authentication
`java
// Enable authentication
spark.conf().set("spark.authenticate", "true");
spark.conf().set("spark.authenticate.secret", System.getenv("SPARK_SECRET"));

// Enable encryption
spark.conf().set("spark.network.crypto.enabled", "true");
spark.conf().set("spark.ssl.enabled", "true");
spark.conf().set("spark.ssl.keyStore", "/path/to/keystore");
`

## Access Control
`java
// SQL-level security
spark.conf().set("spark.sql.redaction.string.regex", "(?i)(password|secret|token)");

// View-based access
spark.sql("CREATE VIEW sales_safe AS " +
    "SELECT region, SUM(amount) as total, COUNT(*) as count " +
    "FROM fact_sales GROUP BY region");
`

## Data Protection
`java
// Encrypt sensitive columns
Dataset<Row> safe = df.withColumn("email",
    functions.sha2(col("email"), 256));

// Dynamic data masking
spark.udf().register("mask", (String s) -> {
    if (s == null) return null;
    return s.substring(0, 3) + "***" + s.substring(s.indexOf("@"));
}, DataTypes.StringType);
`
"@

System.Collections.Hashtable["ARCHITECTURE.md"] = @"
# Apache Spark Architecture

## Cluster Mode Overview
`
+------------------+       +------------------+
|    Driver        |       |   Cluster Mgr    |
| +--------------+ |       | (YARN/K8s/Stand) |
| | SparkContext | |       +------------------+
| | DAGScheduler | |               |
| | TaskScheduler| |               |
| +--------------+ |               |
+--------+---------+               |
         |                         |
    +----+----+           +--------+--------+
    |         |           |        |        |
+---v---+ +---v---+  +---v---+ +--v----+ +--v----+
| Exec1 | | Exec2 |  | Exec3 | | Exec4 | | Exec5 |
+-------+ +-------+  +-------+ +-------+ +-------+
  | Cache |  | Cache |  | Cache |  | Cache |  | Cache |
+---------+---------+---------+---------+---------+
`

## Application Components
`java
@SpringBootApplication
public class SparkApplication {
    public static void main(String[] args) {
        ConfigurableApplicationContext ctx =
            SpringApplication.run(SparkApplication.class, args);
        SparkSession spark = ctx.getBean(SparkSession.class);
        ctx.getBean(DataPipeline.class).run(spark);
    }

    @Bean
    public SparkSession sparkSession() {
        return SparkSession.builder()
            .appName("SparkApp")
            .config("spark.sql.extensions",
                "io.delta.sql.DeltaSparkSessionExtension")
            .getOrCreate();
    }
}
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# Apache Spark Exercises

## Exercise 1: Word Count
Implement word count using both RDD and DataFrame APIs.

## Exercise 2: Sales Analysis
Load sales CSV, compute daily revenue by product category, find top 10 products.

## Exercise 3: Streaming Pipeline
Build a Spark Streaming application that reads from Kafka, aggregates events in 5-minute windows, and writes to Delta Lake.

## Exercise 4: Custom UDAF
Implement a user-defined aggregate function for percentile calculation.

## Exercise 5: Performance Tuning
Take a slow query, use explain plans to identify bottlenecks, and optimize it with AQE, broadcasting, and partitioning.
