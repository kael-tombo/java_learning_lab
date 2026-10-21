# How CDC Works

## Debezium MySQL Connector
`java
public class DebeziumConfig {
    public Configuration createConfig() {
        return Configuration.create()
            // Source database connection
            .with("database.hostname", "mysql-primary.example.com")
            .with("database.port", "3306")
            .with("database.user", "cdc_user")
            .with("database.password", System.getenv("DB_PASSWORD"))
            .with("database.server.id", "12345")

            // Tables to capture
            .with("table.include.list", "db1.orders,db1.customers")

            // Kafka connection
            .with("database.history.kafka.bootstrap.servers", "kafka:9092")
            .with("topic.prefix", "cdc")

            // Snapshots
            .with("snapshot.mode", "initial") // or "schema_only", "when_needed"
            .with("snapshot.locking.mode", "none") // minimize impact

            // Decimal handling
            .with("decimal.handling.mode", "string")

            // Tombstones on delete
            .with("tombstones.on.delete", "true")
            .build();
    }
}
`

## Processing CDC Events with Kafka Streams
`java
public class CdcEventProcessor {
    public KStream<String, JsonNode> processCdcStream() {
        StreamsBuilder builder = new StreamsBuilder();

        KStream<String, JsonNode> cdcEvents = builder
            .stream("cdc.db1.orders",
                Consumed.with(Serdes.String(), jsonSerde()));

        // Parse CDC events
        KStream<String, OrderEvent> parsed = cdcEvents
            .mapValues((KeyValueMapper<String, JsonNode, OrderEvent>) (key, value) -> {
                String op = value.get("op").asText();
                JsonNode after = value.get("after");
                JsonNode source = value.get("source");
                long ts = source.get("ts_ms").asLong();

                switch (op) {
                    case "c": return new OrderEvent(Operation.CREATE, after, ts);
                    case "u": return new OrderEvent(Operation.UPDATE, after, ts);
                    case "d": return new OrderEvent(Operation.DELETE,
                        value.get("before"), ts);
                    case "r": return new OrderEvent(Operation.SNAPSHOT, after, ts);
                    default: return null;
                }
            })
            .filter((key, event) -> event != null);

        // Write to different targets based on operation
        parsed.filter((k, e) -> e.getOperation() == Operation.CREATE
            || e.getOperation() == Operation.UPDATE)
            .to("enriched-orders", Produced.with(Serdes.String(), orderEventSerde()));

        parsed.filter((k, e) -> e.getOperation() == Operation.DELETE)
            .to("deleted-orders", Produced.with(Serdes.String(), orderEventSerde()));

        return parsed;
    }
}
`

## Kafka Connect Sink
`java
// Sink connector writing CDC events to S3
// PUT /connectors/cdc-s3-sink/config
{
    "name": "s3-sink-connector",
    "config": {
        "connector.class": "io.confluent.connect.s3.S3SinkConnector",
        "tasks.max": "1",
        "topics": "cdc.db1.orders",
        "s3.bucket.name": "data-lake",
        "s3.region": "us-east-1",
        "flush.size": "1000",
        "storage.class": "io.confluent.connect.s3.storage.S3Storage",
        "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
        "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
        "path.format": "'year'=YYYY/'month'=MM/'day'=dd/'hour'=HH",
        "locale": "en-US",
        "timezone": "UTC"
    }
}
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# CDC Internals

## MySQL Binlog Reading
`java
/*
MySQL binary log (binlog) contains all database changes.
Debezium positions itself as a MySQL replica:
1. Connects as a slave
2. Requests binlog stream from specific position
3. Parses binlog events (WriteRows, UpdateRows, DeleteRows)
4. Converts to Debezium change events
5. Stores offset in Kafka for resume capability

Binlog formats:
- STATEMENT: SQL statements (not recommended for CDC)
- ROW: Actual row changes (recommended for Debezium)
- MIXED: Statement or row based on operation
*/
`

## Offset Management
`java
// Debezium stores offsets for resume capability
// Offset stored in Kafka topic: connect-offsets
// Structure:
{
    "sourcePartition": {
        "server": "my-connector"
    },
    "sourceOffset": {
        "file": "mysql-bin.000123",
        "pos": 45678,
        "gtids": "12345678-1234-1234-1234-123456789012:1-1234"
    }
}
`

## Snapshot Process
`java
/*
1. Connector starts
2. Check existing offset -> no offset found
3. Determine snapshot mode (initial)
4. Lock tables (optional, configurable)
5. Read current binlog position
6. Export table data (SELECT * FROM table)
7. Release locks
8. Emit snapshot events (op: 'r')
9. Start streaming from recorded binlog position
10. Normal CDC streaming begins
*/
`
"@

System.Collections.Hashtable["MATH_FOUNDATION.md"] = @"
# Math Foundation for CDC

## Throughput and Lag
`
Change Rate = DML_ops / second
CDC Throughput = Min(BinlogReadRate, KafkaProduceRate, NetworkBandwidth)
ReplicationLag = CurrentTime - LastCommittedTimestamp

