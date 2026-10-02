# CDC Theory

## CDC Mechanisms
- **Log-based**: Read DB transaction log (binlog, WAL) - minimal impact
- **Trigger-based**: DB triggers - performance impact
- **Query-based**: Timestamp columns - simple, no deletes

## Debezium Architecture
```
[Source DB] -> [Debezium Connector] -> [Kafka Topic] -> [Stream/Store]
```

## Change Event Structure
```json
{op: "c/u/d/r", before: {...}, after: {...}, source: {db, table, ts_ms}}
```

## Sourced field notes (fetched Oct 2026 — verify before citing)
- "Debezium connector for PostgreSQL" (Debezium 3.7 reference docs — accessed Oct 2026) — https://debezium.io/documentation/reference/stable/connectors/postgresql.html — Takeaway tied to lab log-based CDC exercise: configure logical decoding with `plugin.name=pgoutput` (built-in, no extra library) vs `decoderbufs`, create the replication slot/user with replication privilege, and confirm WAL streaming via the replication protocol before expecting events.
- "Debezium connector for PostgreSQL" (Debezium 3.7 reference docs — accessed Oct 2026) — https://debezium.io/documentation/reference/stable/connectors/postgresql.html — Takeaway tied to lab snapshot config: pick `snapshot.mode` (`initial` default, `initial_only`, `never`/`no_data`, `when_needed`, `always`) to match the lab's initial-load scenario; the connector snapshots then streams from the recorded LSN so no committed change is skipped.
- "Debezium connector for PostgreSQL" (Debezium 3.7 reference docs — accessed Oct 2026) — https://debezium.io/documentation/reference/stable/connectors/postgresql.html — Takeaway tied to lab event-structure exercise: validate `op` = create/update/delete/read plus `before`/`after`/`source` against the connector's change-event key/value spec, and check `REPLICA IDENTITY` when `before` is null on updates/deletes.
- "Debezium connector for PostgreSQL" (Debezium 3.7 reference docs — accessed Oct 2026) — https://debezium.io/documentation/reference/stable/connectors/postgresql.html — Takeaway tied to lab failure/recovery config: the connector checkpoints WAL position per event and resumes from the last offset after crash/rebalance, but monitor WAL disk retention and replication-slot lag so the slot isn't dropped while the connector is stopped.
