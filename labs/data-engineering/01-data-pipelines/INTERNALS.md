# Internal Architecture of Data Pipelines

## Pipeline Runtime Components

### Process Manager
`java
public class PipelineOrchestrator {
    private final ExecutorService executor = Executors.newFixedThreadPool(4);
    private final Map<String, PipelineStage> stages = new ConcurrentHashMap<>();

    public CompletableFuture<PipelineResult> execute(Pipeline pipeline) {
        List<CompletableFuture<PipelineResult>> futures = pipeline.getStages()
            .stream()
            .map(stage -> CompletableFuture
                .supplyAsync(() -> stage.process(pipeline.getData()), executor)
                .thenApply(this::validateOutput))
            .collect(Collectors.toList());

        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> PipelineResult.success());
    }
}
`

### Checkpointing System
`java
public class WalCheckpointer {
    private final Path walPath;

    public void checkpoint(String pipelineId, long offset, byte[] state) {
        Path checkpointFile = walPath.resolve(pipelineId + ".wal");
        try (FileOutputStream fos = new FileOutputStream(checkpointFile.toFile(), true)) {
            fos.write(longToBytes(offset));
            fos.write(state);
        }
    }
}
`

### Backpressure Mechanism
`java
@Bean
public Flux<DataRecord> backpressuredPipeline() {
    return Flux.from(sourceStream)
        .onBackpressureBuffer(10000,
            dropped -> log.warn("Dropped {} records due to backpressure", dropped))
        .publishOn(Schedulers.parallel())
        .transform(this::processRecord);
}
`
"@

System.Collections.Hashtable["MATH_FOUNDATION.md"] = @"
# Math Foundation for Data Pipelines

## Data Flow Metrics

### Throughput Calculation
`
Throughput = Records processed / Time unit
TPS (Transactions/sec) = N / At

For parallel pipelines:
Total Throughput = S(TP_i) for i = 1 to n workers
`

### Latency Components
`
Total Latency = T_extract + T_transform + T_load + T_queue
`

### Pipeline Capacity Planning
`java
public class PipelineCapacity {
    public static double calculateRequiredNodes(
            long dailyDataVolume, double processingRate, double slaHours) {
        double nodes = (dailyDataVolume / 24.0) / processingRate;
        nodes = nodes * (24.0 / slaHours);
        return Math.ceil(nodes);
    }
}
`

### Amdahl's Law for Pipelines
`
Speedup = 1 / ((1 - P) + P/N)
Where P = parallelizable portion, N = number of processors
`

### Probability of Pipeline Failure
`
P(failure) = 1 - P(1 - p_i) for i stages
MTBF = 1 / lambda (where lambda = failure rate)
Availability = MTBF / (MTBF + MTTR)
`
"@

System.Collections.Hashtable["VISUAL_GUIDE.md"] = @"
# Visual Guide to Data Pipelines

## Pipeline Architecture Diagram
`
+---------+    +----------+    +-----------+    +----------+
| Source  |--->| Extract  |--->| Transform |--->|   Load   |
| Systems |    |  Layer   |    |   Layer   |    |   Layer  |---> Data Warehouse
+---------+    +----------+    +-----------+    +----------+
     |               |               |               |
     v               v               v               v
  PostgreSQL     Kafka Topic     Spark Job       Snowflake
  Oracle         S3 Events      Flink Job       Redshift
  REST APIs      File Drops    Spring Batch     BigQuery
`

## Streaming Pipeline Flow
`
+----------+    +----------+    +-----------+    +----------+
| Producers|--->|  Kafka   |--->|  Stream   |--->| Consumer |
| (Java)   |    |  Broker  |    | Processor |    |  (Apps)  |
+----------+    +----------+    +-----------+    +----------+
     |               |               |               |
  Send events    Partitioned    Exactly-once     Real-time
  via Kafka      & replicated   processing       dashboards
`

