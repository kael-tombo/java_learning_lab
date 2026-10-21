# How Apache Flink Works

## Streaming Topology
`java
public class StreamTopology {
    public static void main(String[] args) {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Source
        DataStream<Transaction> transactions = env
            .addSource(kafkaSource)
            .name("Kafka Source");

        // Transformations
        DataStream<EnrichedTransaction> enriched = transactions
            .keyBy(Transaction::getUserId)
            .process(new EnrichmentFunction())
            .name("Enrichment");

        // Windowed Aggregation
        DataStream<AggregateResult> aggregated = enriched
            .keyBy(Transaction::getCategory)
            .window(TumblingEventTimeWindows.of(Time.minutes(5)))
            .aggregate(new RevenueAggregator())
            .name("5min Revenue");

        // Sink
        aggregated.addSink(jdbcSink).name("JDBC Sink");

        env.execute("Transaction Processing Pipeline");
    }
}
`

## Watermark Propagation
`java
// Watermark strategy
DataStream<Event> withTimestamps = stream
    .assignTimestampsAndWatermarks(
        WatermarkStrategy.<Event>forBoundedOutOfOrderness(Duration.ofSeconds(10))
            .withTimestampAssigner((event, ts) -> event.getEventTime()));
`

## Checkpointing Mechanism
`java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
env.enableCheckpointing(10000); // 10 seconds
env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(5000);
env.getCheckpointConfig().setCheckpointTimeout(60000);
env.getCheckpointConfig().setTolerableCheckpointFailureNumber(3);
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# Apache Flink Internals

## Job Execution Architecture
`java
/*
+------------------+     +-------------------+     +------------------+
| JobManager       |     | TaskManager 1     |     | TaskManager 2    |
| +--------------+ |     | +---------------+ |     | +---------------+ |
| | Scheduler    | |     | | Task Slot 1   | |     | | Task Slot 1   | |
| | Checkpoint   | |<--->| | Task Slot 2   | |     | | Task Slot 2   | |
| | Coordinator  | |     | +---------------+ |     | +---------------+ |
| +--------------+ |     +-------------------+     +------------------+
+------------------+
*/
`

## Task Execution
`java
// Operator chaining for performance
env.disableOperatorChaining(); // Disable for debugging
stream.map(new MyMapper()).name("Map1")
      .map(new MyMapper2()).name("Map2")
      .startNewChain() // Start new chain
      .map(new MyMapper3()).name("Map3");
`

## State Backends
`java
// MemoryStateBackend (dev only)
env.setStateBackend(new MemoryStateBackend());

// FsStateBackend (production, state in filesystem)
env.setStateBackend(new FsStateBackend("hdfs://namenode:40010/flink/checkpoints"));

// RocksDBStateBackend (large state, disk-based)
env.setStateBackend(new RocksDBStateBackend("hdfs://namenode:40010/flink/checkpoints"));
`

## Network Stack
`java
// Credit-based flow control
env.setBufferTimeout(100); // Default 100ms
// TaskManager network memory
// config set taskmanager.network.memory.min=64mb
// config set taskmanager.network.memory.max=1gb
`
"@

System.Collections.Hashtable["MATH_FOUNDATION.md"] = @"
# Math Foundation for Flink

## Parallelism Calculation
`
Throughput = EventCount / Time
ProcessingTime = EventsProcessed / Parallelism
NetworkLatency = ShuffleSize / Bandwidth

Optimal Parallelism = min(SourcePartitions, TargetCores)
MaxParallelism = 32768 (default, can increase)
`

## Checkpoint Cost
`
CheckpointDuration = StateSize / SnapshotBandwidth
AlignTime = MaxInFlightBytes / NetworkBandwidth
TotalCheckpointTime = CheckpointDuration + AlignTime
Goal: < 1% of processing time
`

## Watermark Delay
`
Watermark = Min(EventTimes in Buffer) - MaxOutOfOrderness
EventTimeProgress = Watermark / WallClock
LateEventFraction = LateEvents / TotalEvents
LateEventHandlingLatency = SideOutputBufferTime
`

## Window Calculations
`
Tumbling = Floor(EventTime / WindowSize) * WindowSize
Sliding = Floor(EventTime / Slide) * Slide
WindowCount = WindowSize / Slide
SessionGapThreshold = InactivityGap

