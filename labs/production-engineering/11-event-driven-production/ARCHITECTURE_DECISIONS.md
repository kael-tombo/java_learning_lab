# ARCHITECTURE DECISIONS: Event-Driven Infrastructure Standards
## Lab 11 | Production Engineering Academy — Top 0.0001% Engineering

---

## ADR-01: Transactional Outbox Pattern — Mandatory for All State-Changing Services

**Status**: ACCEPTED (2025-Q2)
**Deciders**: Platform Architects, SRE Lead, Engineering VP

### Context
Dual-write inconsistencies between PostgreSQL and the Kafka event bus led to reconciliation
discrepancies totaling $2.3M in missing/phantom order events during a Black Friday network
partition event. 1,081 orders were affected. Root cause: `kafkaTemplate.send()` called inside
or immediately after `@Transactional` blocks — two separate I/O operations with no atomic guarantee.

### Decision
1. **Direct Kafka produce from service layer is BANNED.** Any `kafkaTemplate.send()` call outside
   of a dedicated publisher component will fail code review and the CI `archunit` gate:
   ```java
   // ArchUnit rule — enforced in CI pipeline
   noClasses().that().resideInAPackage("..service..")
       .should().callMethodWhere(target().hasName("send")
           .and(target().getOwner().isAssignableTo(KafkaTemplate.class)));
   ```
2. **Transactional Outbox Pattern is mandatory.** All domain events must be written to an
   `outbox_events` table within the same ACID transaction as the business entity.
3. **Debezium CDC** reads PostgreSQL WAL and publishes to Kafka. Outbox rows routed to topic
   `outbox.{aggregateType}` via the Debezium `EventRouter` SMT.
4. **Replication slot monitoring**: Prometheus alert at 5 GB WAL lag, automated pg_cron slot
   drop if inactive > 30 minutes.

### Consequences
- **Positive**: Zero event loss even during Kafka broker or network outages.
- **Positive**: Events published in strict DB transaction order (WAL sequence).
- **Negative**: Requires maintaining Debezium Kafka Connect infrastructure (+2 pods, +1 PostgreSQL replication user).
- **Negative**: Adds ~2ms latency (DB write + WAL read) vs direct produce (~0.5ms). Acceptable for all current SLAs.

---

## ADR-02: LMAX Disruptor for HFT and Sub-Millisecond Event Pipelines

**Status**: ACCEPTED (2026-Q1)
**Deciders**: Platform Architects, HFT Engineering Lead

### Context
The trading pipeline processing market data and order events was using a standard Spring Kafka
listener with `ExecutorService` thread pool. At 500,000 events/sec, GC pressure from per-event
object allocation caused P99.9 latency of 12ms and P99.99 of 80ms — exceeding the 5ms SLA.

### Decision
1. **LMAX Disruptor replaces Spring Kafka listener** for all pipelines with P99 latency < 500µs
   or throughput > 100,000 events/sec.
2. **ProducerType.SINGLE** is mandated for all single-threaded Kafka poll loops (eliminates CAS overhead).
3. **BusySpinWaitStrategy** is mandated only on pods with isolated cores (`isolcpus` kernel param).
   All other deployments use `YieldingWaitStrategy`.
4. **`OrderEvent` pre-allocation** with all-primitive fields (no `byte[]`, no `String` in the
   hot-path event object). Customer IDs encoded as `long[4]`.
5. **Buffer size formula**: `bufferSize = nextPowerOfTwo(max_consumer_slowdown_ms × throughput_per_ms × 2)`

### Consequences
- **Positive**: P99 latency reduced from 12ms → 180µs. P99.99: 80ms → 2µs.
- **Positive**: Zero GC allocation on the hot event path.
- **Negative**: BusySpinWaitStrategy consumes 100% of one CPU core per Disruptor instance.
  Requires node-level CPU isolation setup (DevOps responsibility).
- **Negative**: Disruptor is a complex library — only engineers who have completed Lab 11
  (Disruptor certification) are permitted to modify Disruptor-based pipelines.

---

## ADR-03: Confluent Schema Registry — Mandatory for All Production Topics

**Status**: ACCEPTED (2025-Q4)
**Deciders**: Platform Architects, Data Engineering Lead

### Context
A partner service added a new field to their event schema without coordinating with consumers.
Three consumer services threw `UnrecognizedPropertyException` and sent 400,000 records to the DLQ.
Manual schema coordination was identified as the root cause — no formal schema contract enforcement.

