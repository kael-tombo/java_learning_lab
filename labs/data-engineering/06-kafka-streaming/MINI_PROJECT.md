# Kafka Streaming — MINI PROJECT

## Project: Event Bus with Outbox, Replay, and DLQ

Build a small event bus on a single-node Kafka: a transactional outbox
publisher, a partitioned consumer with a worker pool, a dead-letter topic, and
an offset-replay CLI.

### Scope
- Topics: `orders.v1` (12 partitions), `orders.dlq.v1` (3), `orders.compact.v1` (12).
- Producer: idempotent, `acks=all`, key = `orderId`, custom header `trace_id`.
- Consumer: manual commit after processing, 2 retries then DLQ.
- Replay: `replay --topic orders.v1 --from 0 --to <offset>` into a scratch topic.
- Metrics: produce rate, consume rate, lag, DLQ depth.

### Architecture

```
[order service DB]
   |  same transaction
[outbox table] -> publisher (poll + send) -> orders.v1 (12 partitions)
                                                     |
                                          +----------+-----------+
                                          |                      |
                                    consumer group A     consumer group B
                                    (billing)            (analytics replay)
                                          |
                              retry(2) -> orders.dlq.v1
```

### Sizing the topic

```java
public record TopicPlan(int partitions, short replication) {}

/**
 * throughput  = records/sec
 * batchSize   = records per producer request
 * bytesPerRec = average serialized record size
 * targetMBps  = throughput * bytesPerRec
 * We aim for <= 40 MB/s per broker (comfortably under default replica fetch limits)
 * and >= 3x headroom for the next growth step, while keeping partition count
 * equal to the maximum consumer parallelism you will ever need.
 */
public static TopicPlan plan(double throughput, int batchSize, int bytesPerRec, int brokers) {
    int perBrokerMBps = 40;
    int needed = (int) Math.ceil(throughput * bytesPerRec * 3 / (double) (perBrokerMBps * 1024 * 1024 * brokers));
    int partitions = Math.max(needed, 1);
    return new TopicPlan(partitions, (short) Math.min(3, brokers));
}
```

### Idempotent producer

```java
Properties p = new Properties();
p.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
p.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
p.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
p.put(ProducerConfig.ACKS_CONFIG, "all");                      // durability
p.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);         // no duplicate-on-retry
p.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5); // allowed under idempotence
p.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);
p.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");
p.put(ProducerConfig.LINGER_MS_CONFIG, 5);
p.put(ProducerConfig.BATCH_SIZE_CONFIG, 64 * 1024);
p.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, 120_000);

KafkaProducer<String, String> producer = new KafkaProducer<>(p);

RecordMetadata md = producer.send(new ProducerRecord<>(
        "orders.v1", order.customerId(), order.json(),
        Map.of("trace_id", order.traceId()))       // headers for cross-system correlation
    ).get(10, TimeUnit.SECONDS);
log.info("stored at {}-{}@{}", md.topic(), md.partition(), md.offset());
```

### Consumer with retry and DLQ

```java
public final class BillingConsumer implements Runnable {
    private final KafkaConsumer<String, String> consumer;
    private final int maxAttempts = 3;

    @Override public void run() {
        consumer.subscribe(List.of("orders.v1"));
        while (running) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(500));
            for (ConsumerRecord<String, String> rec : records) {
                if (!processWithRetry(rec)) {
                    sendToDlq(rec, "permanent failure after " + maxAttempts);
                }
                consumer.commitSync(Map.of(TopicPartition.of(rec.topic(), rec.partition()),
                        new OffsetAndMetadata(rec.offset() + 1)));   // commit AFTER handling
            }
        }
    }

    private boolean processWithRetry(ConsumerRecord<String, String> rec) {
        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try { handler.handle(rec); return true; }
            catch (TransientException e) { sleep(backoff(attempt)); }
            catch (Exception e) { log.error("permanent", e); return false; }
        }
        return false;
    }
}
```

### Replay

```java
public long replay(String source, String sinkTopic, long from, long to) {
    KafkaConsumer<String, String> src = newReader(source);
    List<TopicPartition> tps = src.partitionsFor(source).stream()
            .map(p -> new TopicPartition(source, p.partition())).toList();
    src.assign(tps);                                  // assign, not subscribe: no rebalance
    src.seekToBeginning(tps);
    for (TopicPartition tp : tps) src.seek(tp, Math.max(from, 0));
    src.seekToEnd(tps);
    for (TopicPartition tp : tps) src.seek(tp, Math.min(to, src.position(tp)));

    KafkaProducer<String, String> out = newProducer();
    long n = 0;
    for (ConsumerRecord<String, String> r : src.pollUntilCaughtUp()) {
        out.send(new ProducerRecord<>(sinkTopic, r.key(), r.value(),
                new RecordHeaders(r.headers().toArray())));
        n++;
    }
    return n;
}
```

### Compacted topic (state as a log)

```bash
# log compaction keeps the latest value per key, forever-ish
kafka-topics.sh --create --topic orders.compact.v1 \
  --partitions 12 --config cleanup.policy=compact \
  --config min.cleanable.dirty.ratio=0.1 \
  --config delete.retention.ms=86400000
```

### Stretch
- Add a schema check (Avro/JSON Schema) and fail the consumer on BREAKING change.
- Measure rebalance duration with and without `group.instance.id`.
- Add a lag exporter and a Grafana panel.

## Deliverables
- [ ] Sizing calculation with a documented formula
- [ ] Idempotent producer with `acks=all` and in-flight settings justified
- [ ] Consumer with retry, DLQ routing, and commit-after-process
- [ ] Replay CLI with a scratch-topic output and a count check
- [ ] Compaction demo with a before/after record count
- [ ] Runbook for a lag incident
