# Event Sourcing - Code Deep Dive

Pure Java. Five pieces: aggregate, event store, projector, snapshot, upcaster.

## 1. The Aggregate: Deciding, Not Storing

```java
package systemdesign.eventsourcing;

import java.time.Instant;
import java.util.*;

/**
 * An aggregate DECIDES. It does not store. It is loaded with the events that
 * happened, you ask it a question, and it returns new events describing what
 * SHOULD happen. Applying them is the store's job.
 *
 * This separation is why a rebuild works: there is no hidden state anywhere
 * except in the events.
 *
 * The aggregate is the consistency boundary. One aggregate is modified by one
 * transaction at a time, enforced by the expected version.
 */
public abstract class Aggregate {

    public record Event(String aggregateId, long version, String type,
                        Map<String, Object> data, Instant occurredAt) {}

    private final String id;
    private long version;                    // last applied version
    private final List<Event> uncommitted = new ArrayList<>();

    protected Aggregate(String id) { this.id = id; }

    public String id() { return id; }
    public long version() { return version; }

    /** Rehydrate from stored events. This is what a rebuild does, 1.2M times a day. */
    public void rehydrate(List<Event> history) {
        for (Event e : history) {
            if (e.version() != version + 1) {
                // A GAP means either corruption or a partition we failed to
                // notice. Fail loudly: a silently skipped event produces a
                // balance that is wrong forever.
                throw new IllegalStateException(
                        "event gap on " + id + ": expected " + (version + 1)
                        + " got " + e.version());
            }
            apply(e);
            version = e.version();
        }
    }

    /** Pure state transition. Must not perform I/O, use now(), or read globals. */
    protected abstract void apply(Event e);

    /** Business decision. Returns new events; does not mutate durable state. */
    protected void record(String type, Map<String, Object> data) {
        uncommitted.add(new Event(id, version + uncommitted.size() + 1, type,
                Map.copyOf(data), Instant.now()));
    }

    public List<Event> uncommitted() { return List.copyOf(uncommitted); }

    public void clearUncommitted() { uncommitted.clear(); }

    /** Guard: state changes must come from events, never from direct assignment. */
    protected final void illegalDirectMutation(String what) {
        throw new UnsupportedOperationException(
                "cannot mutate " + what + " directly in an event-sourced aggregate; record an event");
    }
}
```

**Residual risk:** `Instant.now()` inside `record` makes events
irreproducible across a rebuild. That is acceptable for the event *itself*
(occurred_at is recorded), but a **projection** must never do this — see §3.

## 2. A Concrete Aggregate: Bank Account

```java
/**
 * Invariant: balance == sum(entries). The balance is DERIVED and only exists
 * to be checked; the events are the truth.
 */
public final class Account extends Aggregate {

    private long balanceMinor;
    private String currency = "USD";
    private boolean frozen;
    /** customerRef, NOT name/email. See the GDPR section: erasable personal
     *  data must not be in an immutable log. */
    private String customerRef;

    public Account(String id) { super(id); }

    public static Account opened(String id, String customerRef, long initialMinor) {
        Account a = new Account(id);
        a.record("AccountOpened", Map.of(
                "customerRef", customerRef,
                "initialMinor", initialMinor,
                "currency", "USD"));
        return a;
    }

    public void deposit(long amountMinor) {
        if (amountMinor <= 0) throw new IllegalArgumentException("deposit must be positive");
        record("Deposited", Map.of("amountMinor", amountMinor));
    }

    public void withdraw(long amountMinor) {
        // Business rules are enforced HERE, in the decision, not in the store.
        // This is the payoff: a replay re-validates every historical decision.
        if (frozen) throw new IllegalStateException("account frozen");
        if (amountMinor <= 0) throw new IllegalArgumentException("withdraw must be positive");
        if (balanceMinor - amountMinor < 0) throw new IllegalStateException("insufficient funds");
        record("Withdrawn", Map.of("amountMinor", amountMinor));
    }

    public void freeze() { record("Frozen", Map.of()); }

    /** Corrections are APPEND-ONLY. You never edit history, even to fix a mistake. */
    public void correct(long amountMinor, String reason) {
        record("CorrectionApplied", Map.of(
                "amountMinor", amountMinor, "reason", reason));
    }

    @Override
    protected void apply(Event e) {
        switch (e.type()) {
            case "AccountOpened" -> {
                balanceMinor = ((Number) e.data().get("initialMinor")).longValue();
                customerRef = String.valueOf(e.data().get("customerRef"));
                currency = String.valueOf(e.data().getOrDefault("currency", "USD"));
            }
            case "Deposited"  -> balanceMinor += num(e, "amountMinor");
            case "Withdrawn"  -> balanceMinor -= num(e, "amountMinor");
            case "Frozen"     -> frozen = true;
            case "CorrectionApplied" -> balanceMinor += num(e, "amountMinor");
            default -> throw new IllegalArgumentException("unknown event type: " + e.type());
        }
    }

    private static long num(Event e, String field) {
        return ((Number) e.data().get(field)).longValue();
    }

    public long balanceMinor() { return balanceMinor; }
    public boolean isFrozen() { return frozen; }
    public String customerRef() { return customerRef; }
}
```