### Decision
1. **Schema Registry is mandatory** for all topics with more than one producer OR more than
   one consumer team.
2. **Compatibility mode = `BACKWARD`** for all topics by default:
   - Consumers on schema v(N) can read messages produced with schema v(N+1).
   - New fields in v(N+1) MUST have default values in Avro/Protobuf.
   - Fields CANNOT be removed without a compatibility mode change (requires architect approval).
3. **Avro is the preferred serialization format** for structured domain events.
   JSON is permitted only for external API events where schema enforcement is impossible.
4. **Schema validation in CI**: Producer services must run `schema-registry-maven-plugin:test-compatibility`
   against the registry before merging schema changes.

```xml
<!-- pom.xml — CI schema validation -->
<plugin>
  <groupId>io.confluent</groupId>
  <artifactId>kafka-schema-registry-maven-plugin</artifactId>
  <version>7.5.0</version>
  <configuration>
    <schemaRegistryUrls>
      <param>http://schema-registry:8081</param>
    </schemaRegistryUrls>
    <subjects>
      <orders-value>src/main/avro/OrderEvent.avsc</orders-value>
    </subjects>
    <compatibilityLevels>
      <orders-value>BACKWARD</orders-value>
    </compatibilityLevels>
  </configuration>
</plugin>
```

### Consequences
- **Positive**: Schema incompatibilities caught at CI time, not production.
- **Positive**: Avro binary encoding reduces message size by 60–70% vs JSON.
- **Negative**: Requires managing Schema Registry infrastructure (+2 pods).
- **Negative**: Avro schema evolution learning curve for teams unfamiliar with Avro IDL.

---

## ADR-04: Kafka Streams Exactly-Once Semantics (EOS v2) for All Stateful Pipelines

**Status**: ACCEPTED (2026-Q2)
**Deciders**: Platform Architects, Data Engineering Lead

### Context
The order aggregation pipeline using Kafka Streams with default `processing.guarantee=at_least_once`
produced duplicate records after broker failovers. Zombie task fencing was not enabled.
Duplicate orders in the aggregation topic caused billing to charge customers twice for the same order.

### Decision
1. **All stateful Kafka Streams applications MUST use `EXACTLY_ONCE_V2`**:
   ```java
   props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG,
             StreamsConfig.EXACTLY_ONCE_V2); // Requires Kafka 2.5+, broker ≥ 2.5
   ```
2. **Commit interval tuned per application**:
   - Low-latency pipelines: `commit.interval.ms=50`
   - High-throughput pipelines: `commit.interval.ms=500`
3. **Zombie fencing validation**: All Kafka Streams deployments must log `ProducerFencedException`
   on broker failover (proves fencing is active). Missing this log during chaos testing fails
   the certification gate.
4. **`at_least_once` is permitted ONLY for**: Pure analytics pipelines where duplicates in
   output are acceptable and explicitly documented in the service's runbook.

### Consequences
- **Positive**: Zero duplicate records after broker failover.
- **Positive**: Zombie tasks fenced via producer epoch — no manual intervention required.
- **Negative**: ~5% throughput reduction due to transaction overhead per commit interval.
- **Negative**: Requires Kafka brokers >= 2.5. Older broker versions require migration first.


---

## ADR-01: Guaranteed Delivery Architecture (Transactional Outbox Standard)

### Status: ACCEPTED

### Context
Dual-write inconsistencies between relational databases and Kafka event buses led to reconciliation discrepancies totaling $2.3M in missing order events during network partition events in 2025.

### Decisions
1. **Direct Dual-Writing Banned**:
   - Calling Kafka `producer.send()` inside or immediately following a JPA/JDBC transaction is strictly prohibited.
2. **Transactional Outbox Mandate**:
   - All state-changing services must implement the Transactional Outbox pattern.
   - Outbox tables must be co-located in the same database and transaction as the domain aggregate.
   - Event extraction via **Debezium CDC (Change Data Capture)** reading PostgreSQL WAL (Write-Ahead Log) into Kafka.
3. **Partitioning & Consumer Standards**:
   - Minimum replication factor = 3, `min.insync.replicas = 2`, producer `acks = all`.
   - Consumer groups must use `CooperativeStickyAssignor` to eliminate Stop-the-world rebalance storms.
   - All consumers must implement Dead Letter Queues (DLQ) with exponential backoff.

### Consequences
- Zero event loss even during database or Kafka broker outages.
- Requires maintaining Debezium Kafka Connect infrastructure.
