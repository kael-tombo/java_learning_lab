# Microservices - Code Deep Dive

Pure Java. Each section is a failure that distributed systems make possible.

## 1. Saga Orchestrator with Durable State

```java
package systemdesign.microservices;

import java.util.*;

/**
 * A saga is a distributed transaction with NO rollback -- only compensating
 * actions. Three properties are non-negotiable:
 *
 *   1. Every step is IDEMPOTENT. Retries are guaranteed, so a non-idempotent
 *      step will double-apply. There is no way around this.
 *   2. Compensation is a NEW business action, not an undo. Refunding is not
 *      un-charging: the money moved and the customer sees both transactions.
 *   3. State must be DURABLE. Without a persisted saga log, a crash
 *      mid-compensation leaves recovery unable to even decide what to undo.
 */
public final class SagaOrchestrator {

    public enum SagaState { RUNNING, COMPLETED, COMPENSATING, NEEDS_HUMAN }

    public interface Step {
        String name();
        /** @return a compensation token, or null if the step is IRREVERSIBLE. */
        Object execute(SagaState ctx) throws Exception;
        void compensate(SagaState ctx, Object token) throws Exception;
    }

    /** In production this is a table, fsynced in the same tx as step effects. */
    public interface SagaLog {
        void recordStep(SagaId id, int position, String stepName, Object token);
        void recordState(SagaId id, SagaState state);
        List<String> completedSteps(SagaId id);   // used by recovery
    }

    public record SagaId(String value) {}

    private final SagaLog log;
    private final Map<SagaId, SagaState> states = new ConcurrentHashMapHash<>();

    public SagaOrchestrator(SagaLog log) { this.log = log; }

    public void run(SagaId id, List<Step> steps) {
        states.put(id, SagaState.RUNNING);
        List<String> irreversible = new ArrayList<>();
        List<Exception> compensationFailures = new ArrayList<>();

        try {
            int position = 0;
            for (Step step : steps) {
                Object token = step.execute(null);
                log.recordStep(id, position++, step.name(), token);
                if (token == null) {
                    // A null token means IRREVERSIBLE (email sent, parcel shipped).
                    // Record it: from here a later failure CANNOT be rolled back,
                    // and pretending otherwise is how money disappears.
                    irreversible.add(step.name());
                }
            }
            states.put(id, SagaState.COMPLETED);
            log.recordState(id, SagaState.COMPLETED);

        } catch (Exception failure) {
            states.put(id, SagaState.COMPENSATING);
            log.recordState(id, SagaState.COMPENSATING);

            // Compensate in REVERSE order of completion.
            List<String> completed = new ArrayList<>(log.completedSteps(id));
            Collections.reverse(completed);
            for (String name : completed) {
                Step step = findStep(steps, name);
                if (step == null) continue;
                try {
                    // Compensation is itself a distributed call and can fail.
                    // Each compensation MUST be idempotent: a retried refund
                    // must not refund twice.
                    step.compensate(null, null);
                } catch (Exception e) {
                    compensationFailures.add(new Exception(name, e));
                }
            }

            // Do NOT silently succeed. Escalate with full context so a human can
            // reconcile. This state MUST be in the alerting rules.
            states.put(id, SagaState.NEEDS_HUMAN);
            log.recordState(id, SagaState.NEEDS_HUMAN);
            throw new IllegalStateException(
                    "saga unrecoverable id=" + id.value()
                    + " cause=" + failure
                    + " irreversibleSteps=" + irreversible
                    + " compensationFailures=" + compensationFailures.size(), failure);
        }
    }

    private static Step findStep(List<Step> steps, String name) {
        return steps.stream().filter(s -> s.name().equals(name)).findFirst().orElse(null);
    }

    public SagaState state(SagaId id) { return states.getOrDefault(id, SagaState.RUNNING); }
}
```

**Residual risk:** recovery after a crash reads `log.completedSteps(id)` and
finishes the compensation. Test it by killing the process mid-saga; if recovery
cannot reconstruct what to undo, the saga log is not durable enough.

## 2. Transactional Outbox (removes the dual-write problem)