## Pipeline State Machine
`
                  +-----------------------------+
                  |                             |
                  v                             |
+--------+   +---------+   +--------+   +----------+
|PENDING |-->| RUNNING |-->|STOPPING|-->| COMPLETED|
+--------+   +---------+   +--------+   +----------+
                  |
    +-------------+-------------+
    v             v             v
+--------+  +----------+  +--------+
|FAILED  |  |TIMEOUT   |  |ABORTED |
+--------+  +----------+  +--------+
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: Data Pipeline Implementation

## Complete Java Pipeline with Spring Batch

### Domain Model
`java
public class Transaction {
    private String id;
    private String userId;
    private BigDecimal amount;
    private LocalDateTime timestamp;
    private String status;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }
    public BigDecimal getAmount() { return amount; }
    public void setAmount(BigDecimal amount) { this.amount = amount; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
`

### Custom Item Processor
`java
public class TransactionProcessor implements ItemProcessor<Transaction, EnrichedTransaction> {

    private final CustomerService customerService;
    private final FraudDetectionClient fraudClient;

    public TransactionProcessor(CustomerService customerService, FraudDetectionClient fraudClient) {
        this.customerService = customerService;
        this.fraudClient = fraudClient;
    }

    @Override
    public EnrichedTransaction process(Transaction item) {
        Customer customer = customerService.findById(item.getUserId());
        BigDecimal riskScore = fraudClient.evaluate(item);

        EnrichedTransaction enriched = new EnrichedTransaction();
        enriched.setId(item.getId());
        enriched.setCustomerName(customer.getFullName());
        enriched.setCustomerSegment(customer.getSegment());
        enriched.setAmount(item.getAmount());
        enriched.setRiskScore(riskScore);
        enriched.setProcessedAt(LocalDateTime.now());

        if (riskScore.compareTo(new BigDecimal("0.8")) > 0) {
            enriched.setFlag("FRAUD_REVIEW");
        }
        return enriched;
    }
}
`

### Pipeline Configuration
`java
@Configuration
public class TransactionPipelineConfig {

    @Bean
    public Job transactionPipelineJob(
            JobRepository jobRepository, Step extractStep, Step transformStep, Step loadStep) {
        return new JobBuilder("transactionPipeline", jobRepository)
            .start(extractStep)
            .next(transformStep)
            .next(loadStep)
            .listener(new PipelineMetricsListener())
            .build();
    }

    @Bean
    public Step extractStep(JobRepository jobRepository,
            PlatformTransactionManager transactionManager, ItemReader<Transaction> reader) {
        return new StepBuilder("extractStep", jobRepository)
            .<Transaction, Transaction>chunk(1000, transactionManager)
            .reader(reader)
            .writer(items -> log.info("Extracted {} records", items.size()))
            .build();
    }
}
`

### Metrics and Monitoring
`java
@Component
public class PipelineMetricsListener extends JobExecutionListenerSupport {
    private final MeterRegistry meterRegistry;

    @Override
    public void beforeJob(JobExecution jobExecution) {
        meterRegistry.counter("pipeline.started",
            "name", jobExecution.getJobInstance().getJobName()).increment();
    }

    @Override
    public void afterJob(JobExecution jobExecution) {
        if (jobExecution.getStatus() == BatchStatus.COMPLETED) {
            meterRegistry.counter("pipeline.completed").increment();
        } else {
            meterRegistry.counter("pipeline.failed").increment();
        }
        long duration = jobExecution.getEndTime().getTime() -
                       jobExecution.getStartTime().getTime();
        meterRegistry.timer("pipeline.duration")
            .record(Duration.ofMillis(duration));
    }
}
`
"@

System.Collections.Hashtable["STEP_BY_STEP.md"] = @"
# Step-by-Step Guide to Building Data Pipelines

## Phase 1: Requirements Analysis
1. Identify data sources (databases, APIs, files, streams)
2. Define data volume and velocity requirements
3. Determine freshness SLAs (real-time, hourly, daily)
4. Map data consumers and their formats

## Phase 2: Architecture Design
`java
@ConfigurationProperties(prefix = "pipeline")
public class PipelineProperties {
    private String sourceType;
    private String sinkType;
    private int batchSize = 1000;
    private int parallelism = 4;
    private String checkpointDir = "/tmp/checkpoints/";
    private String cronSchedule = "0 */5 * * * *";
}
`

## Phase 3: Source Connection Setup
`
spring.datasource.url=jdbc:postgresql://oltp-server:5432/source_db
spring.datasource.username=pipeline_user
spring.datasource.password=
spring.cloud.stream.bindings.input.destination=source-topic
spring.cloud.stream.kafka.binder.brokers=localhost:9092
`

## Phase 4: Transformation Logic
`java
public class DataTransformer {
    public Dataset<Row> cleanData(Dataset<Row> raw) {
        return raw
            .na().drop("any")
            .dropDuplicates("id")
            .filter("amount > 0")
            .withColumn("created_date", functions.to_date(functions.col("created_at")));
    }

    public Dataset<Row> enrichData(Dataset<Row> clean) {
        return clean
            .withColumn("tax", functions.expr("amount * 0.08"))
            .withColumn("total_with_tax", functions.expr("amount + (amount * 0.08)"))
            .withColumn("year_month", functions.date_format(functions.col("created_date"), "yyyyMM"));
    }
}
`

## Phase 5: Sink Configuration
`java
public class MultiSinkWriter {
    public void write(Dataset<Row> data) {
        data.write().mode("append").parquet("s3a://datalake/transactions/");
        data.write().mode("append").jdbc(warehouseUrl, "fact_transactions", connectionProps);
        data.write().format("org.elasticsearch.spark.sql")
            .option("es.resource", "transactions/_doc")
            .save();
    }
}
`

## Phase 6: Monitoring
`java
@RestController
@RequestMapping("/api/pipeline")
public class PipelineController {
    @GetMapping("/health")
    public ResponseEntity<PipelineHealth> health() {
        return ResponseEntity.ok(new PipelineHealth(
            pipelineService.getStatus(), pipelineService.getProcessedCount(),
            pipelineService.getErrorCount(), pipelineService.getLagBytes()));
    }
}
`
"@

System.Collections.Hashtable["COMMON_MISTAKES.md"] = @"
# Common Mistakes in Data Pipelines

## 1. Schema Evolution Ignorance
`java
// WRONG - brittle
dataset.select("col1", "col2", "col3");

// RIGHT - schema-aware
StructType schema = dataset.schema();
if (schema.fieldNames().contains("new_col")) {
    dataset = dataset.withColumn("new_col", functions.lit("default"));
}
`

## 2. Not Handling Late Data
`java
// WRONG - assumes ordered arrival
Dataset<Row> result = stream
    .groupBy(functions.window(col("timestamp"), "1 hour"))
    .count();

// RIGHT - handles late data with watermark
Dataset<Row> result = stream
    .withWatermark("timestamp", "10 minutes")
    .groupBy(functions.window(col("timestamp"), "1 hour"))
    .count();
`

## 3. Missing Idempotency
`java
// WRONG - always inserts
stmt.execute("INSERT INTO target VALUES (...)");

// RIGHT - idempotent merge
stmt.execute("MERGE INTO target t " +
    "USING (VALUES (...)) s " +
    "ON t.id = s.id " +
    "WHEN MATCHED THEN UPDATE SET ... " +
    "WHEN NOT MATCHED THEN INSERT ...");
`

## 4. No Backpressure Handling
`java
// WRONG - infinite queue
BlockingQueue<Record> queue = new LinkedBlockingQueue<>();

// RIGHT - bounded queue with rejection
BlockingQueue<Record> queue = new ArrayBlockingQueue<>(10000);
`

## 5. Hardcoding Connection Strings
`java
// WRONG
String url = "jdbc:postgresql://localhost:5432/db?user=admin&pass=password";

// RIGHT
String url = System.getenv("DB_URL");
String pass = vaultService.getSecret("db/password");
`
"@

System.Collections.Hashtable["DEBUGGING.md"] = @"
# Debugging Data Pipelines

## Common Failure Modes

### OOM Errors
`java
// WRONG - collects all to driver
List<Row> allRows = dataset.collectAsList();

// RIGHT - process per partition
dataset.foreachPartition((Iterator<Row> it) -> {
    while (it.hasNext()) { processRow(it.next()); }
});
`

### Serialization Errors
`java
// Symptom: Task not serializable
// WRONG
SomeService service = new SomeService();
dataset.map(row -> service.process(row));

// RIGHT - initialize per partition
dataset.mapPartitions((Iterator<Row> it) -> {
    SomeService service = new SomeService();
    return new Iterator<String>() {
        public boolean hasNext() { return it.hasNext(); }
        public String next() { return service.process(it.next()); }
    };
}, Encoders.STRING());
`

### Data Skew
`java
// Diagnose skew
dataset.groupBy("key").count().orderBy(functions.desc("count")).show(10);

// Fix with salting
Dataset<Row> salted = dataset
    .withColumn("salt", (functions.rand() * 10).cast("int"))
    .withColumn("salted_key",
        functions.concat(functions.col("key"), functions.lit("_"), functions.col("salt")));
`

### Debugging Commands
`ash
# Spark UI
open http://localhost:4040

# Kafka consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group pipeline-group --describe

# Pipeline logs
kubectl logs -l app=pipeline -n data-platform --tail=100 -f
`
"@

System.Collections.Hashtable["REFACTORING.md"] = @"
# Refactoring Data Pipelines

## From Monolith to Modular
### Before
`java
public class Pipeline {
    public void run() {
        // 500 lines of extract, transform, load all mixed together
    }
}
`

### After
`java
@Component
public class PipelineOrchestrator {
    private final Extractor extractor;
    private final Transformer transformer;
    private final Loader loader;
    private final MetricsCollector metrics;

    public PipelineResult run(PipelineContext ctx) {
        metrics.startTimer();
        DataFrame raw = extractor.extract(ctx);
        DataFrame transformed = transformer.transform(raw);
        LoadResult result = loader.load(transformed, ctx);
        metrics.record(ctx, result);
        return result;
    }
}
`

## Configuration Externalization
### Before
`java
jdbcTemplate.query("SELECT * FROM orders WHERE date > '2024-01-01'");
`

### After
`java
@Value("")
private String extractQuery;
jdbcTemplate.query(extractQuery);
`

## From Batch to Streaming
### Before
`java
Dataset<Row> daily = spark.read().parquet("s3://data/2024/01/01/");
`

### After
`java
Dataset<Row> stream = spark.readStream()
    .format("delta")
    .option("maxFilesPerTrigger", 10)
    .table("events");
stream.groupBy("type").count();
`
"@

System.Collections.Hashtable["PERFORMANCE.md"] = @"
# Performance Optimization for Data Pipelines

## Spark Performance Tuning
`java
SparkSession spark = SparkSession.builder()
    .config("spark.sql.shuffle.partitions", "200")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.sql.adaptive.localShuffleReader.enabled", "true")
    .getOrCreate();
`

## Caching Strategies
`java
Dataset<Row> lookupTable = spark.read().parquet("lookup/");
lookupTable.cache();
lookupTable.persist(StorageLevel.MEMORY_AND_DISK_SER());
`

## Partition Pruning
`java
dataset.write()
    .partitionBy("year", "month", "day")
    .parquet("s3://data-lake/events/");

Dataset<Row> filtered = spark.read()
    .parquet("s3://data-lake/events/")
    .filter("year = 2024 AND month = 6");
`

## Broadcast Joins
`java
Dataset<Row> result = largeTable
    .join(smallTable.hint("broadcast"), "country_id");
`

## JVM Tuning
`ash
--executor-memory 8g
--driver-memory 4g
--conf spark.executor.memoryOverhead=2g
--conf spark.memory.offHeap.enabled=true
--conf spark.executor.extraJavaOptions="-XX:+UseG1GC -XX:InitiatingHeapOccupancyPercent=35"
`
"@

System.Collections.Hashtable["SECURITY.md"] = @"
# Security in Data Pipelines

## Authentication and Authorization
`java
// Kerberos authentication
spark.conf().set("spark.hadoop.fs.s3a.aws.credentials.provider",
    "com.amazonaws.auth.InstanceProfileCredentialsProvider");

// JDBC with SSL
String url = "jdbc:postgresql://host:5432/db?ssl=true&sslmode=verify-full";
Properties props = new Properties();
props.setProperty("user", System.getenv("DB_USER"));
props.setProperty("password", vaultService.getSecret("db/password"));
`

## Data Encryption
`java
public class DataEncryptor {
    private static final String ALGORITHM = "AES/GCM/NoPadding";

    public Dataset<Row> encryptPII(Dataset<Row> data, String column, byte[] key) {
        return data.withColumn(column,
            functions.udf((String value) -> {
                Cipher cipher = Cipher.getInstance(ALGORITHM);
                cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "AES"));
                byte[] encrypted = cipher.doFinal(value.getBytes(StandardCharsets.UTF_8));
                return Base64.getEncoder().encodeToString(encrypted);
            }, DataTypes.StringType).apply(functions.col(column)));
    }
}
`

## Secret Management
`java
@Configuration
public class VaultConfiguration {
    @Bean
    public VaultTemplate vaultTemplate() {
        return new VaultTemplate(
            new VaultEndpoint("vault.internal", 8200, true),
            new AppRoleAuthentication(
                System.getenv("VAULT_ROLE_ID"),
                System.getenv("VAULT_SECRET_ID")));
    }
}
`
"@

System.Collections.Hashtable["ARCHITECTURE.md"] = @"
# Architecture of Data Pipelines

## High-Level Architecture
`
+---------------------------------------------------------+
|                    Data Pipeline Platform                |
+--------------+--------------+--------------+-------------+
|  Ingestion   |  Processing  |  Storage     |  Serving    |
|  Layer       |  Layer       |  Layer       |  Layer      |
+--------------+--------------+--------------+-------------+
|  Kafka       |  Spark       |  Data Lake   |  APIs       |
|  Kinesis     |  Flink       |  Warehouse   |  BI Tools   |
|  JDBC        |  Spring Batch|  Cache       |  Dashboards |
|  REST APIs   |  Beam        |  Search      |  ML Models  |
+--------------+--------------+--------------+-------------+
`

## Component Diagram
`
                    +---------------+
                    |  Controller   |
                    |  (REST API)   |
                    +-------+-------+
                            |
                    +-------v-------+
                    |  Service      |
                    |  Orchestrator |
                    +-------+-------+
                            |
        +-------------------+-------------------+
        |                   |                   |