Lag = Max(SourceLogPosition - ConsumedLogPosition) / BinlogRate
CatchupTime = LagSize / (ConsumeRate - ChangeRate)
`

## Snapshot Size
`
SnapshotTime = SUM(table_sizes) / ReadThroughput
SnapshotEvents = SUM(row_counts)
MemoryDuringSnapshot = MaxTableSize * RowSize * BufferFactor
`

## Offset Storage
`
OffsetPerTable = PositionBytes + GtidInfo + Metadata
TotalOffsetSize = OffsetPerTable * Tables * Replicas
Retention = OffsetSize * MaxOffsetAge
`

## Event Size
`
CDCEventSize = KeySize + ValueSize + MetadataOverhead
KeySize = PrimaryKeyColumns * AvgColumnSize
ValueSize = BeforeSize + AfterSize + SourceMetadata

NetworkLoad = CDCEventSize * ChangeRate * Consumers
StorageNeeded = CDCEventSize * ChangeRate * Retention
`
"@

System.Collections.Hashtable["VISUAL_GUIDE.md"] = @"
# Visual Guide to CDC

## CDC Architecture
`
Source Database          Debezium              Kafka              Consumers
+----------------+     +------------+     +------------+     +--------------+
| MySQL          |     | Debezium   |     | Kafka      |     | Streaming    |
| +------------+ |     | Connector  |     | Topic:     |     | Processor    |
| | Binlog     |----->| (Kafka     |----->| cdc.db1.   |----->| (Flink/     |
| | 000123     | |     |  Connect)  |     | orders     |     |  KStreams)  |
| +------------+ |     +------------+     +------------+     +--------------+
|                |                                            |              |
| +------------+ |                                            | Data Lake   |
| | Table:     | |     +------------+     +------------+      | or          |
| | orders     | |     | Debezium   |     | Kafka      |     | Warehouse   |
| | customers  | |     | Connector  |----->| Topic:     |----->|             |
| +------------+ |     | (Kafka     |     | cdc.db1.   |     +--------------+
+----------------+     |  Connect)  |     | customers  |
                       +------------+     +------------+
`

## Change Event Examples
`
INSERT (op: c)
{
  "schema": {...},
  "payload": {
    "op": "c",
    "before": null,
    "after": {
      "id": 1001,
      "name": "Jane Doe",
      "email": "jane@example.com"
    },
    "source": {
      "db": "inventory",
      "table": "customers",
      "ts_ms": 1704067200000
    }
  }
}

UPDATE (op: u)
{
  "payload": {
    "op": "u",
    "before": {"id": 1001, "name": "Jane Doe"},
    "after": {"id": 1001, "name": "Jane Smith"},
    "source": {...}
  }
}

DELETE (op: d)
{
  "payload": {
    "op": "d",
    "before": {"id": 1001, ...},
    "after": null,
    "source": {...}
  }
}
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: CDC Implementation

## Complete Debezium + Kafka Connect Setup