StateSize = Keys * Window * WindowStatePerKey
`
"@

System.Collections.Hashtable["VISUAL_GUIDE.md"] = @"
# Visual Guide to Apache Flink

## Streaming Dataflow
`
Source: Kafka
  |
  v
Map: Parse JSON
  |
  v
KeyBy: customer_id
  |
  v
Window: Tumbling 5min
  |
  v
Aggregate: SUM(amount)
  |
  v
Sink: PostgreSQL
`

## Checkpointing
`
Time ----> t0 ----- t1 ----- t2 ----- t3 ----- t4
           |        |        |        |
           v        v        v        v
         +------+ +------+ +------+ +------+
         | Chk  | | Proc | | Chk  | | Proc |
         | 1    | |      | | 2    | |      |
         +------+ +------+ +------+ +------+
                    | Failure |
                    v
         Restore from Checkpoint 1
         +------+ +------+
         | Chk  | | Proc |
         | 1r   | | replay|
         +------+ +------+
`

## Watermark Progress
`
Event Time -->
  10:00   10:01   10:02   10:03   10:04   10:05   10:06
  |       |       |       |       |       |       |
  e1      e2      e3      e4      e5      e6
                      |
                    W=10:02  (max out-of-order = 30s)
                            W=10:03
                                    W=10:04
                                            W=10:05
                                                    W=10:06
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: Apache Flink

## Complex Event Processing
`java
public class FraudDetector extends KeyedProcessFunction<String, Transaction, Alert> {
    private final transient ValueState<Double> lastAmountState;
    private final transient ValueState<Long> lastTimestampState;
    private static final double THRESHOLD = 1000.0;
    private static final long TIME_WINDOW_MS = 60000;

    @Override
    public void open(Configuration parameters) {
        ValueStateDescriptor<Double> amountDesc =
            new ValueStateDescriptor<>("lastAmount", Types.DOUBLE);
        lastAmountState = getRuntimeContext().getState(amountDesc);

        ValueStateDescriptor<Long> timeDesc =
            new ValueStateDescriptor<>("lastTimestamp", Types.LONG);
        lastTimestampState = getRuntimeContext().getState(timeDesc);
    }

    @Override
    public void processElement(Transaction transaction, Context ctx, Collector<Alert> out) {
        Double lastAmount = lastAmountState.value();
        Long lastTimestamp = lastTimestampState.value();

        if (lastAmount != null && lastTimestamp != null) {
            long timeDiff = transaction.getTimestamp() - lastTimestamp;
            if (timeDiff < TIME_WINDOW_MS &&
                transaction.getAmount() > THRESHOLD &&
                lastAmount > THRESHOLD) {
                out.collect(new Alert("Suspicious activity: multiple large transactions",
                    transaction.getAccountId()));
            }
        }

        lastAmountState.update(transaction.getAmount());
        lastTimestampState.update(transaction.getTimestamp());

        // Register timer to clear state after 5 minutes
        ctx.timerService().registerEventTimeTimer(
            transaction.getTimestamp() + 300000);
    }

    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<Alert> out) {
        lastAmountState.clear();
        lastTimestampState.clear();
    }
}
`

## Custom Window Aggregate
`java
public class AverageAggregate
    implements AggregateFunction<Transaction, AverageAccumulator, Double> {

    @Override
    public AverageAccumulator createAccumulator() {
        return new AverageAccumulator();
    }

    @Override
    public AverageAccumulator add(Transaction value, AverageAccumulator acc) {
        acc.sum += value.getAmount();
        acc.count++;
        return acc;
    }

    @Override
    public Double getResult(AverageAccumulator acc) {
        return acc.count == 0 ? 0.0 : acc.sum / acc.count;
    }

    @Override
    public AverageAccumulator merge(AverageAccumulator a, AverageAccumulator b) {
        a.sum += b.sum;
        a.count += b.count;
        return a;
    }

    public static class AverageAccumulator {
        double sum = 0.0;
        long count = 0;
    }
}
`

## Side Output for Late Data
`java
public class LateDataHandler {
    private static final OutputTag<Transaction> lateOutputTag =
        new OutputTag<Transaction>("late-data") {};

    public DataStream<Transaction> processMainStream(DataStream<Transaction> stream) {
        SingleOutputStreamOperator<Transaction> processed = stream
            .keyBy(Transaction::getCategory)
            .window(TumblingEventTimeWindows.of(Time.hours(1)))
            .sideOutputLateData(lateOutputTag)
            .aggregate(new MyAggregate());

        // Handle late data separately
        DataStream<Transaction> lateStream = processed.getSideOutput(lateOutputTag);
        lateStream.addSink(new LateDataSink());

        return processed;
    }
}
`
"@

