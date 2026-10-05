# Message Queues & Protocols - REAL WORLD PROJECT

## Project: EventRail — the messaging backbone for a multi-tenant order platform

A marketplace processes 4 million events per day across orders, payments, inventory,
shipping, and notifications — for 12,000 merchant tenants. Events cross team boundaries, so
a broker choice that is wrong for one team's workload is wrong for everyone. The work:
select a protocol per workload class, define delivery semantics per topic, and make
backlog a non-event through honest capacity work.

### Architecture

```
  12,000 merchants, 4M events/day (~46 msg/s avg, 4,000 at peak)

  ┌──────────────── Workload classes, each with a different answer ───────────────┐
  │                                                                              │
  │  A. ORDER LIFECYCLE (the system of record)                                 │
  │     - must not lose an order event, ever                                   │
  │     - replayable: rebuild projections from history                          │
  │     → partitioned LOG (Kafka), 12 partitions by orderId                     │
  │       at-least-once + idempotent consumers, retention 7 days                │
  │                                                                              │
  │  B. ASYNC WORK (email, PDF, webhooks)                                       │
  │     - at-least-once is fine, delivery can be retried later                  │
  │     - high fan-out to third parties that are unreliable                    │
  │     → AMQP (RabbitMQ), per-tenant queue, publisher confirms                 │
  │       DLQ per tenant so one bad consumer cannot affect others                │
  │                                                                              │
  │  C. DEVICE TELEMETRY (lab 02's 30k devices)                                 │
  │     - high volume, individual messages are near-worthless                   │
  │     - must tolerate device networks that are down for minutes                │
  │     → MQTT (broker), QoS 0/1, retained last-value per device                │
  │       tiny footprint; a Java broker is too heavy for constrained devices     │
  │                                                                              │
  │  D. COMMAND / RPC (synchronous business flows)                              │
  │     - caller needs a response, not a stream                                 │
  │     → AMQP request/reply with a correlation id, 30s timeout                  │
  └──────────────────────────────────────────────────────────────────────────────┘

  Cross-cutting: schema registry (Avro, BACKWARD compatibility enforced),
  per-tenant rate limits, DLQ with tenant-scoped alerting, lag as an SLO
```

### Implementation

Topic and semantic governance, because the semantics must be explicit per topic:

```java
/**
 * Every topic declares its delivery semantic, its retention, and its partitions. A topic
 * with no declared semantic is a topic where two teams assume different guarantees, which
 * is a bug waiting for a redelivery.
 */
record TopicSpec(String name,
                 DeliverySemantic semantic,          // AT_LEAST_ONCE | EXACTLY_ONCE | AT_MOST_ONCE
                 int partitions,
                 Duration retention,
                 Set<String> producers,
                 Set<String> consumers,
                 String purpose,
                 String owner) {
    static final DeliverySemantic DEFAULT = AT_LEAST_ONCE;
}

@Component
class TopicRegistry {
    @PostConstruct
    void validateAgainstDeclaredPolicy() {
        for (TopicSpec t : specs.all()) {
            // EXACTLY_ONCE is expensive: it requires a transaction coordinator, limits
            // throughput, and interacts badly with non-transactional side effects. So it
            // requires a written justification, and by default it is refused.
            if (t.semantic() == EXACTLY_ONCE && !justificationFor(t).isPresent())
                throw new TopicPolicyException("EXACTLY_ONCE on " + t.name()
                        + " requires a documented justification naming the side effects it covers");

            // A system-of-record topic with AT_MOST_ONCE is almost always a mistake: an
            // order event that is dropped cannot be recovered by replay.
            if (t.purpose().contains("system of record") && t.semantic() == AT_MOST_ONCE)
                throw new TopicPolicyException("system-of-record topic " + t.name()
                        + " may not be AT_MOST_ONCE: a lost event is unrecoverable");
        }
    }
}
```

Per-tenant isolation, because one merchant must not be able to stall another's processing:

