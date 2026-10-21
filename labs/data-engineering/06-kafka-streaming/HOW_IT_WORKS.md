# How Kafka Streaming Works

## Core Processing Model
`java
public class OrderProcessingTopology {

    public void buildTopology(StreamsBuilder builder) {
        // Input streams
        KStream<String, Order> orders = builder
            .stream("orders", Consumed.with(Serdes.String(), orderSerde));

        KTable<String, Customer> customers = builder
            .table("customers", Consumed.with(Serdes.String(), customerSerde));

        // Enrich orders with customer data
        KStream<String, EnrichedOrder> enriched = orders.join(
            customers,
            (order, customer) -> new EnrichedOrder(order, customer),
            Joined.with(Serdes.String(), orderSerde, customerSerde));

        // Aggregate by region
        KTable<String, Long> regionalCounts = enriched
            .groupBy((key, order) -> order.getRegion(),
                     Grouped.with(Serdes.String(), enrichedOrderSerde))
            .count(Materialized.as("regional-counts"));

        // Filter for alerts
        KStream<String, Alert> alerts = enriched
            .filter((key, order) -> order.getAmount() > 10000)
            .mapValues(order -> new Alert("High value order: " + order.getId()));

        // Output
        enriched.to("enriched-orders", Produced.with(Serdes.String(), enrichedOrderSerde));
        alerts.to("alerts", Produced.with(Serdes.String(), alertSerde));
    }
}
`

## Stateful Transformations
`java
public class FraudDetectionProcessor implements Processor<String, Transaction, String, Alert> {
    private KeyValueStore<String, Double> lastAmountStore;

    @Override
    public void init(ProcessorContext context) {
        lastAmountStore = context.getStateStore("transaction-store");
    }

    @Override
    public void process(String key, Transaction transaction) {
        Double lastAmount = lastAmountStore.get(key);
        if (lastAmount != null &&
            transaction.getAmount() > 1000 &&
            lastAmount > 1000 &&
            transaction.getTimestamp() - lastTimestamp < 60000) {
            context.forward(key, new Alert("Suspicious transaction pattern"));
        }
        lastAmountStore.put(key, transaction.getAmount());
    }
}
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# Kafka Streaming Internals

## Task Architecture
`java
/*
Application Thread 1          Application Thread 2
+---------------------+       +---------------------+
| Task 0 (p0)         |       | Task 2 (p2)         |
| Task 1 (p1)         |       | Task 3 (p3)         |
+---------------------+       +---------------------+
| Consumer + Producer |       | Consumer + Producer |
+---------------------+       +---------------------+

Partitions: p0, p1, p2, p3
Tasks = Partitions / Threads
*/
`

## State Management
`java
// RocksDB state store
// Key-value data stored on local disk
// Changelog topic for fault tolerance
// Backup and restore via Kafka topics

Properties props = new Properties();
props.put(StreamsConfig.STATE_DIR_CONFIG, "/data/kafka-streams");
props.put(StreamsConfig.ROCKSDB_CONFIG_SETTER_CLASS_CONFIG,
    CustomRocksDBConfig.class.getName());
`

## Consumer/Producer Integration
`java
// Each task has its own consumer and producer
// Records consumed -> processed -> produced
// Offsets committed with transactions (exactly-once)
props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 100);
props.put(StreamsConfig.BUFFERED_RECORDS_PER_PARTITION_CONFIG, 1000);
`
"@

System.Collections.Hashtable["MATH_FOUNDATION.md"] = @"
# Math Foundation for Kafka Streaming

## Throughput
`
Records/Sec = BatchSize / ProcessingTime
Effective Throughput = Min(ConsumeRate, ProcessRate, ProduceRate)

Optimal BatchSize = TargetLatency * Throughput
MaxThroughput = Partitions * PerPartitionThroughput
`

## State Size
`
StateSize = Keys * ValueSize * (1 + Overhead)
ChangelogTopicSize = StateSize * UpdateRate * RetentionTime

RocksDB WriteBuffer = Memtable Size
RocksDB ReadCache = BlockCache Size
`

## Window Calculations
`
Tumbling Windows = Duration / WindowSize * Partitions
Hopping Windows = Duration / Advance * Partitions
StatePerWindow = KeysPerWindow * ValueSize * Overhead

SessionWindows = Sessions * AvgSessionDuration * Partitions
`

## Exactly-Once Overhead
`
Normal Latency = ConsumerPoll + Process + Produce + Commit
ExactlyOnceLatency = NormalLatency + TransactionCoordinator + CommitLog

