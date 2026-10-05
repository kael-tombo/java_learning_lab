# Apache Flink (Advanced) — MINI PROJECT

## Project: Flink SQL + CEP Lakehouse Ingest

Three jobs in one project: (1) a Table API job reading CDC from Kafka and
upserting to a lakehouse table, (2) a CEP job detecting sequence patterns, and
(3) a dimensional join in SQL with a time-travel lookup.

### Scope
- Job A: `StreamTableJob` — dynamic tables, upsert sink, event time, watermarks.
- Job B: `PatternJob` — CEP with contiguity, timeouts, and after-match skip.
- Job C: `LakehouseSink` — two-phase commit into a Delta/Iceberg-style table.
- Table: `catalog` with a Flink-managed dimension table for a temporal join.
- Ops: savepoint/rescale script, RocksDB tuning notes.

### Architecture

```
Kafka CDC topic (orders, PK changes)
   |
StreamTableJob  (Flink SQL via Table API)
   |-- TEMPORARY VIEW orders_cdc
   |-- event-time attribute: ts  (WATERMARK FOR ts AS ...)
   |-- GROUP BY window (1h) -> agg table
   v
iceberg/upsert sink  (exactly-once, partitioned by window_start)

Kafka payments topic
   |
PatternJob (CEP):  payment -> chargeback within 72h
   v
alerts topic + sink
```

### Implementation — Table API with event time

```java
EnvironmentSettings settings = EnvironmentSettings.newInstance()
        .inStreamingMode()
        .build();

StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
env.enableCheckpointing(30_000, CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig().setCheckpointStorage("s3://ckpt/orders/");

TableEnvironment tEnv = StreamTableEnvironment.create(env, settings);
tEnv.executeSql("""
    CREATE TABLE kafka_orders (
      order_id     STRING,
      customer_id  STRING,
      amount       DECIMAL(12,2),
      status       STRING,
      ts           TIMESTAMP_LTZ(3),
      proc_time    AS proc_time(),
      WATERMARK FOR ts AS ts - INTERVAL '20' SECOND
    ) WITH (
      'connector' = 'kafka',
      'topic' = 'orders.cdc.v1',
      'properties.bootstrap.servers' = 'localhost:9092',
      'format' = 'json',
      'scan.startup.mode' = 'earliest-offset'
    )""");

// Dimensional join needs a lookup source; a registered Flink table is the
// pragmatic option when the dimension is small and changes slowly.
tEnv.executeSql("""
    CREATE TEMPORARY TABLE dim_customer (
      customer_id  STRING,
      segment      STRING,
      country      STRING,
      updated_at   TIMESTAMP_LTZ(3),
      PRIMARY KEY (customer_id) NOT ENFORCED
    ) WITH ('connector' = 'upsert-kafka', ...)""");

Table agg = tEnv.sqlQuery("""
    SELECT window_start, window_end, customer_id, segment,
           COUNT(*)                       AS orders,
           SUM(amount)                   AS revenue,
           COUNT_IF(status = 'COMPLETED') AS completed
      FROM TABLE(TUMBLE(TABLE kafka_orders, DESCRIPTOR(ts), INTERVAL '1' HOUR))
      JOIN dim_customer FOR SYSTEM_TIME AS OF ts
        ON kafka_orders.customer_id = dim_customer.customer_id
     GROUP BY window_start, window_end, customer_id, segment""");

tEnv.executeSql("CREATE TABLE iceberg_sales ("
        + " window_start TIMESTAMP(3), window_end TIMESTAMP(3),"
        + " customer_id STRING, segment STRING, orders BIGINT,"
        + " revenue DECIMAL(20,2), completed BIGINT,"
        + " PRIMARY KEY (window_start, customer_id)) NOT ENFORCED"
        + " WITH ('connector' = 'iceberg', 'catalog-type' = 'hadoop', ...)");

// The append-only path is wrong for a windowed aggregate: an upsert sink keyed
// by (window_start, customer_id) is what makes re-runs and restarts idempotent.
agg.executeInsert("iceberg_sales").await();
```