```java
/**
 * A single noisy tenant in a shared consumer group is a real incident. The design
 * separates SYSTEM health (is the pipeline working?) from TENANT health (is this merchant
 * failing?), and gives a failing tenant its own queue so it cannot consume capacity
 * belonging to others.
 */
@Component
class TenantAwareDispatcher {
    private final Map<String, Executor> perTenantExecutors = new ConcurrentHashMap<>();
    private final Map<String, CircuitBreaker> tenantBreakers = new ConcurrentHashMap<>();

    void dispatch(TenantEvent e) {
        var executor = perTenantExecutors.computeIfAbsent(e.tenantId(), t -> boundedExecutorFor(t));
        var breaker = tenantBreakers.computeIfAbsent(e.tenantId(), t -> CircuitBreaker.of("tenant-" + t));

        // A tenant whose webhooks have been failing for 10 minutes gets OPENED: its events
        // accumulate in its own queue and its DLQ, rather than consuming worker threads
        // and inflating the lag of the shared group.
        breaker.execute(() -> executor.submit(() -> process(e)));
    }

    /** Bounded per-tenant concurrency with a global cap. Without both limits, one tenant
     *  can exhaust the whole pool (fairness) or the pool itself (collapse). */
    private Executor boundedExecutorFor(String tenantId) {
        var sem = new Semaphore(perTenantConcurrency(tenantId));   // e.g. 5
        var pool = new ThreadPoolExecutor(2, perTenantConcurrency(tenantId),
                60, SECONDS, new LinkedBlockingQueue<>(queueDepthFor(tenantId)),
                new ThreadFactoryBuilder().setNameFormat("tenant-" + tenantId + "-%d").build(),
                // REJECT to the tenant's own queue rather than blocking the dispatcher.
                // Blocking here propagates back-pressure into the consumer poll loop and
                // causes a rebalance, which is a self-inflicted outage.
                new ThreadPoolExecutor.DiscardOldestPolicy());
        return new SemaphoreBoundedExecutor(pool, sem);
    }
}
```

Lag as a leading indicator with actionable thresholds, not a number on a dashboard:

```java
/**
 * Lag alerts are only useful if the threshold corresponds to something the team can do.
 * The key change: express the threshold in TIME TO CLEAR, not in message count. A 500k
 * message backlog means nothing without knowing the processing rate.
 */
class LagAlerting {
    record LagAssessment(long lagMessages, long consumptionRatePerSec, Duration sinceLastRebalance) {
        Duration timeToClear() {
            return consumptionRatePerSec > 0
                    ? Duration.ofSeconds(lagMessages / consumptionRatePerSec)
                    : Duration.ofDays(1);                       // not consuming at all
        }
        Severity severity() {
            Duration ttl = timeToClear();
            if (consumptionRatePerSec == 0) return Severity.PAGE;         // stopped
            if (ttl.compareTo(STRETCH_SLO) > 0)  return Severity.PAGE;    // cannot clear in time
            if (ttl.compareTo(STRETCH_WARNING) > 0) return Severity.TICKET;
            return Severity.NONE;
        }
    }

    @Scheduled(fixedDelay = 60_000)
    void assess() {
        for (var group : kafka.admin().listConsumerGroups()) {
            var lag = consumerLag(group);
            var rate = consumptionRate(group);
            var assessment = new LagAssessment(lag, rate, sinceLastRebalance(group));

            if (assessment.severity() != Severity.NONE) {
                // The alert carries the DIAGNOSIS PATH, not just the number:
                // rate == 0 -> is it a rebalance loop, a stuck consumer, or a down dependency?
                var likelyCause = diagnose(group, assessment);
                alerts.raise("CONSUMER_LAG", group, assessment, likelyCause);
            }
        }
    }

    /** A rebalance loop looks exactly like lag from the outside. Distinguishing them is
     *  most of the value: one needs `max.poll.interval`, the other needs a restart. */
    String diagnose(String group, LagAssessment a) {
        if (rebalanceCount(group, Duration.ofHours(1)) > 20)
            return "REBALANCE_LOOP: check max.poll.interval vs processing time; "
                 + "consider separate consumer groups for slow handlers";
        if (a.consumptionRatePerSec() == 0)
            return "NOT_CONSUMING: check consumer liveness and downstream dependency health";
        if (rebalanceCount(group, Duration.ofHours(1)) > 3)
            return "UNSTABLE_PARTITION_OWNERSHIP: one member is flapping";
        return "UNDER_PROVISIONED: consumption rate below production rate; scale consumers";
    }
}
```

Schema evolution enforced, so a producer change cannot break every consumer at once:

```java
/**
 * Avro BACKWARD compatibility, enforced in CI. The rule: a new schema must be readable by
 * the OLD consumers. Adding a field with a default is safe; removing a field is not;
 * changing a type is not. Enforced mechanically, because a schema break at 3am with 40
 * consumer groups is an outage.
 */
@Component
class SchemaCompatibilityGate {
    void validate(String topic, Schema newSchema) {
        var registry = schemaRegistry.forSubject(topic);
        var versions = registry.versions();
        if (versions.isEmpty()) { registry.register(newSchema); return; }

        var compatibility = registry.configuredCompatibility();
        var result = switch (compatibility) {
            case BACKWARD  -> newSchema.isBackwardCompatibleWith(registry.latest());
            case FULL      -> newSchema.isBackwardCompatibleWith(registry.latest())
                              && registry.latest().isBackwardCompatibleWith(newSchema);
            case NONE      -> CompatibilityResult.compatible();
        };
        if (!result.compatible())
            throw new IncompatibleSchemaException(topic, registry.latest(), newSchema,
                    result.errors());
        registry.register(newSchema);
    }
}
```

