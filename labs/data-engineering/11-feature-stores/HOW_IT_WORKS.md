# How Feature Stores Work

## Feast Feature Store
`java
// Feature definition (Python/YAML, processed by Feast)
// features.yaml
project: my_project
registry: gs://my-feature-store/registry.db
provider: gcp
online_store:
  type: redis
  connection_string: localhost:6379
offline_store:
  type: file

feature_views:
  - name: user_features
    entities:
      - name: user_id
        value_type: INT64
    features:
      - name: avg_order_value
        type: FLOAT
      - name: total_transactions
        type: INT64
      - name: days_since_last_purchase
        type: INT32
    ttl: 86400  # 1 day
    source: bigquery_query
    query: |
      SELECT
        customer_id as user_id,
        AVG(amount) as avg_order_value,
        COUNT(*) as total_transactions,
        DATE_DIFF(CURRENT_DATE(), MAX(transaction_date), DAY) as days_since_last_purchase
      FROM transactions
      GROUP BY customer_id
`

## Serving Features
`java
// Java client for online feature serving
public class FeatureService {
    private final FeatureStoreClient featureStore;

    public Map<String, Object> getFeatures(String userId, List<String> featureNames) {
        // Online serving - low latency
        GetOnlineFeaturesRequest request = GetOnlineFeaturesRequest.builder()
            .project("my_project")
            .featureService("user_features")
            .entityRows(Collections.singletonMap("user_id", Arrays.asList(userId)))
            .build();

        GetOnlineFeaturesResponse response = featureStore.getOnlineFeatures(request);
        return response.toMap();
    }
}
`

## Training Dataset Generation
`java
// Offline feature retrieval for training
public class TrainingDataGenerator {
    public Dataset<Row> generateTrainingData(SparkSession spark, 
                                              String startDate, String endDate) {
        // Point-in-time correct join
        Dataset<Row> features = spark.read()
            .format("feast")
            .option("project", "my_project")
            .option("feature_view", "user_features")
            .option("start_date", startDate)
            .option("end_date", endDate)
            .load();

        Dataset<Row> labels = spark.read()
            .parquet("s3://data/labels/");

        // Point-in-time join
        Dataset<Row> trainingData = features
            .join(labels.as("l"),
                features.col("user_id").equalTo(labels.col("user_id"))
                    .and(features.col("feature_timestamp")
                        .(labels.col("label_timestamp"))))
            .select("l.*", features.col("*"));

        return trainingData;
    }
}
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# Feature Store Internals

## Architecture Components
`java
/*
Feature Store Architecture:

+------------------+          +------------------+
| Feature Registry |          | Feature          |
| (SQL/File DB)    |          | Engineering      |
| - Feature defs   |<---------| (Spark/Dataflow) |
| - Lineage        |          |                  |
| - Metadata       |          +------------------+
+------------------+                 |
        |                            |
        | Store/Retrieve        Write features
        v                            v
+------------------+          +------------------+
| Online Store     |          | Offline Store    |
| (Redis/Cassandra)|          | (S3/Delta Lake)  |
| - Latest values  |          | - Historical     |
| - Sub-ms latency |          | - Time-series    |
+------------------+          +------------------+
        |                            |
        | Read                       | Read
        v                            v
+------------------+          +------------------+
| Model Serving    |          | Training Pipeline|
| (Real-time)      |          | (Batch)          |
+------------------+          +------------------+
*/
`

## Point-in-Time Join Implementation
`java
public class PointInTimeJoin {
    public Dataset<Row> pointInTimeCorrectJoin(
            Dataset<Row> features, Dataset<Row> labels, 
            String entityKey, String featureTimestamp, String labelTimestamp) {
        // For each label event, find the most recent feature value
        // WITHOUT using future data (no data leakage)
        
        return features.as("f")
            .join(labels.as("l"),
                features.col(entityKey).equalTo(labels.col(entityKey))
                    .and(features.col(featureTimestamp)
                        .(labels.col(labelTimestamp)))
            )
            .groupBy("l.*")
            .agg(functions.max(
                functions.struct(features.col(featureTimestamp), features.col("*")))
                .as("latest_feature"))
            .select("l.*", "latest_feature.*");
    }
}
`
"@

System.Collections.Hashtable["MATH_FOUNDATION.md"] = @"
# Math Foundation for Feature Stores

## Feature Computation Cost
`
ComputeCost = SUM(FeatureCost) * UpdateFrequency
FeatureCost = SourceDataScan + TransformationOps + StorageWrite
OnlineStorage = DistinctEntities * Features * AvgValueSize
OfflineStorage = Events * Features * AvgValueSize * RetentionDays
`

## Serving SLAs
`
Online Latency = NetworkRoundtrip + CacheLookup + Serialization
Online SLA: P99 < 10ms