### 1. Spring Boot Configuration
`java
@Configuration
public class CdcConfig {

    @Bean
    public DebeziumEngine<ChangeEvent<String, String>> debeziumEngine() {
        Properties props = new Properties();
        props.setProperty("name", "mysql-connector");
        props.setProperty("connector.class", "io.debezium.connector.mysql.MySqlConnector");
        props.setProperty("offset.storage", "org.apache.kafka.connect.storage.FileOffsetBackingStore");
        props.setProperty("offset.storage.file.filename", "/tmp/offsets.dat");
        props.setProperty("offset.flush.interval.ms", "60000");
        props.setProperty("database.hostname", System.getenv("DB_HOST"));
        props.setProperty("database.port", System.getenv("DB_PORT"));
        props.setProperty("database.user", System.getenv("DB_USER"));
        props.setProperty("database.password", System.getenv("DB_PASSWORD"));
        props.setProperty("database.server.id", "184054");
        props.setProperty("topic.prefix", "cdc");
        props.setProperty("schema.history.internal",
            "io.debezium.storage.file.history.FileSchemaHistory");
        props.setProperty("schema.history.internal.file.filename",
            "/tmp/schemahistory.dat");

        return DebeziumEngine.create(Json.class)
            .using(props)
            .notifying(this::handleChangeEvent)
            .build();
    }

    private void handleChangeEvent(ChangeEvent<String, String> event) {
        String key = event.key();
        String value = event.value();

        // Parse JSON and process
        ObjectMapper mapper = new ObjectMapper();
        JsonNode changeEvent = mapper.readTree(value);
        String operation = changeEvent.get("payload").get("op").asText();
        JsonNode after = changeEvent.get("payload").get("after");
        JsonNode source = changeEvent.get("payload").get("source");
        String table = source.get("table").asText();
        long timestamp = source.get("ts_ms").asLong();

        // Route to appropriate handler
        switch (operation) {
            case "c": handleCreate(table, after, timestamp); break;
            case "u": handleUpdate(table,
                changeEvent.get("payload").get("before"), after, timestamp); break;
            case "d": handleDelete(table, after, timestamp); break;
            case "r": handleSnapshot(table, after, timestamp); break;
        }
    }

    private void handleCreate(String table, JsonNode data, long timestamp) {
        // Write to data lake, update cache, etc.
        cdcMetrics.recordCreate(table);
    }

    private void handleUpdate(String table, JsonNode before, JsonNode after, long ts) {
        cdcMetrics.recordUpdate(table);
    }

    private void handleDelete(String table, JsonNode before, long timestamp) {
        cdcMetrics.recordDelete(table);
        // Flag as deleted in warehouse
    }

    private void handleSnapshot(String table, JsonNode data, long timestamp) {
        // Initial load of existing data
        loadSnapshotData(table, data);
    }
}
`

### 2. Kafka Connect REST API
`ash
# Register Debezium source connector
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "inventory-connector",
    "config": {
      "connector.class": "io.debezium.connector.mysql.MySqlConnector",
      "tasks.max": "1",
      "database.hostname": "mysql",
      "database.port": "3306",
      "database.user": "debezium",
      "database.password": "dbz",
      "database.server.id": "184054",
      "topic.prefix": "cdc",
      "database.include.list": "inventory",
      "schema.history.internal.kafka.bootstrap.servers": "kafka:9092",
      "schema.history.internal.kafka.topic": "schemahistory.inventory",
      "key.converter": "org.apache.kafka.connect.json.JsonConverter",
      "value.converter": "org.apache.kafka.connect.json.JsonConverter",
      "key.converter.schemas.enable": "false",
      "value.converter.schemas.enable": "false"
    }
  }'

# Check connector status
curl http://localhost:8083/connectors/inventory-connector/status

# List connectors
curl http://localhost:8083/connectors
`

### 3. Outbox Pattern
`java
// Instead of CDC on the main table, applications write to an outbox table
@Entity
@Table(name = "outbox")
public class OutboxEvent {
    @Id private UUID id;
    private String aggregateType;
    private String aggregateId;
    private String eventType;
    private String payload; // JSON
    private Instant createdAt;

    // Getters
}

// Debezium captures the outbox table
// Each row becomes one Kafka event
// Cleaner than raw table CDC
// The application controls what events to emit
`
"@

System.Collections.Hashtable["STEP_BY_STEP.md"] = @"
# Step-by-Step CDC Setup

## Step 1: Enable Source DB Logging
`sql
-- MySQL: Enable binlog
-- my.cnf
[mysqld]
server-id = 1
log_bin = mysql-bin
binlog_format = ROW
binlog_row_image = FULL
expire_logs_days = 3

-- PostgreSQL: Set WAL level
wal_level = logical
max_replication_slots = 1
max_wal_senders = 1
`

