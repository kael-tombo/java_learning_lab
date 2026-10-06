# Distributed Transactions - Code Deep Dive

Pure Java. No frameworks. Each section names the failure it prevents.

## 1. The Transactional Outbox (fixes the dual-write problem)

```java
package systemdesign.transactions;

import java.sql.*;
import java.time.Instant;
import java.util.*;

/**
 * THE PROBLEM: writing to your database and publishing to a broker is two
 * writes. Between them there is a window:
 *
 *   DB commit  ----X----  broker publish        (crash here: event lost forever)
 *   DB commit  ----X----  partial publish       (crash here: phantom event)
 *
 * THE FIX: make the business row and the event row the SAME transaction, then
 * let a separate poller move committed events to the broker. The event cannot
 * be lost, and it CAN be duplicated — which is why every consumer here is
 * required to be idempotent.
 */
public final class OutboxRepository {

    private final Connection db;

    public OutboxRepository(Connection db) { this.db = db; }

    /**
     * Business mutation + outbox row in ONE local transaction.
     * Either both are durable or neither exists. This is the whole trick.
     */
    public void placeOrderAndEmit(String orderId, long cents) throws SQLException {
        boolean auto = db.getAutoCommit();
        db.setAutoCommit(false);
        try {
            // 1. The actual business write.
            try (PreparedStatement ps = db.prepareStatement(
                    "INSERT INTO orders(id, total_cents, status) VALUES (?,?,'PENDING')")) {
                ps.setString(1, orderId);
                ps.setLong(2, cents);
                ps.executeUpdate();
            }
            // 2. The event, same tx. Note the dedup key is UNIQUE so an
            //    accidental double-insert of the same event is impossible.
            try (PreparedStatement ps = db.prepareStatement(
                    "INSERT INTO outbox(event_id, aggregate_id, type, payload, " +
                    "dedup_key, created_at) VALUES (?,?,?,?,?,?) " +
                    "ON CONFLICT (dedup_key) DO NOTHING")) {
                ps.setString(1, UUID.randomUUID().toString());
                ps.setString(2, orderId);
                ps.setString(3, "OrderPlaced");
                ps.setString(4, "{\"totalCents\":" + cents + "}");
                ps.setString(5, "OrderPlaced:" + orderId);   // stable, not random
                ps.setTimestamp(6, Timestamp.from(Instant.now()));
                ps.executeUpdate();
            }
            db.commit();
        } catch (SQLException e) {
            db.rollback();          // both writes vanish together. Correct.
            throw e;
        } finally {
            db.setAutoCommit(auto);
        }
    }

    /**
     * The publisher side. Reads committed-but-unpublished rows and sends them.
     *
     * Two hazards this method must survive:
     *  (a) publishing succeeds, then the process dies before marking sent
     *      -> DUPLICATE event. Expected. Consumers must be idempotent.
     *  (b) two pollers read the same rows
     *      -> DUPLICATE events. Fixed by FOR UPDATE SKIP LOCKED (below).
     */
    public List<Event> claimBatch(int batchSize) throws SQLException {
        List<Event> out = new ArrayList<>();
        try (PreparedStatement ps = db.prepareStatement(
                "SELECT event_id, aggregate_id, type, payload FROM outbox " +
                "WHERE published_at IS NULL " +
                "ORDER BY id " +
                "LIMIT ? FOR UPDATE SKIP LOCKED")) {   // concurrent pollers, no double-claim
            ps.setInt(1, batchSize);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    out.add(new Event(rs.getString(1), rs.getString(2),
                                      rs.getString(3), rs.getString(4)));
                }
            }
        }
        return out;
    }

    public void markPublished(Collection<String> eventIds) throws SQLException {
        boolean auto = db.getAutoCommit();
        db.setAutoCommit(false);
        try (PreparedStatement ps = db.prepareStatement(
                "UPDATE outbox SET published_at = now() WHERE event_id = ?")) {
            for (String id : eventIds) { ps.setString(1, id); ps.addBatch(); }
            ps.executeBatch();
            db.commit();
        } catch (SQLException e) { db.rollback(); throw e; }
        finally { db.setAutoCommit(auto); }
    }

    public record Event(String eventId, String aggregateId, String type, String payload) {}
}
```