Offline Throughput = ScannedData / ComputeTime
Offline SLA: 1TB / 30min
`

## Point-in-Time Join Complexity
`
FeatureEvents = SUM(Features * Entities * TimePoints)
LabelEvents = TrainingExamples
JoinComplexity = FeatureEvents * Log(FeatureEvents)
JoinResult = LabelEvents * Features

Optimal: Pre-join features to time-series format
`

## Feature Store Sizing
`
Entities = Distinct entity keys (users, products, etc.)
FeatureCount = Features per entity
UpdateFrequency = How often features recomputed
Storage = Entities * FeatureCount * UpdateFrequency * Retention

Redis Memory = Entities * FeatureCount * AvgValueSize * Replication
DynamoDB RCUs = QPS * FeatureCount / 4096KB
`
"@

System.Collections.Hashtable["VISUAL_GUIDE.md"] = @"
# Visual Guide to Feature Stores

## Feature Store Architecture
`
Source Data                     Feature Store                  Consumers
+----------+                    +------------------------+     +----------+
| Raw      |--- Feature ------->| Feature Registry      |     | Training |
| Events   |   Engineering      | - Feature Definitions |     | Pipeline |
+----------+                    | - Metadata/Lineage    |     +----------+
                                | - Versioning          |
+----------+                    +----------+-------------+     +----------+
| Batches  |--- Batch --------->| Offline  |                  | Batch    |
| (Daily)  |   Features         | Store    |----+---------+   | Scoring  |
+----------+                    | (S3/     |    |         |   +----------+
                                |  Delta)  |    |         |
+----------+                    +----------+    |         |   +----------+
| Streams  |--- Streaming ----->| Online   |----+         +-->| Real-time|
| (Kafka)  |   Features         | Store    |                  | Scoring  |
+----------+                    | (Redis)  |                  +----------+
                                +----------+
`

## Feature Value Flow
`
Timestamp:     t0    t1    t2    t3    t4    t5
Events:        e1    e2    e3    e4    e5    e6
                        |     |           |
Feature Value:  ---v0--v1----v2----------v3---->
                          |     |
Label:                    L1    L2
                            |     |
Point-in-time correct:   v1    v2  (not v0 or v3!)

Model trains on {L1->v1, L2->v2}  - no future leakage
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: Feature Store Implementation

## Feature Engineering Pipeline
`java
@Component
public class FeatureEngineeringPipeline {

    private final SparkSession spark;
    private final FeatureRegistry registry;
    private final OnlineStore onlineStore;

    public void computeAndStoreFeatures(LocalDateTime executionTime) {
        // Compute user features
        Dataset<Row> userFeatures = computeUserFeatures();
        storeFeatures("user_features", userFeatures, executionTime);

        // Compute product features
        Dataset<Row> productFeatures = computeProductFeatures();
        storeFeatures("product_features", productFeatures, executionTime);

        // Compute interaction features
        Dataset<Row> interactionFeatures = computeInteractionFeatures();
        storeFeatures("interaction_features", interactionFeatures, executionTime);
    }

    private Dataset<Row> computeUserFeatures() {
        Dataset<Row> transactions = spark.table("transactions");
        Dataset<Row> users = spark.table("users");

        return transactions
            .join(users, "user_id")
            .groupBy(transactions.col("user_id"))
            .agg(
                count("*").as("total_orders"),
                sum("amount").as("total_revenue"),
                avg("amount").as("avg_order_value"),
                stddev("amount").as("std_order_value"),
                max("amount").as("max_order_value"),
                collect_set("category").as("categories_purchased"),
                datediff(current_date(), max("order_date"))
                    .as("days_since_last_order"),
                count(when(col("is_canceled").equalTo(true), 1))
                    .as("cancel_count"),
                (count(when(col("is_canceled").equalTo(true), 1))
                    .cast("double")
                    .divide(count("*"))).as("cancel_rate")
            )
            .withColumn("feature_timestamp", lit(executionTime));
    }

    private void storeFeatures(String featureGroup,
                                Dataset<Row> features,
                                LocalDateTime timestamp) {
        // Write to offline store (historical)
        features.write()
            .mode("append")
            .partitionBy("feature_timestamp")
            .format("delta")
            .save("s3://feature-store/offline/" + featureGroup + "/");

        // Write latest values to online store
        Dataset<Row> latest = features
            .drop("feature_timestamp");
        latest.foreachPartition((Iterator<Row> it) -> {
            RedisClient client = new RedisClient("redis://feature-store:6379");
            while (it.hasNext()) {
                Row row = it.next();
                String key = featureGroup + ":" + row.getString(0); // entity key
                Map<String, String> featureMap = new HashMap<>();
                for (String col : row.schema().fieldNames()) {
                    if (!col.equals("user_id")) {
                        featureMap.put(col, row.getAs(col).toString());
                    }
                }
                client.hset(key, featureMap);
            }
            client.close();
        });
    }
}
`

