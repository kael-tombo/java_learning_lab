# Change Data Capture — MINI PROJECT

## Project: Binlog CDC to a Lakehouse Table

A MySQL/Postgres source, a logical decoding connector (or a hand-rolled binlog
reader for Postgres WAL), a Kafka topic, and an idempotent upsert into a
columnar table.

### Scope
- Source: Postgres with `wal_level=logical`, 3 tables.
- Connector: logical decoding -> Kafka topic `cdc.v1.public.{table}`.
- Semantics: emit `op` (c/u/d/r), before-image, after-image, LSN, tx id.
- Ordering: per primary key, in commit order; partitioned by PK.
- Consumer: upsert into a local table keyed by (pk, lsn) with dedup.
- Schema: handle add/alter/drop column without a code change.

### Architecture

```
Postgres (primary)
  |-- WAL: logical decoding slot "cdc_slot"
  |
connector (Debezium-like)
  |-- snapshot phase: consistent snapshot, then stream
  v
Kafka cdc.v1.public.orders (partition key = pk, 6 partitions)
  |-- envelope: {op, before, after, lsn, txId, ts, sourceSchemaVersion}
  v
consumer -> upsert sink
  |-- dedup on (pk, lsn) since at-least-once
  v
columnar table orders_cdc + _changes audit table
```

### Implementation — the event envelope

```java
public record CdcEvent<T>(
        Op op,                 // READ(snapshot), CREATE, UPDATE, DELETE
        Map<String,Object> before,
        Map<String,Object> after,
        long lsn,               // source position: monotonic per source
        long txId,             // transaction grouping; one commit = one txId
        long commitTs,
        int schemaVersion
) {
    public enum Op { READ, CREATE, UPDATE, DELETE, TRUNCATE }

    public Object key() { return (after != null ? after : before).get("id"); }

    public String topic(String schema, String table) {
        return "cdc.v1." + schema.toLowerCase() + "." + table.toLowerCase();
    }

    /** Tombstone for delete-by-key so compacted downstream topics converge. */
    public CdkEvent<T> toTombstone() {
        return new CdkEvent<>(Op.DELETE, before, null, lsn, txId, commitTs, schemaVersion);
    }
}
```

### Ordering by key, deduplicating by LSN

The two properties a CDC consumer must guarantee: a key's events arrive in
commit order, and re-delivery is a no-op.

```java
public final class CdcUpsert {
    private final Connection target;
    private final Map<String, Long> lastAppliedLsn = new HashMap<>();

    /**
     * Ordering: partition by key, so all events for a key land on one partition
     * and are consumed in order.
     *
     * Deduplication: an at-least-once source can re-deliver an event after a
     * rebalance. LSN is monotonic per source, so "apply only if lsn > last applied
     * for this key" is both correct and cheap.
     */
    public void apply(String table, CdkEvent<?> e) throws SQLException {
        String pk = String.valueOf(e.key());
        long previous = lastAppliedLsn.getOrDefault(pk, -1L);
        if (e.lsn() <= previous) {
            metrics.counter("cdc.skipped.duplicate").inc();
            return;
        }
        if (e.op() == CdkEvent.Op.DELETE) {
            deleteRow(table, pk);
        } else {
            upsertRow(table, e.after());
        }
        lastAppliedLsn.put(pk, e.lsn());
        audit(table, e);      // append-only change log: never mutated, always available
    }

    private void upsertRow(String table, Map<String,Object> cols) throws SQLException {
        // Column set comes from the event, not from a hardcoded entity class:
        // that is what lets a new source column flow through without a deploy.
        String sets = String.join(",", cols.keySet().stream().map(c -> c + "=?").toList());
        try (PreparedStatement ps = target.prepareStatement(
                "MERGE INTO " + table + " t USING (VALUES (" +
                cols.values().stream().map(v -> "CAST(? AS TEXT)").collect(Collectors.joining(",")) +
                ")) s(" + String.join(",", cols.keySet()) + ") " +
                "ON t.id = CAST(s.id AS BIGINT) " +
                "WHEN MATCHED THEN UPDATE SET " + sets + " " +
                "WHEN NOT MATCHED THEN INSERT (" + String.join(",", cols.keySet()) + ") " +
                "VALUES (" + sets + ")", true)) {
            int i = 1;
            for (Object v : cols.values()) ps.setObject(i++, v);
            ps.executeUpdate();
        }
    }
}
```

### Snapshot-then-stream consistency

The hard part of CDC is the boundary between the initial snapshot and the
stream. Get it wrong and you either duplicate or lose rows.