## Step 2: Create CDC User
`sql
CREATE USER 'debezium'@'%' IDENTIFIED BY 'dbz';
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%';
FLUSH PRIVILEGES;
`

## Step 3: Configure Debezium
`properties
# application.properties
debezium.database.hostname=localhost
debezium.database.port=3306
debezium.database.user=debezium
debezium.database.password=
debezium.database.server.id=184054
debezium.topic.prefix=cdc
debezium.table.include.list=inventory.customers,inventory.orders
`

## Step 4: Start Kafka Connect
`ash
# Using Confluent platform
confluent local services connect start

# Or with Docker
docker run -d --name connect \
  -e CONNECT_BOOTSTRAP_SERVERS=localhost:9092 \
  -e CONNECT_REST_PORT=8083 \
  confluentinc/cp-kafka-connect:latest
`

## Step 5: Register Connector
`ash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @connector-config.json
`

## Step 6: Consume CDC Events
`ash
# Read from Kafka topic
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic cdc.inventory.customers \
  --from-beginning \
  --property print.key=true
`
"@

System.Collections.Hashtable["COMMON_MISTAKES.md"] = @"
# Common CDC Mistakes

## 1. No Schema History Topic
`java
// WRONG - in-memory schema history
// Connector loses schema on restart

// RIGHT - persistent schema history
.with("schema.history.internal.kafka.topic", "schemahistory.inventory")
.with("schema.history.internal.kafka.bootstrap.servers", "kafka:9092")
`

## 2. Binlog Retention Too Short
`sql
-- WRONG - binlog expires too fast
expire_logs_days = 1

-- RIGHT
expire_logs_days = 3
-- Or set hours for finer control
-- MySQL 8+: binlog_expire_logs_seconds = 259200
`

## 3. Not Handling Schema Changes
`java
// WRONG - schema evolution breaks pipeline
// RIGHT - handle schema changes
.with("schema.history.internal", "io.debezium.storage.kafka.KafkaSchemaHistory")
.with("database.history.skip.unparseable.ddl", "true")
`

## 4. Single Task for Large Tables
`java
// WRONG - one task can't keep up
"tasks.max": "1"

// RIGHT - more tasks for parallelism
"tasks.max": "4"
`
"@

System.Collections.Hashtable["DEBUGGING.md"] = @"
# Debugging CDC

## Common Issues

### Connector Failing to Start
`ash
# Check Connect logs
docker logs connect --tail 100

# Verify database connectivity
curl http://localhost:8083/connectors/inventory-connector/status

# Common: permissions missing, binlog not enabled
`

### Lag Increasing
`ash
# Check consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group connect-inventory-connector --describe

# Check if binlog is being consumed fast enough
# Increase tasks.max or tune batch size
`

### Schema Registry Errors
`java
// Check if schema is compatible
// Verify schema registry is accessible
// Try with JSON converter instead of Avro
`

### Offset Issues
`ash
# Check offset topic
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic connect-offsets --from-beginning

# Reset offset if needed (caution!)
curl -X DELETE http://localhost:8083/connectors/inventory-connector
# Then recreate
`
"@

System.Collections.Hashtable["REFACTORING.md"] = @"
# Refactoring CDC

## Before: Timestamp-Based Polling
`java
// Every 5 minutes, check for new records
SELECT * FROM orders WHERE updated_at > ?;
// Misses deletes, high latency, source load
`

## After: Log-Based CDC
`java
// Debezium captures all changes in real-time
// No source load, captures deletes, sub-second
DebeziumEngine.create(Json.class)
    .using(config)
    .notifying(this::process)
    .build();
`

## Before: Raw Table CDC
`java
// CDC on main tables - lots of noise
`

## After: Outbox Pattern
`java
// Applications write to outbox table
// Clean events with explicit intent
// Perfect for event-driven architectures
`
"@

System.Collections.Hashtable["PERFORMANCE.md"] = @"
# CDC Performance