```java
/**
 * THE PROBLEM: business write + event publish is TWO writes. Between them:
 *
 *   DB commit ---X--- publish        -> event lost forever
 *   DB commit ---X--- partial publish -> phantom event
 *
 * THE FIX: same transaction, then a separate poller publishes. The event
 * cannot be lost. It CAN be duplicated -- which is why every consumer must be
 * idempotent. Duplicates are acceptable; silent loss is not.
 */
public final class OutboxPublisher {

    public record Event(String eventId, String aggregateId, String type,
                        String payload, String dedupKey, Instant createdAt) {}

    private final java.sql.Connection db;

    public OutboxPublisher(java.sql.Connection db) { this.db = db; }

    /** Business row + outbox row in ONE local transaction. */
    public void writeWithEvent(String aggregateId, String sql, Object... args,
                               String eventType, String payload) throws Exception {
        boolean auto = db.getAutoCommit();
        db.setAutoCommit(false);
        try {
            try (var ps = db.prepareStatement(sql)) {
                for (int i = 0; i < args.length; i++) ps.setObject(i + 1, args[i]);
                ps.executeUpdate();
            }
            try (var ps = db.prepareStatement(
                    "INSERT INTO outbox(event_id, aggregate_id, type, payload, dedup_key, "
                    + "created_at) VALUES (?,?,?,?,?,?) ON CONFLICT (dedup_key) DO NOTHING")) {
                ps.setString(1, UUID.randomUUID().toString());
                ps.setString(2, aggregateId);
                ps.setString(3, eventType);
                ps.setString(4, payload);
                // STABLE business identity, NOT a per-attempt UUID. A per-attempt
                // UUID makes the ON CONFLICT clause useless and duplicates
                // silently through -- and it always passes tests, because tests
                // do not retry.
                ps.setString(5, eventType + ":" + aggregateId);
                ps.setTimestamp(6, Timestamp.from(Instant.now()));
                ps.executeUpdate();
            }
            db.commit();
        } catch (Exception e) {
            db.rollback();     // both writes vanish together. Correct.
            throw e;
        } finally {
            db.setAutoCommit(auto);
        }
    }

    /**
     * FOR UPDATE SKIP LOCKED lets multiple pollers read disjoint batches. Without
     * it, two pollers read the same rows and every event is published twice.
     */
    public List<Event> claimBatch(int size) throws Exception {
        List<Event> out = new ArrayList<>();
        try (var ps = db.prepareStatement(
                "SELECT event_id, aggregate_id, type, payload, dedup_key, created_at "
              + "FROM outbox WHERE published_at IS NULL ORDER BY id LIMIT ? "
              + "FOR UPDATE SKIP LOCKED")) {
            ps.setInt(1, size);
            try (var rs = ps.executeQuery()) {
                while (rs.next()) {
                    out.add(new Event(rs.getString(1), rs.getString(2), rs.getString(3),
                            rs.getString(4), rs.getString(5),
                            rs.getTimestamp(6).toInstant()));
                }
            }
        }
        return out;
    }

    public void markPublished(Collection<String> ids) throws Exception {
        boolean auto = db.getAutoCommit();
        db.setAutoCommit(false);
        try (var ps = db.prepareStatement(
                "UPDATE outbox SET published_at = now() WHERE event_id = ?")) {
            for (String id : ids) { ps.setString(1, id); ps.addBatch(); }
            ps.executeBatch();
            db.commit();
        } catch (Exception e) { db.rollback(); throw e; }
        finally { db.setAutoCommit(auto); }
    }
}
```

**Residual risk:** the outbox table grows unboundedly. Partition it by time and
drop old partitions; a `DELETE` over 90M rows is itself an outage.

## 3. Circuit Breaker with Three States