## Feature Serving API
`java
@RestController
@RequestMapping("/api/features")
public class FeatureServingController {
    private final FeatureStoreClient featureStore;

    @GetMapping("/online/{entityType}/{entityId}")
    public ResponseEntity<Map<String, Object>> getOnlineFeatures(
            @PathVariable String entityType,
            @PathVariable String entityId,
            @RequestParam List<String> features) {

        Map<String, Object> result = featureStore.getOnlineFeatures(
            entityType, entityId, features);
        return ResponseEntity.ok(result);
    }

    @PostMapping("/training-dataset")
    public ResponseEntity<String> generateTrainingDataset(
            @RequestBody TrainingDatasetRequest request) {

        String datasetPath = featureStore.createTrainingDataset(
            request.getFeatureGroups(),
            request.getLabelTable(),
            request.getStartDate(),
            request.getEndDate()
        );
        return ResponseEntity.ok(datasetPath);
    }
}
`

## Feature Validation
`java
@Component
public class FeatureValidator {

    public void validateFeatures(Dataset<Row> features, String featureGroup) {
        // Check for nulls
        for (String col : features.columns()) {
            if (!col.equals("entity_id")) {
                long nullCount = features.filter(col(col).isNull()).count();
                if (nullCount > 0) {
                    log.warn("Feature {} has {} null values", col, nullCount);
                }
            }
        }

        // Check distributions
        for (String col : features.columns()) {
            if (features.schema().apply(col).dataType() instanceof DoubleType) {
                Dataset<Row> stats = features.agg(
                    min(col).as("min"),
                    max(col).as("max"),
                    avg(col).as("avg"),
                    stddev(col).as("stddev")
                );

                Row statRow = stats.first();
                log.info("Feature {}: min={}, max={}, avg={}, stddev={}",
                    col, statRow.get(0), statRow.get(1),
                    statRow.get(2), statRow.get(3));
            }
        }
    }
}
`
"@

System.Collections.Hashtable["STEP_BY_STEP.md"] = @"
# Step-by-Step Feature Store Setup

## Step 1: Define Features
`yaml
# feature-views.yaml
feature_views:
  - name: user_purchase_features
    entities: [user]
    features:
      - name: avg_order_value
        type: FLOAT
        description: Average value of user's orders
      - name: purchase_frequency_30d
        type: FLOAT
        description: Number of purchases in last 30 days
    source: 
      type: spark_sql
      query: SELECT user_id, AVG(amount) as avg_order_value, ...
`

## Step 2: Compute Features
`java
// Batch feature computation
spark.submit(new FeatureJob()
    .withDate("2024-01-01")
    .withOutput("s3://feature-store/offline/"));
`

## Step 3: Deploy Online Store
`ash
# Deploy Redis for online serving
docker run -d --name feature-store-redis \
  -p 6379:6379 \
  redis:7-alpine
`

## Step 4: Serve Features
`java
// Online serving in production
FeatureClient client = new FeatureClient("redis://feature-store:6379");
Map<String, Object> features = client.getFeatures("user:123",
    Arrays.asList("avg_order_value", "purchase_frequency_30d"));
`