EOS Overhead = 1-5% additional latency
TransactionTimeout = 2x MaxProcessingTime
`
"@

System.Collections.Hashtable["VISUAL_GUIDE.md"] = @"
# Visual Guide to Kafka Streaming

## Topology Visualization
`
Source: orders (KStream)
  |
  v
Join with customers (KTable)
  |
  v
EnrichedOrder (KStream)
  |
  +-----> GroupBy region
  |         |
  |         v
  |       Count (KTable)
  |         |
  |         v
  |       Sink: regional-counts
  |
  +-----> Filter: amount > 10000
  |         |
  |         v
  |       MapValue -> Alert
  |         |
  |         v
  |       Sink: alerts
  |
  +-----> Sink: enriched-orders (to output)
`

## Stream-Table Duality
`
KStream (Append Log):        KTable (Changelog):
key=1,val=A                  key=1 -> A
key=2,val=B                  key=2 -> B
key=1,val=C                  key=1 -> C (overwrites A)
key=1,val=D                  key=1 -> D (overwrites C)

Final:
KStream: 4 records
KTable: {1=D, 2=B}
`

## State Store Architecture
`
Application Instance 1          Application Instance 2
+------------------------+      +------------------------+
| State Store (p0)       |      | State Store (p2)       |
|   cust_1 -> {...}     |      |   cust_3 -> {...}      |
|   cust_2 -> {...}     |      |   cust_4 -> {...}      |
| Changelog Topic p0    |      | Changelog Topic p2     |
+------------------------+      +------------------------+
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: Kafka Streams

## Clickstream Analysis
`java
@Configuration
@EnableKafkaStreams
public class ClickstreamPipeline {

    @Bean
    public KStream<String, ClickEvent> clickStream(StreamsBuilder builder) {
        return builder.stream("clicks",
            Consumed.with(Serdes.String(), clickEventSerde));
    }

    @Bean
    public KTable<String, Long> pageViews(KStream<String, ClickEvent> clicks) {
        return clicks
            .filter((key, click) -> click.getEventType() == EventType.PAGE_VIEW)
            .groupBy((key, click) -> click.getUrl(),
                     Grouped.with(Serdes.String(), clickEventSerde))
            .count(Materialized.<String, Long, KeyValueStore<Bytes, byte[]>>
                as("page-view-counts")
                .withKeySerde(Serdes.String())
                .withValueSerde(Serdes.Long()));
    }

    @Bean
    public KStream<String, UserSession> userSessions(KStream<String, ClickEvent> clicks) {
        return clicks
            .groupByKey(Grouped.with(Serdes.String(), clickEventSerde))
            .windowedBy(SessionWindows.with(Duration.ofMinutes(30)))
            .aggregate(
                UserSession::new,
                (key, click, session) -> session.addEvent(click),
                (key, s1, s2) -> s1.merge(s2),
                Materialized.with(Serdes.String(), userSessionSerde))
            .toStream()
            .map((windowedKey, session) ->
                KeyValue.pair(windowedKey.key(), session));
    }

    @Bean
    public KStream<String, AnomalyAlert> anomalyDetection(
            KStream<String, ClickEvent> clicks) {
        return clicks
            .groupByKey(Grouped.with(Serdes.String(), clickEventSerde))
            .windowedBy(TimeWindows.of(Duration.ofMinutes(5)))
            .count(Materialized.as("click-rate-store"))
            .toStream()
            .filter((key, count) -> count > 100)
            .map((key, count) ->
                KeyValue.pair(key.key(),
                    new AnomalyAlert(key.key(), count,
                        "High click rate: " + count + " in 5 min")));
    }

    @Bean
    public InteractiveQueryService interactiveQuery(
            KafkaStreams streams, StreamsBuilder builder) {
        return new InteractiveQueryService(streams);
    }
}
`

## Interactive Queries
`java
@RestController
@RequestMapping("/api/kafka-state")
public class StateQueryController {
    private final KafkaStreams streams;

    @GetMapping("/count/{url}")
    public ResponseEntity<Long> getPageViewCount(@PathVariable String url) {
        ReadOnlyKeyValueStore<String, Long> store =
            streams.store(StoreQueryParameters.fromNameAndType(
                "page-view-counts", QueryableStoreTypes.keyValueStore()));
        Long count = store.get(url);
        return ResponseEntity.ok(count != null ? count : 0L);
    }

    @GetMapping("/instances")
    public ResponseEntity<Collection<StreamsMetadata>> getInstances() {
        return ResponseEntity.ok(
            streams.metadataForAllStreamsClients());
    }
}
`
"@

