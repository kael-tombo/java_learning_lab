# Apache Flink — MINI PROJECT

## Project: Real-time Order Fraud & Revenue Stream

A Flink job with keyed state, event-time windows, timers, and a
two-phase-commit sink into a staging table. Includes a crash-recovery test.

### Scope
- Source: Kafka topic `orders`, 4 partitions, JSON payloads with `event_time`.
- Job 1 `revenue`: event-time 1-minute tumbling + 1-hour sliding windows per merchant.
- Job 2 `fraud`: `KeyedProcessFunction` with per-card velocity state + a 60s timer.
- Sink: upsert into H2/Postgres staging, then a commit table flip.
- Ops: checkpointing every 10s, savepoint command, restore-from-savepoint script.

### Architecture

```
Kafka orders (4 partitions)
   |
watermark strategy: out-of-orderness = 30s, idle-partition = 60s
   |
+-- keyBy(merchantId) --+-- window(TUMBLING 1min).process(RevenueAgg)
|                      +-- window(SLIDING 1h/1min).process(RevenueAgg)
|                      +-- process(VelocityCheck)   [ValueState + Timer]
|
  TwoPhaseCommitSink -> staging_fraud_txn -> (checkpoint complete) -> fact table
```

### Implementation

```java
public class RevenueJob {

    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env =
                StreamExecutionEnvironment.getExecutionEnvironment();
        env.enableCheckpointing(10_000, CheckpointingMode.EXACTLY_ONCE);
        env.getCheckpointConfig().enableExternalizedCheckpoints(
                CheckpointConfig.ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION);
        env.getCheckpointConfig().setCheckpointTimeout(120_000);

        env.setStateBackend(new EmbeddedRocksDBStateBackend(true));   // incremental

        KafkaSource<String> source = KafkaSource.<String>builder()
                .setBootstrapServers("localhost:9092")
                .setTopics("orders")
                .setGroupId("revenue-v1")
                .setStartingOffsets(OffsetsInitializer.earliest())
                .setValueOnlyDeserializer(new SimpleStringSchema())
                .build();

        WatermarkStrategy<Order> wm = WatermarkStrategy
                .<Order>forBoundedOutOfOrderness(Duration.ofSeconds(30))
                .withTimestampAssigner((o, ts) -> o.eventTime().toEpochMilli())
                .withIdleness(Duration.ofSeconds(60));   // prevents a dead partition from stalling

        DataStream<Order> orders = env
                .fromSource(source, wm, "orders-source")
                .uid("orders-source");                    // uid matters: it anchors state

        SingleOutputStreamOperator<Revenue> perMinute = orders
                .keyBy(Order::merchantId)
                .window(TumblingEventTimeWindows.of(Duration.ofMinutes(1)))
                .process(new RevenueAgg());
        perMinute.uid("revenue-1m");

        orders.keyBy(Order::cardId)
              .process(new VelocityCheck(3, 3, Duration.ofSeconds(60)))
              .uid("fraud-velocity")
              .sinkTo(TwoPhaseCommitSink.forJdbc("jdbc:sqlite:revenue.db"));

        env.execute("revenue-and-fraud");
    }
}
```

### Event-time window with a process function

```java
public class RevenueAgg extends ProcessWindowFunction<Order, Revenue, String, TimeWindow> {
    private static final DecimalFormat MONEY = new DecimalFormat("#,##0.00");

    @Override
    public void process(String merchantId, Context ctx,
                        Iterable<Order> in, Collector<Revenue> out) {
        BigDecimal total = BigDecimal.ZERO;
        long orders = 0;
        for (Order o : in) { total = total.add(o.amount()); orders++; }
        if (orders > 0) {
            out.collect(new Revenue(merchantId, ctx.window().getStart(),
                    ctx.window().getEnd(), total, orders));
        }
    }
}
```

### Keyed state + timer for fraud velocity

```java
public class VelocityCheck extends KeyedProcessFunction<String, Order, FraudAlert> {
    private final int maxAttempts;      // 3
    private final int maxAmountCents;   // $300
    private final Duration window;      // 60s
    private transient ValueState<Long> firstSeen;   // transient: not part of state

    @Override
    public void open(Configuration cfg) {
        ValueStateDescriptor<Long> d = new ValueStateDescriptor<>("firstSeen", Long.class);
        firstSeen = getRuntimeContext().getState(d);
    }

    @Override
    public void processElement(Order o, Context ctx, Collector<FraudAlert> out) throws Exception {
        Long first = firstSeen.value();
        if (first == null) {
            first = o.eventTime().toEpochMilli();
            firstSeen.update(first);
            ctx.timerService().registerEventTimeTimer(first + window.toMillis());
        }
        long cents = o.amountCents();
        if (cents > maxAmountCents || tooManyAttempts(o)) {
            out.collect(new FraudAlert(o.cardId(), o.orderId(), cents,
                    o.eventTime(), "velocity"));
        }
    }

    @Override
    public void onTimer(long ts, OnTimerContext ctx, Collector<FraudAlert> out) {
        firstSeen.clear();      // window elapsed: reset the counter
    }
}
```

### Crash-recovery proof

```bash
# terminal 1
flink run -d target/revenue.jar
# terminal 2: mid-run, no clean shutdown
taskkill /F /PID <taskmanager_pid>
# terminal 3: observe recovery from the last completed checkpoint
# assertion: sum(revenue) before crash + sum(revenue) after restore == sum(all events),
#            i.e. no double count, no loss
```

### Stretch
- Add allowed lateness and emit a correction stream when late data changes a window.
- Savepoint a job with 400GB state, rescale to 2x parallelism, restore, measure.
- Compare RocksDB vs heap state backend on the same workload.

## Deliverables
- [ ] Two jobs running against a local Kafka cluster
- [ ] Event-time windows with an explicit watermark and idleness strategy
- [ ] Keyed state + timer fraud check with a reset test
- [ ] Kill -9 test proving no loss and no double count
- [ ] Savepoint + rescale + restore runbook