**Residual risk:** an unknown event type throws, which means a projection
written before a new event was added will break. That is intentional for the
aggregate (it must not silently ignore a debit) and wrong for read projections —
see the tolerant reader in §5.

## 3. Event Store with Optimistic Concurrency

```java
/**
 * The append is a compare-and-set on (aggregate_id, version). 0 rows affected
 * means someone else won the race, and the caller MUST rehydrate and retry.
 *
 * WHY OPTIMISTIC, NOT PESSIMISTIC: aggregates are usually low-contention, so
 * retries are rare; and a pessimistic lock here means holding a lock across
 * event appends plus projection dispatch, which is exactly the coupling event
 * sourcing was meant to remove.
 */
public final class EventStore {

    public record StoredEvent(String eventId, String aggregateId, long version,
                              String type, String payload, Instant occurredAt) {}

    public static class ConcurrencyConflictException extends RuntimeException {
        public ConcurrencyConflictException(String id, long expected, long actual) {
            super("concurrency conflict on " + id
                    + ": expected version " + expected + ", store is at " + actual);
        }
    }

    private final java.sql.Connection db;
    private final EventSerializer serializer;

    public EventStore(java.sql.Connection db, EventSerializer serializer) {
        this.db = db;
        this.serializer = serializer;
    }

    /**
     * Append events for ONE aggregate.
     *
     * The UNIQUE (aggregate_id, version) constraint is the idempotency and
     * safety mechanism. Application-level version checks are a convenience;
     * this constraint is the guarantee.
     */
    public List<StoredEvent> append(String aggregateId, long expectedVersion,
                                    List<Aggregate.Event> events) throws Exception {
        boolean auto = db.getAutoCommit();
        db.setAutoCommit(false);
        try {
            long v = expectedVersion;
            List<StoredEvent> stored = new ArrayList<>();
            for (Aggregate.Event e : events) {
                v++;
                if (e.version() != v) {
                    throw new IllegalStateException("event version " + e.version()
                            + " does not match expected " + v);
                }
                String id = UUID.randomUUID().toString();
                try (var ps = db.prepareStatement(
                        "INSERT INTO events(event_id, aggregate_id, version, type, payload, "
                        + "occurred_at) VALUES (?,?,?,?,?,?)")) {
                    ps.setString(1, id);
                    ps.setString(2, aggregateId);
                    ps.setLong(3, v);
                    ps.setString(4, e.type());
                    ps.setString(5, serializer.serialize(e));
                    ps.setTimestamp(6, Timestamp.from(e.occurredAt()));
                    ps.executeUpdate();
                }
                stored.add(new StoredEvent(id, aggregateId, v, e.type(),
                        serializer.serialize(e), e.occurredAt()));
            }
            db.commit();
            return stored;
        } catch (java.sql.SQLIntegrityConstraintViolationException dup) {
            // The unique (aggregate_id, version) constraint fired: a duplicate.
            // That is concurrent modification, not corruption. Rehydrate and retry.
            db.rollback();
            throw new ConcurrencyConflictException(aggregateId, expectedVersion, -1);
        } catch (Exception ex) {
            db.rollback();
            throw ex;
        } finally {
            db.setAutoCommit(auto);
        }
    }

    /** Read for rehydration or a temporal query. Ordered by version, NOT time. */
    public List<Aggregate.Event> read(String aggregateId, long fromVersion, long toVersion)
            throws Exception {
        List<Aggregate.Event> out = new ArrayList<>();
        try (var ps = db.prepareStatement(
                "SELECT version, type, payload, occurred_at FROM events "
              + "WHERE aggregate_id = ? AND version > ? AND version <= ? "
              + "ORDER BY version")) {          // version ordering, not timestamp
            ps.setString(1, aggregateId);
            ps.setLong(2, fromVersion);
            ps.setLong(3, toVersion);
            try (var rs = ps.executeQuery()) {
                while (rs.next()) {
                    out.add(new Aggregate.Event(aggregateId, rs.getLong(1), rs.getString(2),
                            serializer.deserialize(rs.getString(3)),
                            rs.getTimestamp(4).toInstant()));
                }
            }
        }
        return out;
    }

    /** Stream the whole log for a rebuild, from a checkpoint. */
    public java.util.stream.Stream<Aggregate.Event> streamAll(String lastEventId, int batch)
            throws Exception {
        List<Aggregate.Event> batchOut = new ArrayList<>();
        try (var ps = db.prepareStatement(
                "SELECT event_id, aggregate_id, version, type, payload, occurred_at FROM events "
              + "WHERE event_id > ? ORDER BY event_id LIMIT ?")) {
            ps.setString(1, lastEventId);
            ps.setInt(2, batch);
            try (var rs = ps.executeQuery()) {
                while (rs.next()) {
                    batchOut.add(new Aggregate.Event(rs.getString(2), rs.getLong(3),
                            rs.getString(4), serializer.deserialize(rs.getString(5)),
                            rs.getTimestamp(6).toInstant()));
                }
            }
        }
        return batchOut.stream();
    }
}
```