**Residual risk:** the outbox table grows forever unless you partition it by
time and drop old partitions. A `DELETE FROM outbox WHERE published_at < ?`
over 90M rows will itself become an outage.

## 2. Idempotency Store (the consumer half of effectively-once)

```java
/**
 * Exactly-once is not achievable over a network. What IS achievable:
 *
 *   at-least-once delivery  x  deduplication  =  effectively-once EFFECT
 *
 * The dedup store records the result, not just "seen". Storing the result
 * matters: a retry must return the SAME response as the original, or the
 * caller's client sees a different answer for the same logical request.
 *
 * CRITICAL: the TTL must exceed the broker's retention. See MATH_FOUNDATION.
 */
public final class IdempotencyStore {

    private final Map<String, Entry> entries = new java.util.concurrent.ConcurrentHashMap<>();

    public record Entry(String responseJson, String state, long expiresAt) {}

    /**
     * Two-phase claim so two concurrent requests with the SAME key cannot both
     * execute. If the second sees IN_PROGRESS it must wait/retry, not execute —
     * this is what prevents a thundering herd from double-charging.
     */
    public enum Claim { PROCEED, REPLAY, IN_PROGRESS }

    public Claim claim(String key, long ttlMillis) {
        long now = System.currentTimeMillis();
        Entry existing = entries.get(key);
        if (existing != null && existing.expiresAt() > now) {
            return "IN_PROGRESS".equals(existing.state()) ? Claim.IN_PROGRESS : Claim.REPLAY;
        }
        Entry fresh = new Entry(null, "IN_PROGRESS", now + ttlMillis);
        // putIfAbsent is atomic: only ONE caller can install the IN_PROGRESS row.
        Entry prev = entries.putIfAbsent(key, fresh);
        if (prev == null) return Claim.PROCEED;
        if (prev.expiresAt() <= now) return claim(key, ttlMillis);  // expired; retry
        return "IN_PROGRESS".equals(prev.state()) ? Claim.IN_PROGRESS : Claim.REPLAY;
    }

    public void complete(String key, String responseJson, long ttlMillis) {
        entries.compute(key, (k, old) ->
                new Entry(responseJson, "DONE", System.currentTimeMillis() + ttlMillis));
    }

    /** The ORIGINAL response, so retries are byte-identical. */
    public String replayResponse(String key) {
        Entry e = entries.get(key);
        return e == null ? null : e.responseJson();
    }

    /**
     * In production this is a single UPSERT against a UNIQUE-keyed table, or a
     * Redis SETNX with a TTL plus a persistent row for audit. In-memory here,
     * which is exactly why this lab cannot prove crash-safety: a process
     * restart loses the dedup window and duplicates get through.
     */
    public void sweep() {
        long now = System.currentTimeMillis();
        entries.entrySet().removeIf(e -> e.getValue().expiresAt() <= now);
    }
}
```

**Residual risk:** in-memory state is lost on restart. A production dedup
store must be durable, or a rolling deploy silently disables deduplication.

## 3. Saga Orchestrator with Compensation