+-------v-------+   +-------v-------+   +-------v-------+
|  Extractor    |   | Transformer   |   |    Loader     |
|  (Reader)     |   | (Processor)   |   |   (Writer)    |
+-------+-------+   +-------+-------+   +-------+-------+
        |                   |                   |
+-------v-------+   +-------v-------+   +-------v-------+
|  Source       |   |  Business     |   |   Target      |
|  Connectors   |   |  Logic        |   |   Connectors  |
+---------------+   +---------------+   +---------------+
`

## Spring Boot Pipeline Application
`java
@SpringBootApplication
@EnableBatchProcessing
@EnableScheduling
public class PipelineApplication {
    public static void main(String[] args) {
        SpringApplication.run(PipelineApplication.class, args);
    }
}
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# Exercises for Data Pipelines

## Exercise 1: Build a Simple Batch Pipeline
Create a Spring Batch pipeline that reads CSV files and writes to PostgreSQL.
`java
// TODO:
// 1. Configure FlatFileItemReader for CSV
// 2. Create ItemProcessor to transform data
// 3. Configure JdbcBatchItemWriter
// 4. Build Job with steps
`

## Exercise 2: Streaming Pipeline with Kafka
Build a Kafka stream processor that aggregates events by window.
`java
// TODO:
// 1. Create Kafka producer configuration
// 2. Read from topic with Spark streaming
// 3. Apply tumbling window of 5 minutes
// 4. Write aggregated results to console
`