```java
/**
 * A breaker prevents a failing dependency from exhausting the caller's
 * resources, and gives the dependency a chance to recover.
 *
 * THE MINIMUM-REQUEST THRESHOLD IS NOT OPTIONAL. Without it, a service
 * receiving 1 rps of 3-second failures never reaches a 50% window with enough
 * samples, the breaker never opens, and requests queue forever.
 */
public final class CircuitBreaker {

    public enum State { CLOSED, OPEN, HALF_OPEN }

    private final int failureThresholdPercent;
    private final int minimumRequests;
    private final long openDurationMillis;
    private final int halfOpenProbeCount;

    private final AtomicInteger windowSuccess = new AtomicInteger();
    private final AtomicInteger windowFailure = new AtomicInteger();
    private final AtomicInteger halfOpenSuccesses = new AtomicInteger();
    private volatile State state = State.CLOSED;
    private volatile long openedAtMillis;

    public CircuitBreaker(int failureThresholdPercent, int minimumRequests,
                          long openDurationMillis, int halfOpenProbeCount) {
        this.failureThresholdPercent = failureThresholdPercent;
        this.minimumRequests = minimumRequests;
        this.openDurationMillis = openDurationMillis;
        this.halfOpenProbeCount = halfOpenProbeCount;
    }

    public boolean allowRequest() {
        if (state == State.CLOSED) return true;
        if (state == State.OPEN) {
            if (System.currentTimeMillis() - openedAtMillis >= openDurationMillis) {
                synchronized (this) {
                    if (state == State.OPEN) {
                        state = State.HALF_OPEN;
                        halfOpenSuccesses.set(0);
                    }
                }
            }
            return state == State.HALF_OPEN
                    && halfOpenSuccesses.get() < halfOpenProbeCount;
        }
        return false;   // HALF_OPEN, probes already in flight
    }

    public void recordSuccess() {
        if (state == State.HALF_OPEN) {
            if (halfOpenSuccesses.incrementAndGet() >= halfOpenProbeCount) {
                state = State.CLOSED;   // recovered
                resetWindow();
            }
        } else {
            windowSuccess.incrementAndGet();
        }
    }

    public void recordFailure() {
        if (state == State.HALF_OPEN) {
            state = State.OPEN;          // one probe failure re-opens immediately
            openedAtMillis = System.currentTimeMillis();
            return;
        }
        windowFailure.incrementAndGet();
        int total = windowSuccess.get() + windowFailure.get();
        if (total >= minimumRequests
                && (windowFailure.get() * 100 / total) >= failureThresholdPercent) {
            state = State.OPEN;
            openedAtMillis = System.currentTimeMillis();
            resetWindow();
        }
    }

    /** Callers should roll the window; in production this is time-based, not count-based. */
    public void onWindowElapsed() { if (state == State.CLOSED) resetWindow(); }
    private void resetWindow() { windowSuccess.set(0); windowFailure.set(0); }
    public State state() { return state; }
}
```

**Residual risk:** a count-based window behaves differently at different
traffic rates. A time-based window is correct in production, and it is also
what makes the behaviour identical during a traffic spike — which is when it
matters.

## 4. Bulkhead: Per-Dependency Resource Pools

```java
/**
 * Without bulkheads, ONE slow dependency consumes every thread in the process:
 *
 *   payment service has 12 threads, goes slow
 *   -> 12 threads block on payment
 *   -> the shared 100-thread pool is starved
 *   -> ALL checkout traffic fails because of a 10% dependency
 *
 * With bulkheads, only the payment pool is affected. 88 threads keep serving.
 * The failure is bounded AND VISIBLE.
 */
public final class Bulkhead {

    public static final class Permit { private Permit() {} }

    private final java.util.concurrent.Semaphore semaphore;
    private final java.util.concurrent.atomic.AtomicInteger inFlight =
            new java.util.concurrent.atomic.AtomicInteger();
    private final java.util.concurrent.atomic.AtomicInteger rejected =
            new java.util.concurrent.atomic.AtomicInteger();
    private final long queueTimeoutMillis;

    public Bulkhead(int permits, long queueTimeoutMillis) {
        this.semaphore = new java.util.concurrent.Semaphore(permits);
        this.queueTimeoutMillis = queueTimeoutMillis;
    }

    /**
     * Size with Little's Law: permits = throughput * service_time * safety.
     *   100 rps to payment, 120 ms p50 -> 12; use 12-24.
     * Do not guess this number.
     */
    public Permit acquire() throws BulkheadFullException {
        try {
            // tryAcquire with a TIMEOUT, not indefinite. Waiting indefinitely
            // just moves the queue somewhere less visible.
            if (!semaphore.tryAcquire(queueTimeoutMillis, java.util.concurrent.TimeUnit.MILLISECONDS)) {
                rejected.incrementAndGet();
                throw new BulkheadFullException("bulkhead exhausted; shedding load");
            }
            inFlight.incrementAndGet();
            return new Permit();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new BulkheadFullException("interrupted while waiting for permit");
        }
    }

    public void release() { inFlight.decrementAndGet(); semaphore.release(); }
    public int inFlight() { return inFlight.get(); }
    public int rejected() { return rejected.get(); }

    public static class BulkheadFullException extends RuntimeException {
        public BulkheadFullException(String m) { super(m); }
    }
}
```