## Step 5: Generate Training Data
`java
// Point-in-time correct training data
Dataset<Row> trainingData = generateTrainingData(
    "2024-01-01", "2024-03-31",
    Arrays.asList("user_purchase_features", "product_features")
);
trainingData.write().parquet("s3://training/order_prediction/v3/");
`
"@

System.Collections.Hashtable["COMMON_MISTAKES.md"] = @"
# Common Feature Store Mistakes

## 1. Point-in-Time Leakage
`java
// WRONG - joins feature data including future
Dataset<Row> training = features.join(labels, "user_id");

// RIGHT - point-in-time correct
Dataset<Row> training = features.as("f")
    .join(labels.as("l"),
        f.col("user_id").equalTo(l.col("user_id"))
            .and(f.col("timestamp").(l.col("label_timestamp"))));
`

## 2. Online/Offline Skew
`java
// WRONG - different computation logic
// Offline: Spark SQL
// Online: Java logic

// RIGHT - same transformation code
FeatureTransformation fn = (row) -> row.getDouble("amount") * 0.95;
// Used both in batch (Spark) and streaming (Flink)
`

## 3. No Feature Validation
`java
// WRONG - trust features blindly
// Feature could have all nulls or infinite values

// RIGHT - validate
if (features.filter(col("value").isNull()).count() > threshold) {
    throw new FeatureQualityException("Too many nulls");
}
`

## 4. Not Versioning Features
`java
// WRONG - overwrite features
features.write().mode("overwrite").save(path);

// RIGHT - version with timestamps
features.write().mode("append").partitionBy("feature_timestamp").save(path);
`
"@

System.Collections.Hashtable["DEBUGGING.md"] = @"
# Debugging Feature Stores

## Common Issues

### Training/Serving Skew
`java
// Compare distributions between training and serving
Dataset<Row> trainFeatures = spark.read().parquet("s3://features/train/");
Dataset<Row> servingFeatures = spark.read().parquet("s3://features/serving/");

trainFeatures.describe().show();
servingFeatures.describe().show();
// Look for distribution differences
`

### Feature Freshness
`java
// Check when features were last updated
spark.sql("SELECT MAX(feature_timestamp) FROM feature_store.offline.user_features")
    .show();
`

### Online Store Connectivity
`java
// Test Redis connection
Jedis jedis = new Jedis("feature-store-redis", 6379);
String pong = jedis.ping();
if (!"PONG".equals(pong)) {
    log.error("Redis not reachable");
}
`

### Missing Features
`java
// Check feature registry
FeatureDefinition def = registry.getFeature("avg_order_value");
if (def == null) {
    log.error("Feature avg_order_value not registered");
}
`
"@

System.Collections.Hashtable["REFACTORING.md"] = @"
# Refactoring Feature Engineering

## Before: Ad-hoc Notebook Features
`python
# Each data scientist creates their own features
features = df.groupby('user').agg({'amount': 'mean'})
features.columns = ['user_avg']
`

## After: Centralized Feature Store
`java
// Features defined once, used everywhere
FeatureDefinition avgOrderValue = FeatureDefinition.builder()
    .name("avg_order_value")
    .type(FeatureType.FLOAT)
    .transformation("SELECT user_id, AVG(amount) FROM transactions GROUP BY user_id")
    .ttl(Duration.ofDays(1))
    .build();

registry.register(avgOrderValue);
`

## Before: Inconsistent Serving Logic
`python
# Batch training: SQL
# Online serving: Java code
# DIFFERENT RESULTS!
`

## After: Unified Logic
`java
// Same transformation for both
public class AvgOrderValueTransform implements FeatureTransform {
    public double compute(List<Transaction> txns) {
        return txns.stream().mapToDouble(Transaction::getAmount).average().orElse(0);
    }
}
// Used in Spark (offline) and Java service (online)
`
"@

System.Collections.Hashtable["PERFORMANCE.md"] = @"
# Feature Store Performance

## Online Store Optimization
`java
// Redis cluster for horizontal scaling
JedisCluster cluster = new JedisCluster(
    new HostAndPort("redis-1", 6379),
    new HostAndPort("redis-2", 6379),
    new HostAndPort("redis-3", 6379));

// Pipeline multiple feature reads
Pipeline pipeline = cluster.pipelined();
for (String key : keys) {
    pipeline.hgetAll(key);
}
List<Object> results = pipeline.syncAndReturnAll();
`