### CEP: payment then chargeback within 72h

```java
public final class ChargebackPatternJob {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env =
                StreamExecutionEnvironment.getExecutionEnvironment();
        env.enableCheckpointing(30_000);

        KeySelector<Payment, String> byAccount = p -> p.accountId();
        Pattern<Payment, ?> pattern = Pattern.<Payment>begin("payment", AfterMatchSkipStrategy.skipPastLastEvent())
                .where(new SimpleCondition<>() {
                    @Override public boolean filter(Payment p) {
                        return p.amount().compareTo(new BigDecimal("50")) > 0;
                    }
                })
                .followedByAny("chargeback")            // contiguity is NOT required
                .where(new SimpleCondition<>() {
                    @Override public boolean filter(Payment p) { return p.type() == CHARGEBACK; }
                })
                .within(Duration.ofHours(72));          // timeout: emit partial matches too

        PatternStream<Payment> ps = env.fromSource(source, wm, "payments")
                .keyBy(byAccount)
                .pattern(pattern)
                .sideOutputLateData(lateTag)            // do not silently drop
                .process(new AlertFunction());

        env.execute("chargeback-detection");
    }
}
```

The contiguity choice is the whole point of CEP and worth stating in review:

```java
// followedBy   -> strict contiguity: nothing may intervene. Right for
//                 "login then password-reset", where anything in between
//                 means it was not the same intent.
// followedByAny -> relaxed: other events may occur. Right for chargebacks.
// skippingToNext / skipPastLastEvent -> control match cardinality when a
//                 pattern would otherwise produce a combinatorial number of matches.
```

### Pattern process function

```java
public class AlertFunction extends PatternProcessFunction<Payment, ChargebackAlert> {
    private final Map<Long, List<Payment>> partials = new HashMap<>();

    @Override
    public void processMatch(Map<String, List<Payment>> match, Context ctx,
                             Collector<ChargebackAlert> out) {
        List<Payment> payment = match.get("payment");
        List<Payment> cb = match.get("chargeback");
        if (payment.isEmpty() || cb.isEmpty()) return;         // partial match from timeout
        out.collect(new ChargebackAlert(
                payment.get(0).accountId(),
                payment.get(0).amount(),
                cb.get(0).ts(),
                ctx.timestamp(),
                "payment>50 followed by chargeback within 72h"));
    }
}
```

### Rescale via savepoint

```bash
# 1. stop with a savepoint that retains state
#    (flink stop -s /tmp/savepoint -p 128 <jobid> for the classic CLI)
# 2. resume with the same savepoint at higher parallelism
#    (flink run -d -s /tmp/savepoint/savepoint-xxx -p 128 target.jar)
# 3. measure: state redistribution time, and the cold-start gap before output resumes
```

```java
// RocksDB tuning that matters at 900GB state
Configuration rocks = new Configuration();
rocks.setString("state.backend.rocksdb.memory.managed", "true");
rocks.setString("state.backend.rocksdb.compaction.level.use-dynamic-size", "true");
rocks.setString("state.backend.rocksdb.writebuffer.size", "64mb");
rocks.setString("state.backend.rocksdb.block.cache-size", "256mb");
rocks.setString("state.backend.rocksdb.thread.num", "4");   // match managed memory cores
env.configure(rocks);
```

### Stretch
- Implement the same fraud pattern in Flink SQL with a `MATCH_RECOGNIZE`-style
  equivalent and compare readability/maintainability.
- Add a `TUMBLE`/`HOP`/`CUMULATE` comparison on the same data and note latency
  vs state cost for each.
- Add a dedup sink that absorbs CDC upsert storms.

## Deliverables
- [ ] Table API job with event time, watermark, and a temporal dimension join
- [ ] Upsert sink keyed for idempotency, proven by a restart test
- [ ] CEP job with a pattern, a timeout, side outputs, and a documented
      contiguity rationale
- [ ] Savepoint + rescale script with measured recovery time
- [ ] RocksDB tuning note tied to a state size calculation
