# Change Data Capture (CDC)

## Overview
Change Data Capture is a pattern for tracking and capturing changes (inserts, updates, deletes) in databases and streaming them to downstream systems in real-time.

## Key Concepts
- **CDC**: Change Data Capture - monitoring and recording data changes
- **Debezium**: Open-source CDC platform built on Kafka Connect
- **Kafka Connect**: Framework for streaming data between Kafka and other systems
- **Streaming Ingestion**: Real-time data ingestion from sources
- **Schema Registry**: Manages Avro/Protobuf schemas for CDC events

## Java Example
`java
import io.debezium.config.Configuration;
import io.debezium.engine.ChangeEvent;
import io.debezium.engine.DebeziumEngine;
import io.debezium.engine.format.Json;

import java.util.Properties;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class CdcConsumer {
    public static void main(String[] args) {
        Configuration config = Configuration.create()
            .with("connector.class", "io.debezium.connector.mysql.MySqlConnector")
            .with("database.hostname", "localhost")
            .with("database.port", 3306)
            .with("database.user", "debezium")
            .with("database.password", "dbz")
            .with("database.server.id", "184054")
            .with("database.server.name", "my-app-connector")
            .with("database.include.list", "inventory")
            .with("table.include.list", "inventory.customers,inventory.orders")
            .with("database.history.kafka.bootstrap.servers", "localhost:9092")
            .with("database.history.kafka.topic", "schema-changes.inventory")
            .with("key.converter.schemas.enable", "false")
            .with("value.converter.schemas.enable", "false")
            .build();

        try (DebeziumEngine<ChangeEvent<String, String>> engine = DebeziumEngine.create(Json.class)
                .using(config.asProperties())
                .notifying(record -> {
                    System.out.printf("Key: %s, Value: %s%n", record.key(), record.value());
                })
                .build()) {

            ExecutorService executor = Executors.newSingleThreadExecutor();
            executor.execute(engine);
            Thread.sleep(Long.MAX_VALUE);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
`
"@

System.Collections.Hashtable["THEORY.md"] = @"
# Change Data Capture Theory

## CDC Mechanisms
- **Log-based**: Read database transaction log (binlog, WAL)
  - Minimal impact on source database
  - Captures all changes (insert, update, delete)
  - No schema changes needed
  - Examples: Debezium (MySQL binlog, PostgreSQL WAL)

- **Trigger-based**: Database triggers capture changes
  - Works with any database
  - Performance impact on source
  - Requires trigger management

- **Query-based**: Timestamp/version column queries
  - Simple to implement
  - Only captures inserts/updates (not deletes)
  - Higher latency than log-based

## Debezium Architecture
`
Source DB (MySQL binlog)
  |
  v
Debezium Connector (Kafka Connect)
  |
  v
Kafka Topic (CDC events)
  |     |     |
  v     v     v
Stream Processing | Data Lake | Warehouse
`

## Change Event Structure
`json
{
  "op": "c/u/d/r",  // create, update, delete, read (snapshot)
  "before": { ... }, // previous state (for updates/deletes)
  "after": { ... },  // current state (for creates/updates)
  "source": {
    "db": "inventory",
    "table": "customers",
    "ts_ms": 1234567890,
    "snapshot": true  // true during initial snapshot
  }
}
`
"@

System.Collections.Hashtable["WHY_IT_EXISTS.md"] = @"
# Why CDC Exists

## The Problem
Traditional batch ETL has high latency (hours/days). Polling-based approaches (timestamp queries) can't capture deletes and put load on source databases.

## Root Cause
- Need for real-time data replication with minimal source impact
- Must capture all change types (insert, update, delete)
- Source databases can't be modified (no triggers allowed)
- Zero downtime migrations require continuous sync

## CDC Solution
- Log-based CDC reads recovery logs (no source impact)
- Captures all DML operations
- Sub-second latency
- Schema evolution tracking
- Consistent snapshot + streaming

## Use Cases
- Real-time analytics on transactional data
- Cache invalidation
- Search index updates
- Data replication for migrations
- Audit logging
- CQRS patterns
