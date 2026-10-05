# Change Data Capture — REAL WORLD PROJECT

## Context

A B2B SaaS company is replacing a nightly full-table replication between its
primary Postgres and a reporting warehouse with CDC. The stakes are an audit
trail: customer billing events must be reconstructable to any point in time.
The current nightly job misses intraday changes, loses deletes entirely, and
takes 6 hours. You own the CDC platform.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Source | 1 Postgres primary (c6g.16xl), 4.2TB, 310 tables |
| Change rate | ~14k transactions/sec peak, 90M rows changed/day |
| Snapshot | 4.2TB must be initial-loaded without stopping writes |
| Replica | read replica also needs replication (no double-snapshot) |
| SLO | lag < 30s p99; RPO 0 for billing events |
| Retention | change log retained 400 days for audit |
| Constraint | cannot take a maintenance window on the primary |

## Architecture

```
Postgres primary
  |-- wal_level=logical, REPLICA IDENTITY FULL on billing tables
  |-- logical replication slots: one per consumer domain (not per connector!)
  |
Debezium/kafka-connect (3 connector workers, HA)
  |-- snapshot.mode=initial (consistent, non-blocking, chunked)
  |
Kafka cdc.v1.<schema>.<table>
  |-- partition key = primary key  => per-key order
  |-- schemas: Avro + schema registry, BACKWARD compatible enforced
  |-- retention 7d on the stream; 400d on a compacted audit topic
  |
consumers
  |-- warehouse sink: upsert into Iceberg/Delta, exactly-once
  |-- search sink: partial-row upsert
  |-- audit sink: append-only, 400d, immutable object store
  |-- cache invalidation: keys only, ~40k events/sec
```

## Key Implementation — the decisions that determined reliability

**1. Replication slots are a capacity risk, and the failure is silent until it
is catastrophic.** An inactive slot pins WAL. If the connector stops, Postgres
keeps the WAL to satisfy the slot, and the disk fills — taking down the primary.

```java
public final class SlotGuard {
    /**
     * Alert on WAL retention, not just connector liveness.
     *   lag_bytes = (pg_current_wal_lsn - slot.confirmed_flush_lsn) * wal_segment_size
     * Action thresholds scale with disk headroom, not with a fixed constant.
     */
    public record SlotHealth(String slot, long retainedBytes, long diskFreeBytes) {
        boolean critical() { return retainedBytes > diskFreeBytes * 0.20; }
        boolean warn()     { return retainedBytes > diskFreeBytes * 0.05; }
    }
}
```

`max_slot_wal_keep_size` bounds it, but note the consequence honestly: when a
slot is invalidated by hitting that limit, the connector must re-snapshot. That
is an outage, not a hiccup, so the guard's job is to prevent it.

**2. One slot per domain, not per connector, and a documented mapping.** Slot
creation is manual and destructive: dropping a slot can require a full
resnapshot. Slots are therefore a catalog, not a side effect of deployment.

```java
public enum ConsumerDomain { WAREHOUSE, SEARCH, AUDIT, CACHE_INVALIDATION }

public record SlotPolicy(ConsumerDomain domain, String slotName, List<String> tables,
                         long maxSlotWalKeepMb) {
    // WAREHOUSE takes all 310 tables; SEARCH takes 12; AUDIT takes the 9 billing tables;
    // CACHE_INVALIDATION needs keys only, so REPLICA IDENTITY DEFAULT suffices.
    static final Map<ConsumerDomain, SlotPolicy> CATALOG = Map.of(
        WAREHOUSE,          new SlotPolicy(WAREHOUSE, "slot_warehouse", ALL_TABLES, 20_000),
        SEARCH,             new SlotPolicy(SEARCH, "slot_search", SEARCH_TABLES, 2_000),
        AUDIT,              new SlotPolicy(AUDIT, "slot_audit", BILLING_TABLES, 4_000),
        CACHE_INVALIDATION, new SlotPolicy(CACHE_INVALIDATION, "slot_cache", CACHE_TABLES, 500)
    );
}
```

**3. Deletes and updates are the actual requirement.** Full-row before-images
(`REPLICA IDENTITY FULL`) are what make the audit log complete — and they are
also the reason for the storage cost. On 310 tables it is a deliberate,
documented trade.