**Residual risk:** shedding load returns an error to the user. That is correct
— a fast, honest failure beats a slow, opaque one — but it means bulkhead
rejections must be a first-class metric with an alert, not a silent error rate.

## 5. Deadline Propagation Across Services

```java
/**
 * Without propagation, a client that times out at 1,000 ms still causes:
 *   gateway to wait 2,000 ms -> order to wait 3,000 ms -> inventory to do
 *   10 s of work nobody is waiting for.
 *
 * Wasted work under load becomes queueing, which becomes timeout, which
 * produces MORE wasted work. The spiral is why an unbounded chain collapses.
 *
 * Propagate an ABSOLUTE deadline. A duration restarts at every hop and never
 * terminates.
 */
public final class DeadlinePropagation {

    public static final String HEADER = "x-request-deadline";
    private static final long DEFAULT_BUDGET_MS = 30_000;
    private static final ThreadLocal<Long> DEADLINE = new ThreadLocal<>();

    public static void start(long budgetMs) {
        DEADLINE.set(System.currentTimeMillis() + Math.max(1, budgetMs));
    }

    /** Each hop subtracts its own cost before calling out. */
    public static String nextDeadline(String inboundHeader, long ownCostMs) {
        long parent = DEADLINE.get();
        if (inboundHeader != null && !inboundHeader.isBlank()) {
            parent = Long.parseLong(inboundHeader);
        } else if (parent == 0) {
            parent = System.currentTimeMillis() + DEFAULT_BUDGET_MS;
        }
        return Long.toString(Math.max(parent - ownCostMs, 1));
    }

    /**
     * How long this service may work. Small reserve so the response can be
     * shaped and returned BEFORE the client gives up.
     */
    public static long budgetForWork() {
        Long d = DEADLINE.get();
        if (d == null) return DEFAULT_BUDGET_MS;
        return Math.max(0, d - System.currentTimeMillis() - 25);
    }

    public static boolean expired() { return budgetForWork() <= 0; }
}
```

**Residual risk:** a service that ignores the header wastes capacity regardless.
That is why mesh-level propagation exists — an application cannot enforce
correctness on its neighbours.

## 6. Service Discovery with a Static Fallback

```java
/**
 * Discovery is a dependency. If it is unavailable and there is no fallback,
 * routing stops even though every service is healthy -- a self-inflicted
 * outage caused by a component that serves no user-facing work.
 *
 * Resolution order: cache -> fetch -> STATIC FALLBACK.
 */
public final class ServiceDiscovery {

    public record Instance(String serviceId, String host, int port, boolean healthy) {}

    private final Map<String, List<Instance>> cache = new ConcurrentHashMap<>();
    private final Map<String, List<Instance>> staticFallback = new ConcurrentHashMap<>();
    private final java.util.function.Function<String, List<Instance>> registryClient;
    private final long cacheTtlMillis;

    public ServiceDiscovery(Map<String, List<Instance>> staticFallback,
                            java.util.function.Function<String, List<Instance>> registryClient,
                            long cacheTtlMillis) {
        this.staticFallback = Map.copyOf(staticFallback);
        this.registryClient = registryClient;
        this.cacheTtlMillis = cacheTtlMillis;
    }

    public List<Instance> resolve(String serviceId) {
        List<Instance> cached = cache.get(serviceId);
        if (cached != null && !cached.isEmpty()) {
            // TTL check happens on refresh; serving stale here is deliberate --
            // a slightly stale endpoint list beats no endpoint list.
            return cached;
        }
        try {
            List<Instance> fresh = registryClient.apply(serviceId);
            if (fresh != null && !fresh.isEmpty()) {
                cache.put(serviceId, fresh);
                return fresh;
            }
        } catch (Exception e) {
            // fall through to static -- the registry is down, not the services
        }
        List<Instance> fallback = staticFallback.getOrDefault(serviceId, List.of());
        if (fallback.isEmpty()) {
            throw new IllegalStateException("no instances for " + serviceId
                    + " (cache empty and no static fallback)");
        }
        return fallback;
    }

    public void invalidate(String serviceId) { cache.remove(serviceId); }
    public long cacheTtlMillis() { return cacheTtlMillis; }
}
```

**Residual risk:** the static fallback lists go stale as instances are added and
removed. They are a floor, not a plan — and a stale entry pointing at a
decommissioned instance produces connection errors that look like a service bug.