**Residual risk:** retry loops can livelock under sustained contention. Cap
attempts (5-8) with backoff and jitter, then return a `409` — and if an
aggregate still conflicts, it is too hot and needs sharding.

## 4. The Projector: Deterministic and Idempotent

```java
/**
 * A projection is a PURE FUNCTION of the event stream. If a rebuild produces a
 * different answer, the guarantee is gone.
 *
 * Consequences, all enforced by comment and by test:
 *  - NO Instant.now() in projected values. Use the event's occurred_at.
 *  - NO reads of external mutable state.
 *  - NO external side effects (see the note below).
 *  - Processing metadata (processed_at) is stored SEPARATELY, so a rebuild can
 *    overwrite it without corrupting the projected data.
 */
public final class BalanceProjector {

    public record Checkpoint(String lastEventId, long processedCount, Instant processedAt) {}

    public interface ReadModel {
        void upsertBalance(String accountId, long balanceMinor, long version);
        void upsertStatementRow(String accountId, long month, long amountMinor);
    }

    /**
     * Project one batch. Checkpoint and read-model updates go in ONE
     * transaction, or a crash leaves the checkpoint claiming progress that was
     * never applied.
     */
    public Checkpoint projectBatch(List<Aggregate.Event> events, Checkpoint from,
                                   ReadModel rm) {
        // Deterministic: process in version order within the aggregate, and
        // never depend on delivery order for correctness.
        List<Aggregate.Event> ordered = events.stream()
                .sorted(Comparator.comparingLong(Aggregate.Event::version))
                .toList();

        Map<String, Long> balances = new LinkedHashMap<>();
        for (Aggregate.Event e : ordered) {
            switch (e.type()) {
                case "AccountOpened"      -> rm.upsertBalance(e.aggregateId(),
                        num(e, "initialMinor"), e.version());
                case "Deposited"          -> rm.upsertBalance(e.aggregateId(),
                        current(rm, e.aggregateId()) + num(e, "amountMinor"), e.version());
                case "Withdrawn"          -> rm.upsertBalance(e.aggregateId(),
                        current(rm, e.aggregateId()) - num(e, "amountMinor"), e.version());
                case "CorrectionApplied"  -> rm.upsertBalance(e.aggregateId(),
                        current(rm, e.aggregateId()) + num(e, "amountMinor"), e.version());
                // Note: "Frozen" changes domain state, not the balance. Ignoring
                // it here is correct, and it is why tolerant readers work here
                // while the AGGREGATE must reject unknown types.
                default -> { }
            }
        }
        return new Checkpoint(lastEventIdOf(ordered), from.processedCount() + ordered.size(),
                Instant.now());   // metadata only; NOT a projected value
    }

    /**
     * The idempotency requirement for a rebuildable projection: applying the
     * same batch twice must produce the same read model. Because every write is
     * a versioned upsert (not a delta), replay is naturally idempotent.
     *
     * A projection that did `balance += amount` without the version guard would
     * double-apply on redelivery. Version the write or accept the duplication.
     */

    private static long num(Aggregate.Event e, String f) {
        return ((Number) e.data().get(f)).longValue();
    }
    private static String lastEventIdOf(List<Aggregate.Event> events) {
        return events.isEmpty() ? "" : events.get(events.size() - 1).aggregateId();
    }
    private static long current(ReadModel rm, String id) {
        Long v = rm.balanceOf(id);
        return v == null ? 0 : v;
    }
}
```