## Offline Store Optimization
`java
// Partition features for efficient retrieval
features.write()
    .partitionBy("feature_timestamp")
    .format("delta")
    .save("s3://feature-store/offline/");

// Z-order for point-in-time join optimization
spark.sql("OPTIMIZE delta.s3://feature-store/offline/ ZORDER BY (entity_id)");
`

## Caching
`java
// Cache frequently accessed features
@Cacheable(value = "features", key = "#entityType + ':' + #entityId")
public Map<String, Object> getFeatures(String entityType, String entityId) {
    return onlineStore.get(entityType, entityId);
}
`

## Batch Feature Computation
`java
// Incremental computation
Dataset<Row> incremental = spark.read()
    .format("delta")
    .load("s3://feature-store/offline/user_features/")
    .filter(col("feature_timestamp").(lastRunTime));

// Only compute for users with new data
incremental.write()
    .mode("append")
    .save("s3://feature-store/offline/user_features/");
`
"@

System.Collections.Hashtable["SECURITY.md"] = @"
# Feature Store Security

## Access Control
`java
@PreAuthorize("hasPermission('feature', 'read')")
public Map<String, Object> getOnlineFeatures(String entityType, String entityId, 
                                              List<String> features) {
    return onlineStore.get(entityType, entityId, features);
}

@PreAuthorize("hasRole('FEATURE_ADMIN')")
public void registerFeature(FeatureDefinition feature) {
    registry.register(feature);
}
`

## Data Masking
`java
// PII features should be masked or excluded
@FeatureMetadata(sensitive = true)
public class SensitiveFeatureIndicator {
    // Features built from PII will be flagged
}
`

## Audit Logging
`java
@Component
public class FeatureAuditLogger {
    @EventListener
    public void onFeatureAccess(FeatureAccessEvent event) {
        auditLog.save(new AuditEntry(
            event.getUser(),
            event.getFeatureName(),
            event.getEntityId(),
            event.getTimestamp()
        ));
    }
}
`
"@

System.Collections.Hashtable["ARCHITECTURE.md"] = @"
# Feature Store Architecture

## Feature Store Platform
`
+-----------------------------------------------------------+
|                   Feature Store Platform                    |
+------------+------------+-------------+-------------------+
| Feature    | Online     | Offline     | Feature           |
| Registry   | Store      | Store       | Serving API       |
| - Metadata | - Redis    | - S3/Delta  | - REST/gRPC      |
| - Lineage  | - DynamoDB | - Parquet   | - SDK (Java/Py)  |
| - Version  | - Cassandra| - BigQuery  | - Batch export   |
+------------+------------+-------------+-------------------+
                  |              |
                  v              v
+-------------------------------------+
|        Feature Engineering          |
|  Spark Jobs | Flink Jobs | SQL      |
|  Batch + Streaming computation      |
+-------------------------------------+
                  |
         +--------+--------+
         |                  |
    +----+----+       +----+----+
    | Offline |       | Online  |
    | Sources |       | Sources |
    +---------+       +---------+
`

## Spring Boot Integration
`java
@SpringBootApplication
@EnableFeatureStore
public class FeatureStoreApplication {
    public static void main(String[] args) {
        SpringApplication.run(FeatureStoreApplication.class, args);
    }

    @Bean
    public FeatureRegistry featureRegistry() {
        return new FeatureRegistry("s3://feature-store/registry/");
    }

    @Bean
    public OnlineStore onlineStore() {
        return new RedisOnlineStore("redis://feature-store:6379");
    }
}
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# Feature Store Exercises

## Exercise 1: Feature Engineering
Compute user-level features from a transaction dataset (avg order value, frequency, etc.)

## Exercise 2: Online Store Setup
Deploy Redis for online feature serving and implement get/set operations.

## Exercise 3: Point-in-Time Join
Implement a point-in-time correct join between features and labels.

## Exercise 4: Feature Registry
Build a feature registry with metadata management and versioning.

## Exercise 5: Feature Serving
Create a REST API that serves online features for real-time inference.