System.Collections.Hashtable["STEP_BY_STEP.md"] = @"
# Step-by-Step Flink Development

## Step 1: Setup Project
`xml
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-java</artifactId>
    <version>1.18.0</version>
</dependency>
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-streaming-java</artifactId>
    <version>1.18.0</version>
</dependency>
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-connector-kafka</artifactId>
    <version>3.0.0</version>
</dependency>
`

## Step 2: Create Environment
`java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
env.setParallelism(4);
env.enableCheckpointing(10000);
`

## Step 3: Add Source
`java
Properties kafkaProps = new Properties();
kafkaProps.setProperty("bootstrap.servers", "localhost:9092");
kafkaProps.setProperty("group.id", "flink-consumer");

DataStream<String> raw = env.addSource(
    new FlinkKafkaConsumer<>("input-topic",
        new SimpleStringSchema(), kafkaProps));
`

## Step 4: Transform
`java
DataStream<Event> events = raw
    .map(new JsonDeserializer())
    .assignTimestampsAndWatermarks(...)
    .keyBy(Event::getKey)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .aggregate(new CountAggregate());
`

## Step 5: Add Sink
`java
events.addSink(new FlinkKafkaProducer<>("output-topic",
    new EventSerializer(), kafkaProps));
`

## Step 6: Submit
`ash
./bin/flink run -m yarn-cluster -p 10 \
  -c com.example.FlinkJob \
  my-job.jar
`
"@

System.Collections.Hashtable["COMMON_MISTAKES.md"] = @"
# Common Flink Mistakes

## 1. Wrong Time Characteristic
`java
// WRONG - using processing time for event-time logic
env.setStreamTimeCharacteristic(TimeCharacteristic.ProcessingTime);

// RIGHT
env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
`

## 2. No Watermark Strategy
`java
// WRONG - no watermarks assigned
stream.keyBy(...).window(TumblingEventTimeWindows.of(Time.hours(1)));

// RIGHT
stream.assignTimestampsAndWatermarks(WatermarkStrategy
    .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(10))
    .withTimestampAssigner((e, ts) -> e.getTimestamp()));
`

## 3. Ignoring State Backend
`java
// WRONG - default is JVM heap (can OOM)
// RIGHT - use RocksDB for large state
env.setStateBackend(new RocksDBStateBackend("hdfs://checkpoints/"));
`

## 4. Missing Checkpoint Config
`java
// WRONG - no checkpointing configured
env.enableCheckpointing(0);

// RIGHT
env.enableCheckpointing(5000);
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(500);
`
"@

System.Collections.Hashtable["DEBUGGING.md"] = @"
# Debugging Apache Flink

## Common Issues

### Backpressure
`java
// Monitor in Flink Web UI
// Tasks with high backpressure show in red
// Check: Source -> Operator -> Sink backpressure chain

// Fix: Increase parallelism, optimize operators
stream.setParallelism(10);
`

### Watermark Not Advancing
`java
// Check if watermarks are progressing
// Fix: Ensure timestamps are monotonic
// Verify source is providing events with valid timestamps
env.getConfig().setAutoWatermarkInterval(200); // 200ms
`

### Checkpoint Failures
`java
// Check Flink logs for checkpoint failures
env.getCheckpointConfig().setTolerableCheckpointFailureNumber(5);
// Increase timeout if state is large
env.getCheckpointConfig().setCheckpointTimeout(120000);
`

### Serialization Issues
`java
// Register custom types with Kryo
env.getConfig().registerKryoType(MyCustomType.class);
env.getConfig().registerPojoType(MyPojo.class);
env.getConfig().disableGenericTypes(); // Fail fast on unregistered types
`
"@

System.Collections.Hashtable["REFACTORING.md"] = @"
# Refactoring Flink Applications

## Before: Monolithic ProcessFunction
`java
stream.process(new MyComplexProcessFunction() {
    // 500 lines with extraction, transformation, enrichment, aggregation
});
`