System.Collections.Hashtable["STEP_BY_STEP.md"] = @"
# Step-by-Step Kafka Streams Development

## Step 1: Add Dependencies
`xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-streams</artifactId>
    <version>3.7.0</version>
</dependency>
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
`

## Step 2: Configure
`java
@Configuration
@EnableKafkaStreams
public class KafkaStreamsConfig {
    @Bean
    public KafkaStreamsConfiguration kStreamsConfig() {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "my-app");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, customSerde().getClass());
        props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2);
        props.put(StreamsConfig.STATE_DIR_CONFIG, "/tmp/kafka-streams");
        return new KafkaStreamsConfiguration(props);
    }
}
`

## Step 3: Build Topology
`java
@Bean
public KStream<String, Order> processOrders(StreamsBuilder builder) {
    KStream<String, Order> orders = builder.stream("orders");
    KTable<String, Product> products = builder.table("products");

    orders.join(products, (order, product) -> {
        order.setProductName(product.getName());
        order.setCategory(product.getCategory());
        return order;
    }, Joined.with(Serdes.String(), orderSerde(), productSerde()))
        .to("enriched-orders");
    return orders;
}
`

## Step 4: Start Application
`java
@SpringBootApplication
public class KafkaStreamsApp {
    public static void main(String[] args) {
        SpringApplication.run(KafkaStreamsApp.class, args);
    }
}
`

## Step 5: Monitor
`ash
# Check consumer groups
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group my-app --describe

# View state stores
kafka-topics --bootstrap-server localhost:9092 --list | grep my-app
`
"@

System.Collections.Hashtable["COMMON_MISTAKES.md"] = @"
# Common Kafka Streams Mistakes

## 1. Wrong Serde Configuration
`java
// WRONG - no serde specified
KTable<String, Product> products = builder.table("products");

// RIGHT
KTable<String, Product> products = builder.table(
    "products", Consumed.with(Serdes.String(), productSerde()));
`

## 2. State Store Naming Conflicts
`java
// WRONG - duplicate store names
stream1.groupByKey().count(Materialized.as("my-store"));
stream2.groupByKey().count(Materialized.as("my-store"));

// RIGHT - unique names
stream1.groupByKey().count(Materialized.as("store-1"));
stream2.groupByKey().count(Materialized.as("store-2"));
`

## 3. Not Handling Tombstone Records
`java
// WRONG - null values cause NPE
KTable<String, Customer> table = builder.table("customers");
// null value = tombstone (delete)

// RIGHT - handle nulls
table.filter((key, value) -> value != null);
`

## 4. Ignoring Rebalance
`java
// WRONG - no rebalance listener
KafkaStreams streams = new KafkaStreams(topology, config);
streams.start();

// RIGHT - handle rebalance
streams.setStateListener((newState, oldState) -> {
    if (newState == KafkaStreams.State.REBALANCING) {
        // Pause external operations
    }
});
`
"@

System.Collections.Hashtable["DEBUGGING.md"] = @"
# Debugging Kafka Streams

## Common Issues

### Lag Building Up
`ash
# Check consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group app-id --describe
# LAG column tells you how far behind
`

### State Store Corruption
`java
// Reset state stores by changing application ID
// Or clean up local state:
props.put(StreamsConfig.STATE_CLEANUP_DELAY_MS_CONFIG, 10000);
`

### Serialization Errors
`java
// Add error handlers
props.put(StreamsConfig.DEFAULT_DESERIALIZATION_EXCEPTION_HANDLER_CLASS_CONFIG,
    LogAndContinueExceptionHandler.class.getName());
props.put(StreamsConfig.DEFAULT_PRODUCTION_EXCEPTION_HANDLER_CLASS_CONFIG,
    LogAndFailExceptionHandler.class.getName());
`

### Topology Issues
`java
// Print topology description
System.out.println(builder.build().describe());
// Shows: Sources, Processors, Stores, Sinks
`
"@

System.Collections.Hashtable["REFACTORING.md"] = @"
# Refactoring Kafka Streams Applications

## Before: Single Large Topology
`java
builder.stream("input")
    .mapValues(v -> { /* complex logic #1 */ })
    .filter((k, v) -> { /* complex logic #2 */ })
    .groupByKey()
    .count()
    .toStream()
    .to("output");
`