## Tuning Debezium
`java
// Batch size and polling
props.setProperty("max.batch.size", "2048");
props.setProperty("max.queue.size", "8192");
props.setProperty("poll.interval.ms", "500");

// Snapshot tuning
props.setProperty("snapshot.fetch.size", "10000");
props.setProperty("snapshot.locking.mode", "none");

// Connection tuning
props.setProperty("database.server.id", "184054");
props.setProperty("connect.keep.alive", "true");
`

## Kafka Connect Tuning
`properties
# Worker config
worker.count=4
offset.flush.interval.ms=5000
offset.flush.timeout.ms=5000
task.shutdown.graceful.timeout.ms=5000

# Producer configs (for source connectors)
producer.acks=all
producer.linger.ms=50
producer.batch.size=65536
producer.compression.type=snappy
`

## Monitoring
`java
// Record CDC metrics
@Bean
public MeterRegistry meterRegistry() {
    return new PrometheusMeterRegistry(PrometheusConfig.DEFAULT);
}

// Metrics to track:
// - debezium.records.created
// - debezium.records.updated
// - debezium.records.deleted
// - debezium.lag.seconds
// - debezium.snapshot.rows.total
`
"@

System.Collections.Hashtable["SECURITY.md"] = @"
# CDC Security

## Database Credentials
`java
// NEVER hardcode credentials
props.setProperty("database.password", System.getenv("DEBEZIUM_DB_PASSWORD"));
// Use Vault for production
VaultTransitOperations vault = vaultTemplate.opsForTransit("cdc");
props.setProperty("database.password", vault.decrypt("encrypted-password"));
`

## Network Security
`properties
# Use SSL for database connection
database.ssl.mode=verify_full
database.ssl.keystore=/path/to/keystore
database.ssl.truststore=/path/to/truststore

# Kafka with SSL
database.history.kafka.bootstrap.servers=kafka:9093
database.history.kafka.ssl.keystore.location=/path/to/kafka-keystore
`

## Data Masking
`java
// Mask sensitive data in CDC events
.with("column.mask.with.2.chars.hash.salt", "inventory.customers:password")
.with("column.truncate.to.4.chars", "inventory.customers:ssn,credit_card")
.with("column.propagate.source.type", "inventory.orders:.*")
`

## Access Control
`ash
# Limit CDC user permissions
GRANT SELECT ON inventory.* TO 'debezium'@'%';
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%';
`
"@

System.Collections.Hashtable["ARCHITECTURE.md"] = @"
# CDC Architecture

## Production CDC Architecture
`
+------------------+     +------------------+
| MySQL Primary    |     | PostgreSQL       |
| (binlog)         |     | (WAL)            |
+--------+---------+     +--------+---------+
         |                        |
         v                        v
+------------------+     +------------------+
| Debezium MySQL   |     | Debezium PG      |
| Connector        |     | Connector        |
+--------+---------+     +--------+---------+
         |                        |
         v                        v
+------------------+     +------------------+
| Kafka Connect    |     | Kafka Connect    |
| (Source)         |     | (Source)         |
+--------+---------+     +--------+---------+
         |                        |
         +----------+-------------+
                    |
                    v
+-------------------------------------+
|          Kafka Cluster              |
| Topics: cdc.inventory.orders        |
|         cdc.inventory.customers     |
|         cdc.inventory.products      |
+------------------+------------------+
         |         |         |
         v         v         v
+--------+ +-------+ +-----+------+
| Flink   | | Data  | | S3 Sink   |
| Stream  | | Lake  | | (Parquet) |
+---------+ +-------+ +-----------+
`

## Spring Boot Integration
`java
@SpringBootApplication
@EnableDebeziumClient(connector = "mysql-connector")
public class CdcApplication {
    public static void main(String[] args) {
        SpringApplication.run(CdcApplication.class, args);
    }
}
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# CDC Exercises

## Exercise 1: Setup Debezium
Configure Debezium for a MySQL database and capture changes to a Kafka topic.

## Exercise 2: CDC Event Processing
Build a Kafka Streams application that processes CDC events (create, update, delete).

## Exercise 3: Snapshot + Stream
Implement an initial snapshot followed by continuous streaming.

## Exercise 4: Outbox Pattern
Design and implement the outbox pattern for application-level CDC.

## Exercise 5: Schema Evolution
Handle a schema change (new column added) in the CDC pipeline.