## After: Modular Operators
`java
// Separate concerns
DataStream<Raw> rawSource = env.addSource(source);
DataStream<Parsed> parsed = rawSource.map(new Parser());
DataStream<Enriched> enriched = parsed.keyBy(...).process(new Enricher());
DataStream<Output> result = enriched.keyBy(...).window(...).aggregate(new Aggregator());
`

## Before: Hardcoded Config
`java
stream.window(TumblingProcessingTimeWindows.of(Time.minutes(5)));
`

## After: Parameterized
`java
@Value("")
private int windowSize;
stream.window(TumblingProcessingTimeWindows.of(Time.of(windowSize, TimeUnit.MINUTES)));
`
"@

System.Collections.Hashtable["PERFORMANCE.md"] = @"
# Flink Performance Optimization

## Tuning Parameters
`java
// Buffer timeout (lower = lower latency, higher CPU)
env.setBufferTimeout(50); // Default 100ms

// Network buffers
// flink-conf.yaml
// taskmanager.network.memory.min: 128mb
// taskmanager.network.memory.max: 1gb
// taskmanager.network.numberOfBuffers: 2048
`

## Operator Chaining
`java
// Control chaining for debugging vs production
env.disableOperatorChaining(); // Debug
// Or chain manually
stream.map(new Op1()).name("op1")
      .map(new Op2()).name("op2");
`

## State Tuning
`java
// RocksDB tuning
RocksDBStateBackend backend = new RocksDBStateBackend(checkpointUri, true);
backend.setPredefinedOptions(PredefinedOptions.SPINNING_DISK_OPTIMIZED_HIGH);
env.setStateBackend(backend);

// Incremental checkpoints
env.getCheckpointConfig().enableUnalignedCheckpoints();
`

## Memory Configuration
`ash
# Managed memory for RocksDB
taskmanager.memory.managed.size: 512mb
# Heap memory
taskmanager.memory.task.heap.size: 2g
# Network buffer memory
taskmanager.memory.network.max: 1g
`
"@

System.Collections.Hashtable["SECURITY.md"] = @"
# Apache Flink Security

## Authentication
`java
// Kerberos authentication
env.getConfig().setGlobalJobParameters(
    new Configuration() {{
        setString("security.kerberos.login.keytab", "/path/to/keytab");
        setString("security.kerberos.login.principal", "flink@REALM");
    }});
`

## SSL Configuration
`java
// Enable SSL for network communication
// flink-conf.yaml
security.ssl.enabled: true
security.ssl.keystore: /path/to/keystore
security.ssl.truststore: /path/to/truststore
`

## Data Encryption
`java
// Encrypt sensitive fields
DataStream<Event> safe = stream.map(event -> {
    event.setSsn(encrypt(event.getSsn()));
    event.setEmail(hash(event.getEmail()));
    return event;
});
`
"@

System.Collections.Hashtable["ARCHITECTURE.md"] = @"
# Apache Flink Architecture

## System Architecture
`
+---------------------------+
|        Flink Client       |
+---------------------------+
          |
          | Submit Job
          v
+---------------------------+
|       JobManager          |
| +----------------------+  |
| | Resource Manager     |  |
| | Dispatcher           |  |
| | JobMaster per Job    |  |
| +----------------------+  |
+---------------------------+
          |
   +------+------+
   |             |
+--v---+   +---v--+
|Task  |   |Task  |
|Mgr 1 |   |Mgr 2 |
+------+   +------+
| Slot1|   | Slot1|
| Slot2|   | Slot2|
+------+   +------+
`

## Spring Boot Integration
`java
@SpringBootApplication
public class FlinkApplication {
    @Bean
    public StreamExecutionEnvironment flinkEnv() {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.enableCheckpointing(5000);
        return env;
    }
}
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# Apache Flink Exercises

## Exercise 1: Word Count (Streaming)
Implement real-time word count reading from a socket or Kafka source.

## Exercise 2: Event-Time Aggregation
Process a stream of transactions, computing 5-minute tumbling window averages by category.

## Exercise 3: Fraud Detection
Use Flink's CEP library to detect patterns like three failed logins in 5 minutes.

## Exercise 4: Stateful Enrichment
Enrich a stream of order events with customer data from a side input/file.

## Exercise 5: Custom Operator
Implement a custom ProcessFunction with timers that alerts if no heartbeats received for 30 seconds.