## After: Modular Topologies
`java
// Split into sub-topologies
// Topology 1: Processing
KStream<String, Processed> processed = processInput(builder.stream("input"));

// Topology 2: Aggregation
KTable<String, Long> counts = aggregate(processed);

// Topology 3: Output
outputResults(counts);
`

## Before: Hardcoded Topics
`java
builder.stream("orders");
`

## After: Configuration
`java
@Value("")
private String inputTopic;
@Value("")
private String outputTopic;
`
"@

System.Collections.Hashtable["PERFORMANCE.md"] = @"
# Kafka Streams Performance

## Tuning Parameters
`java
// Performance tuning
props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 100);
props.put(StreamsConfig.NUM_STREAM_THREADS_CONFIG, 4);
props.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 10 * 1024 * 1024L);
props.put(StreamsConfig.MAX_TASK_IDLE_MS_CONFIG, 500);
props.put(StreamsConfig.BUFFERED_RECORDS_PER_PARTITION_CONFIG, 1000);
`

## RocksDB Tuning
`java
props.put(StreamsConfig.ROCKSDB_CONFIG_SETTER_CLASS_CONFIG,
    (RocksDBConfigSetter) (db, config) -> {
        db.setOptions(options -> {
            options.setIncreaseParallelism(4);
            options.setMaxBackgroundJobs(4);
        });
        db.tableFilterOptions(options -> {
            options.setBlockCacheSize(100 * 1024 * 1024L);
            options.setCacheIndexAndFilterBlocks(true);
        });
    }.getClass());
`

## Record Cache
`java
// Disable cache for lower latency
props.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 0);
// Or increase for higher throughput
props.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 50 * 1024 * 1024L);
`
"@

System.Collections.Hashtable["SECURITY.md"] = @"
# Kafka Streams Security

## Authentication
`java
props.put(CommonClientConfigs.SECURITY_PROTOCOL_CONFIG, "SASL_SSL");
props.put(SaslConfigs.SASL_MECHANISM, "SCRAM-SHA-512");
props.put(SaslConfigs.SASL_JAAS_CONFIG,
    "org.apache.kafka.common.security.scram.ScramLoginModule required " +
    "username=\"streams-user\" password=\"streams-pass\";");
`

## TLS/SSL
`java
props.put(CommonClientConfigs.SECURITY_PROTOCOL_CONFIG, "SSL");
props.put(SslConfigs.SSL_TRUSTSTORE_LOCATION_CONFIG, "/path/to/truststore.jks");
props.put(SslConfigs.SSL_TRUSTSTORE_PASSWORD_CONFIG, "password");
props.put(SslConfigs.SSL_KEYSTORE_LOCATION_CONFIG, "/path/to/keystore.jks");
props.put(SslConfigs.SSL_KEYSTORE_PASSWORD_CONFIG, "password");
`

## ACLs
`ash
# Grant permissions for the application
kafka-acls --authorizer-properties zookeeper.connect=localhost:2181 \
  --add --allow-principal User:streams-app \
  --operation read --topic source-topic \
  --operation write --topic sink-topic \
  --operation write --topic my-app-*-changelog
`
"@

System.Collections.Hashtable["ARCHITECTURE.md"] = @"
# Kafka Streams Architecture

## Application Architecture
`
+------------------------------+
|     Kafka Streams App        |
|  +------------------------+  |
|  | Topology               |  |
|  | +--------+ +---------+ |  |
|  | | Source | | Process | |  |
|  | | Topic  | | or      | |  |
|  | | Stream | | Sink    | |  |
|  | +--------+ +---------+ |  |
|  +------------------------+  |
|  | State Stores (RocksDB) |  |
|  +------------------------+  |
+------------------------------+
         |            |
    +----+            +----+
    v                      v
Kafka Topic            Kafka Topic
`

## Spring Boot Integration
`java
@SpringBootApplication
@EnableKafkaStreams
public class KafkaStreamsApplication {
    public static void main(String[] args) {
        SpringApplication.run(KafkaStreamsApplication.class, args);
    }
}
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# Kafka Streams Exercises

## Exercise 1: Word Count
Implement a word count application with Kafka Streams.

## Exercise 2: Stream-Table Join
Join an order stream with a customer table to create enriched orders.

## Exercise 3: Session Window
Implement session window aggregation for user clickstream data.

## Exercise 4: Stateful Processor
Build a custom processor that detects rapid-fire events (10 events in 5 seconds).

## Exercise 5: Interactive Query
Create a REST API that queries state stores for real-time dashboard data.