```java
public final class AuditSink {
    /** Append-only. Never updated, never deleted by retention until 400d. */
    public void write(CdcEvent<?> e) {
        append("billing_audit_change_log",
                Map.of("lsn", e.lsn(), "tx_id", e.txId(), "table", e.table(),
                        "op", e.op().name(), "before", json(e.before()),
                        "after", json(e.after()), "commit_ts", e.commitTs()));
    }

    /** Reconstruct the state of a record at any instant in time. */
    public Optional<Map<String,Object>> stateAt(String table, long pk, Instant at) {
        // fold the log forward from the last snapshot at-or-before `at`
        return auditLog(table, pk)
                .filter(r -> r.commitTs() <= at.toEpochMilli())
                .reduce((a, b) -> b.op() == Op.DELETE ? null : b.after());
    }
}
```

**4. Snapshot without downtime.** Chunked, throttled, and resumable.

```java
public final class ChunkedSnapshotter {
    /**
     * Chunk by primary-key range, not by OFFSET: OFFSET skips and duplicates rows
     * while the table is being written to. Range chunking with a last-persisted
     * upper bound is resumable and does not need a long-lived transaction.
     */
    public void snapshot(String table, long chunkSize, Throttle throttle) {
        long lower = progress.get(table);
        while (true) {
            List<Row> chunk = selectRange(table, lower, lower + chunkSize);
            if (chunk.isEmpty()) break;
            emit(chunk, Op.READ);
            lower += chunkSize;
            progress.put(table, lower);       // persist per chunk: restart resumes here
            throttle.acquire();               // protect the primary: this is a 4.2TB read
        }
    }
}
```

Snapshot bandwidth is the operational risk: a 4.2TB chunked read against a live
primary will contend with production traffic. Sizing it to ~8% of the
instance's I/O budget, with a throttle, took the snapshot from "primary
CPU pinned for 6 hours" to "a day and a half of background load".

## Failure Modes and the Runbook

1. **Replication slot retains unbounded WAL.** Symptom: disk fills, primary
   crashes, and a full outage. Fix: `max_slot_wal_keep_size` plus the
   SlotGuard alerting on retained bytes vs free disk. Never drop a slot to
   "fix" lag without accepting a resnapshot.
2. **Connector lost its offset and re-snapshots 4TB.** Symptom: a `Snapshot` event
   storm on the topic. Fix: monitor for `Op.READ` volume on a running connector;
   treat any snapshot after initial load as an incident.
3. **Schema change breaks consumers.** Symptom: deserialization errors, then a
   backlog. Fix: compatibility enforced in the registry at PR time; a `DROP
   COLUMN` is a two-phase change (stop writing, deploy readers, then drop).
4. **Long transaction blocks the slot.** Symptom: lag climbs while throughput
   looks normal — the connector is waiting for the oldest open transaction.
   Fix: alert on `pg_stat_activity` oldest `xact_start`; fix the offending
   application transaction, not the connector.
5. **Out-of-order application.** Symptom: final state does not match the source,
   a few rows per thousand. Fix: partition by primary key; verify no consumer
   uses a different key function; add an LSN monotonicity assertion.
6. **Replica slot conflicts with a base backup.** Symptom: backup window fails.
   Fix: schedule around replication slot creation, and use a separate physical
   backup mechanism from logical slot management.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Change data capture reads a database's change log (binlog / WAL) to stream
  inserts, updates, and deletes; CDC tools typically combine a consistent
  snapshot with the ongoing stream to avoid missing or duplicating changes.
  - Reference: https://debezium.io/documentation/reference/stable/architecture.html
  - Reference: https://www.postgresql.org/docs/current/logicaldecoding.html
- Kafka preserves order within a partition, so keying a CDC topic by primary key
  gives per-record ordering; consumer groups and committed offsets define
  resumable delivery.
  - Reference: https://kafka.apache.org/documentation/#intro_concepts_and_terms
  - Reference: https://kafka.apache.org/documentation/#design
- Iceberg and Delta Lake support schema evolution and snapshot isolation over
  object storage, which is what lets a CDC sink upsert into a table format
  without mutating existing data files.
  - Reference: https://iceberg.apache.org/docs/latest/evolution/
  - Reference: https://docs.delta.io/latest/delta-batch.html

## Deliverables
- [ ] Slot catalog with per-domain policies and `max_slot_wal_keep_size`
- [ ] SlotGuard alerting on retained WAL vs free disk
- [ ] Chunked resumable snapshot with an I/O budget and throttle
- [ ] Exactly-once warehouse sink plus an append-only 400-day audit log
- [ ] `stateAt(table, pk, instant)` reconstruction, proven against a replay
- [ ] Lag SLO dashboard and the runbook for all six failure modes
- [ ] Load impact measurement of snapshot + streaming on the primary