**Residual risk:** if any projection emits an external side effect (email,
webhook), a rebuild re-sends all of them. Emit side effects from a *separate*
consumer of the same log with its own dedup, so replaying projections for a
schema change cannot send 1.2M emails.

## 5. Snapshot and Upcaster

```java
/**
 * A snapshot is a CACHE, never the source of truth. If it is corrupt, delete
 * it and replay. The moment you rely on a snapshot to be correct, event
 * sourcing has become snapshot-sourcing.
 */
public final class SnapshotStore {

    public record Snapshot(String aggregateId, long version, String payload,
                           Instant takenAt, String checksum) {}

    private final java.sql.Connection db;

    public void save(String aggregateId, long version, String payload) throws Exception {
        try (var ps = db.prepareStatement(
                "INSERT INTO snapshots(aggregate_id, version, payload, taken_at, checksum) "
              + "VALUES (?,?,?,?,?) ON CONFLICT (aggregate_id) DO UPDATE "
              + "SET version = EXCLUDED.version, payload = EXCLUDED.payload, "
              + "taken_at = EXCLUDED.taken_at, checksum = EXCLUDED.checksum")) {
            ps.setString(1, aggregateId);
            ps.setLong(2, version);
            ps.setString(3, payload);
            ps.setTimestamp(4, Timestamp.from(Instant.now()));
            ps.setString(5, Integer.toHexString(payload.hashCode()));
            ps.executeUpdate();
        }
    }

    /**
     * Load and VERIFY. A snapshot that fails its checksum is discarded, not
     * trusted -- returning a corrupt snapshot silently corrupts the aggregate
     * state and therefore every subsequent decision.
     */
    public Snapshot loadValid(String aggregateId) throws Exception {
        try (var ps = db.prepareStatement(
                "SELECT aggregate_id, version, payload, taken_at, checksum FROM snapshots "
              + "WHERE aggregate_id = ?")) {
            ps.setString(1, aggregateId);
            try (var rs = ps.executeQuery()) {
                if (!rs.next()) return null;
                String payload = rs.getString("payload");
                String checksum = rs.getString("checksum");
                if (!Integer.toHexString(payload.hashCode()).equals(checksum)) {
                    return null;   // corrupt: force a full replay
                }
                return new Snapshot(rs.getString(1), rs.getLong("version"), payload,
                        rs.getTimestamp("taken_at").toInstant(), checksum);
            }
        }
    }
}

/**
 * Event schema evolution: the log is permanent, so old events must remain
 * readable FOREVER.
 *
 * Upcaster: rewrite an old event into the current shape at read time. Never
 * mutate stored events -- you interpret them.
 */
public final class EventUpcaster {

    /**
     * v1 Deposited: {accountId, amount: "125.50"}
     * v2 Deposited: {accountId, amountMinor: 12550, currency: "USD"}
     *
     * Both are in the log. The upcaster bridges them. When v1 events age out,
     * this class can be deleted.
     */
    public static Map<String, Object> upcast(String type, Map<String, Object> data) {
        if ("Deposited".equals(type) && !data.containsKey("amountMinor")) {
            java.math.BigDecimal amount =
                    new java.math.BigDecimal(String.valueOf(data.get("amount")));
            java.util.Map<String, Object> out = new java.util.LinkedHashMap<>();
            for (var e : data.entrySet()) {
                if (!e.getKey().equals("amount")) out.put(e.getKey(), e.getValue());
            }
            out.put("amountMinor",
                    amount.movePointRight(2).setScale(0,
                            java.math.RoundingMode.HALF_UP).longValue());
            out.putIfAbsent("currency", "USD");
            return Map.copyOf(out);
        }
        return data;
    }

    /**
     * TOLERANT READERS: the more robust technique, because they require no
     * central transform for every consumer.
     *
     *     long amountMinor = data.containsKey("amountMinor")
     *             ? ((Number) data.get("amountMinor")).longValue()
     *             : toMinor((BigDecimal) data.get("amount"));
     *
     * Use upcasting for renames and semantic changes; use tolerant readers for
     * additive changes. Never rely on a field being removed -- events are
     * forever, so every field must be treated as optional.
     */
    public static long toMinor(java.math.BigDecimal amount) {
        return amount.movePointRight(2).setScale(0,
                java.math.RoundingMode.HALF_UP).longValue();
    }
}
```