```java
/**
 * Orchestration, not choreography: one coordinator owns the step list and the
 * compensation logic. The cost of that central brain is that it becomes a
 * component you must operate; the benefit is that the visible state of an
 * in-flight saga is inspectable in one place, which is worth a lot at 03:00.
 *
 * Compensation is attempted in REVERSE order of completion, and each
 * compensation must itself be idempotent — a retried refund must not refund
 * twice (route it through the same IdempotencyStore).
 */
public final class SagaOrchestrator {

    public interface Step {
        String name();
        /** @return a compensation token, or null if the step is irreversible. */
        Object execute(SagaContext ctx) throws Exception;
        void compensate(SagaContext ctx, Object token) throws Exception;
    }

    public enum SagaState { RUNNING, COMPLETED, COMPENSATING, FAILED_NEEDS_HUMAN }

    public static final class SagaContext {
        final Map<String, Object> data = new java.util.LinkedHashMap<>();
        public void put(String k, Object v) { data.put(k, v); }
        public <T> T get(String k) { return (T) data.get(k); }
    }

    private final SagaContext ctx = new SagaContext();
    /** Completed steps, newest last — compensation walks this backwards. */
    private final Deque<Compensable> completed = new ArrayDeque<>();
    private final List<String> nonCompensatable = new ArrayList<>();
    private SagaState state = SagaState.RUNNING;

    private record Compensable(Step step, Object token) {}

    public void run(List<Step> steps) {
        try {
            for (Step step : steps) {
                Object token = step.execute(ctx);
                if (token == null) {
                    // A null token means IRREVERSIBLE (e.g. "email sent").
                    // Record it loudly: from here, a later failure is NOT
                    // automatically recoverable and the design must route it
                    // to a human rather than pretending to roll back.
                    nonCompensatable.add(step.name());
                } else {
                    completed.push(new Compensable(step, token));  // push => reverse order
                }
            }
            state = SagaState.COMPLETED;
        } catch (Exception failure) {
            state = SagaState.COMPENSATING;
            compensate(failure);
        }
    }

    private void compensate(Exception cause) {
        List<String> compensationFailures = new ArrayList<>();
        while (!completed.isEmpty()) {
            Compensable c = completed.pop();
            try {
                c.step().compensate(ctx, c.token());
            } catch (Exception e) {
                compensationFailures.add(c.step().name());
            }
        }
        if (!compensationFailures.isEmpty() || !nonCompensatable.isEmpty()) {
            // Do NOT silently succeed. Escalate with full context so a human
            // can reconcile. This state must be in the alerting rules.
            state = SagaState.FAILED_NEEDS_HUMAN;
            throw new IllegalStateException(
                "saga unrecoverable: cause=" + cause
                + " compensationFailures=" + compensationFailures
                + " irreversibleSteps=" + nonCompensatable, cause);
        }
        state = SagaState.FAILED_NEEDS_HUMAN;
    }

    public SagaState state() { return state; }
    public SagaContext context() { return ctx; }
}
```

**Residual risk:** a crash mid-compensation loses the in-memory `completed`
stack. A durable saga log (state + completed-step list, fsynced) is mandatory
in production — otherwise recovery cannot even *decide* what to undo.

## 4. What "Exactly-Once" Really Means

```java
/**
 * The honest summary, in code.
 *
 * Claim:  "This happens exactly once."
 * Reality: it happens AT-LEAST-ONCE, and the duplicate is suppressed by an
 *          idempotent handler plus a dedup key derived from STABLE business
 *          identity — never from a random UUID generated per attempt.
 *
 * A per-attempt UUID is the single most common bug here: every retry looks
 * brand new to the dedup store, so nothing is ever deduplicated and the code
 * appears to work perfectly in tests (where retries never happen).
 */
public final class StableDedupKeys {
    /** Derived from business facts, so every retry produces the SAME key. */
    public static String forOrderPlaced(String orderId) {
        return "OrderPlaced:" + orderId;
    }

    public static String forPaymentCaptured(String paymentId, String attemptSeq) {
        // attemptSeq must be part of the BUSINESS identity (a legitimate second
        // capture), not the transport retry count. Conflating the two means you
        // either drop a real payment or allow a duplicate one.
        return "PaymentCaptured:" + paymentId + ":" + attemptSeq;
    }
}
```

**Residual risk:** deriving keys from business fields means the business rule
for identity must be written down and agreed. It is a domain decision wearing
an engineering costume — get the domain owner to sign it.