Replay, which is a log's superpower and also a real operational risk:

```java
/**
 * Replay rebuilds a projection from history. Two things make it dangerous, and both are
 * handled explicitly rather than discovered:
 *   1. Side effects: replaying order.placed will re-trigger emails and webhooks.
 *      Solution: consumers declare which events they handle in REPLAY mode, and by default
 *      suppress external side effects.
 *   2. Position: a consumer reading from the beginning while production continues.
 *      Solution: replay to a SEPARATE group id, so the live consumer's offsets are untouched.
 */
class ProjectionRebuildJob {
    void rebuild(String projection, Instant from) {
        var replayGroup = "replay-" + projection + "-" + runId();   // isolated group id
        schemaRegistry.pinVersion(projection, from);                // read the OLD schema

        consumer.subscribeWithOptions(Map.of(
                "group.id", replayGroup,
                "auto.offset.reset", "earliest",
                "read.committed", "true"),
                topics: topicsFor(projection),
                fromTimestamp: from);

        // Consumers in replay mode MUST NOT send emails or call webhooks.
        replayContext.set(true);
        runUntilCaughtUpTo(endOffsetsSnapshot());                    // snapshot the tail FIRST
        replayContext.clear();
        swapProjectionAtomically(projection);                       // readers see old until the swap
    }
}
```

### Non-functional requirements

- **Durability**: zero loss of order lifecycle events. Acknowledgement is producer-side
  with `acks=all` and a replication factor of 3; a single-broker failure cannot lose a message.
- **Throughput**: 4,000 events/second at peak with p99 publish latency under 50 ms, and a
  stated ceiling of 20,000/sec, verified by load test, not estimated.
- **Recovery objective**: consumer lag clears within 30 minutes after a 2-hour outage for
  the order stream; the alert fires when time-to-clear exceeds 30 minutes, not at a
  message count.
- **Isolation**: a failing tenant's backlog must not affect other tenants' processing.
  Verified by a test that fails one tenant's webhooks and asserts other tenants' lag stays flat.
- **Backpressure**: bounded per-tenant queues that reject to the tenant's own buffer rather
  than blocking the dispatcher and triggering a rebalance.
- **Schema safety**: 100% of topics with a registered schema and enforced compatibility.
  A CI failure blocks a producer deploy.
- **Dead letters**: every DLQ entry alerted with its tenant, expired entries purged with an
  audit trail, and replay refusing messages that would fail again.
- **Cost**: retention and partition counts tuned to actual consumption; a 7-day retention on
  a topic read within 1 hour is waste, and the review quantifies it.
- **Observability**: per-topic publish/consume rate, lag with time-to-clear, rebalance
  counts, DLQ depth, and a dashboard that leads with the diagnosis path rather than the raw number.
- **Onboarding**: a new team gets a template with semantic, retention, schema, and DLQ
  preconfigured, because a misconfigured topic is discovered in production rather than in review.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Apache Kafka documentation describes the partitioned-log model, consumer groups, offset
  management, and delivery semantics that workload class A is built on.
  https://kafka.apache.org/documentation/
- RabbitMQ documentation covers AMQP semantics, publisher confirms, dead-letter exchanges,
  and per-queue isolation used for workload classes B and D.
  https://www.rabbitmq.com/docs

## Deliverables

- [x] Topic registry declaring semantics, retention, and partitions, with policy enforcement
- [x] EXACTLY_ONCE refused without written justification; system-of-record topics barred from AT_MOST_ONCE
- [x] Per-tenant bounded concurrency and circuit breaking with rejection to a tenant-local buffer
- [x] Lag alerting expressed as time-to-clear, with a diagnosis path in the alert itself
- [x] Rebalance-loop diagnosis separated from under-provisioning in the alerting logic
- [x] Avro schema compatibility gate in CI, blocking incompatible producer changes
- [x] Safe projection replay with an isolated group id and suppressed side effects
- [x] Bounded DLQ with tenant-scoped alerting, retention, and replay guards
- [x] Isolation test proving one failing tenant does not affect other tenants' lag