## Exercise 3: Error Handling
Implement retry and dead letter queue pattern.
`java
// TODO:
// 1. Configure retry template
// 2. Skip policy for recoverable errors
// 3. Dead letter queue for unrecoverable errors
// 4. Alert on failure threshold
`

## Exercise 4: Pipeline Monitoring
Add metrics collection and health endpoints.
`java
// TODO:
// 1. Record processing time per record
// 2. Count successes and failures
// 3. Expose Prometheus metrics
// 4. Create health check endpoint
`
"@

System.Collections.Hashtable["QUIZ.md"] = @"
# Data Pipelines Quiz

## Question 1
What is the main difference between batch and stream processing?
- A) Batch processes data continuously
- B) Stream processes data in discrete intervals
- C) Batch processes bounded data, stream processes unbounded data
- D) There is no difference

## Question 2
Which Apache project is most commonly used for distributed stream processing?
- A) Hadoop
- B) Spark
- C) HBase
- D) Hive

## Question 3
What does DAG stand for in the context of data pipelines?
- A) Data Aggregation Graph
- B) Directed Acyclic Graph
- C) Distributed Application Grid
- D) Dynamic Access Gateway

## Question 4
Which of the following is NOT a data pipeline pattern?
- A) Fan-out
- B) Fan-in
- C) Lambda architecture
- D) Microservice mesh

## Question 5
What is the purpose of checkpointing in streaming pipelines?
- A) Speed up processing
- B) Enable fault recovery
- C) Reduce memory usage
- D) Improve data quality

## Answer Key
1: C, 2: B, 3: B, 4: D, 5: B