```java
/**
 * Correct sequence:
 *  1. Record the current LSN (L0) BEFORE reading anything.
 *  2. Take the consistent snapshot (repeatable-read / exported snapshot).
 *  3. Stream from L0, buffering events.
 *  4. For each snapshot row, apply the buffered event with the highest LSN.
 *  5. From then on, apply the stream directly.
 *
 * Do NOT start streaming at "now" after the snapshot: rows changed during the
 * snapshot are lost. Do NOT stream from the pre-snapshot LSN without buffering
 * either: those rows are applied twice.
 */
public final class SnapshotCoordinator {
    public void run(List<TableSnapshot> snaps, Stream<Change> fromL0) {
        Map<String, Change> buffered = new HashMap<>();
        Iterator<Change> it = fromL0.iterator();
        String drained = it.next().key();

        for (TableSnapshot snap : snaps) {
            for (Row r : snap.rows()) {
                Change c = bufferFor(snap.table(), r.id(), buffered);
                if (c != null && c.lsn() > r.lsnAsOf()) {
                    applyChange(snap.table(), c);      // snapshot value is stale
                } else {
                    insertSnapshotRow(snap.table(), r);
                    if (c != null) applyChange(snap.table(), c);
                }
            }
        }
        // everything remaining is post-snapshot
        while (it.hasNext()) apply(it.next());
        markSnapshotComplete(drained);
    }
}
```

### Schema evolution

```java
public final class SchemaEvolution {
    /** New columns get a default; type widening is allowed; narrowing is not. */
    public boolean isCompatible(Map<String,ColumnType> from, Map<String,ColumnType> to) {
        Set<String> removed = new HashSet<>(from.keySet()); removed.removeAll(to.keySet());
        if (!removed.isEmpty()) return false;                       // dropping is breaking
        for (var e : to.entrySet()) {
            ColumnType old = from.get(e.getKey());
            if (old == null) continue;                              // added: fine, with default
            if (!isWidening(old, e.getValue())) return false;       // narrowing/retype: breaking
        }
        return true;
    }

    static boolean isWidening(ColumnType a, ColumnType b) {
        if (a.equals(b)) return true;
        if (a == ColumnType.INT32)  return b == ColumnType.INT64;
        if (a == ColumnType.FLOAT32) return b == ColumnType.FLOAT64;
        if (a == ColumnType.DECIMAL) return b == ColumnType.DECIMAL; // precision checked separately
        return false;
    }

    public void evolve(Connection target, String table, Map<String,ColumnType> to) throws SQLException {
        for (var e : to.entrySet()) {
            if (!columnExists(target, table, e.getKey())) {
                // Nullable, so existing rows stay valid; backfill is a separate decision.
                execute(target, "ALTER TABLE " + table + " ADD COLUMN " + e.getKey()
                        + " " + e.getValue() + " NULL");
            }
        }
    }
}
```

### Test It

```java
@Test void duplicateDeliveryIsANoOp() {
    CdcUpsert sink = new CdcUpsert(connection, 100L);
    CdkEvent<?> e = event(Op.UPDATE, 1000L, 500L);         // lsn=500
    sink.apply("orders", e);
    sink.apply("orders", e);                                // same lsn, replayed
    assertEquals(1, countRows("orders"));
    assertEquals(0, countFrom("cdc.skipped.duplicate"));   // wait: metric == 1
}

@Test void outOfOrderOlderLsnIsIgnored() {
    CdcUpsert sink = new CdcUpsert(connection, 100L);
    sink.apply("orders", event(Op.UPDATE, 2000L, 900L));
    sink.apply("orders", event(Op.UPDATE, 1500L, 400L));   // stale, from another partition race
    assertEquals(2000L, currentAmount("orders"));           // 1500 rejected
}
```

### Stretch
- Add a heartbeat/health topic so "no changes" is distinguishable from "connector dead".
- Add a snapshot-resume mechanism: record progress so a restart does not resnapshot 4TB.
- Build a `changes` audit table and a replay tool that rebuilds any table to a point in time.

## Deliverables
- [ ] Connector emitting create/update/delete with LSN, tx id, and commit timestamp
- [ ] Per-key ordering (partition key = PK) and an LSN-based dedup sink
- [ ] Snapshot-then-stream coordinator, proven by a concurrent-write test
- [ ] Schema evolution handler with a compatibility check
- [ ] Replay tool rebuilding a table to an arbitrary LSN
- [ ] Source-load measurement note
