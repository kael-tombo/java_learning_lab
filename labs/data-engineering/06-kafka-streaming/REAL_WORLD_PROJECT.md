# Kafka Streaming — REAL WORLD PROJECT

## Context

A logistics platform ingests telematics from 300k vehicles, order events from
a 40-country commerce platform, and 90 partner webhooks — all on one Kafka
cluster that has become a single point of failure for a dozen downstream teams.
The platform team inherits 9,000 topics, inconsistent naming, and no schema
registry discipline. Your job is to standardize and stabilize it.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Cluster | 9 brokers (3 AZ), RF 3 |
| Throughput | 220k msg/s, 1.4 GB/s compressed peak |
| Topics | ~9,000 (many single-partition, many abandoned) |
| Partitions | 42,000 total, nearing the per-broker file-handle ceiling |
| Consumer groups | 340, of which ~60 are `assign`-based (no group management) |
| Retention | 7d general, compacted for state topics |
| SLO | 99.9% produce availability, p99 end-to-end < 3s |
| Constraint | no downtime window; a broker replacement is routine |

## Architecture (target state)

```
producers -> gateway tier (schema validation, topic-per-entity routing)
              |
   +----------+--------------------------+
   |          |          |               |
 domain    domain     domain         domain
 events    events     events         events
 (12p)     (48p)      (24p)          (6p)
   |          |          |               |
   +---- schema registry (BACKWARD compat enforced in CI) ----+
              |
   consumers: 340 groups, each with an explicit retention/ownership record
              |
   DLQ per domain event: <entity>.dlq.v1, retention 30d
```

## Key Implementation — topic contract as code

Topics become a reviewed, versioned artifact rather than console clicking.

```java
public record TopicSpec(String name, int partitions, short replication,
                        Map<String, String> config, String owner, String dataClass) {
    public static final String REGEX = "[a-z0-9-]+\\.(v[0-9]+)\\.[a-z-]+";
}

public final class TopicContract {
    private static final Set<String> FORBIDDEN_CONFIG =
            Set.of("cleanup.policy=delete", "retention.ms=-1");   // deliberate exclusions

    public static void validate(TopicSpec spec) {
        if (!spec.name().matches(TopicSpec.REGEX))
            throw new IllegalArgumentException("name must be <entity>.<version>.<type>: " + spec.name());
        if (spec.partitions() % 6 != 0)
            throw new IllegalArgumentException("partitions must be a multiple of broker count (6): " + spec.partitions());
        if (spec.replication() < 3)
            throw new IllegalArgumentException("RF must be >= 3 in a 3-AZ cluster");
        if (spec.owner() == null || spec.owner().isBlank())
            throw new IllegalArgumentException("every topic needs an owner for paging");
        spec.config().forEach((k, v) -> {
            if (k.equals("cleanup.policy") && v.equals("delete")
                    && spec.name().endsWith(".state"))
                throw new IllegalArgumentException("state topics must be compacted, not deleted");
        });
    }
}
```

## Partitioning Standard

The decision that mattered most: **key everything, choose keys for access
patterns, never for balance**.

```java
/**
 * Key selection rules, in priority order:
 *  1. Ordering scope needed by a consumer? key = the entity id that must be ordered.
 *  2. Skew? if one key carries > 5% of traffic, use a compound key (entityId, shard).
 *  3. Fan-out? if all consumers read all data, leave it null and let round-robin
 *     spread the load; ordering is then per-partition only.
 */
public static String keyFor(VehicleEvent e) {
    String base = e.vehicleId();
    return (e.gpsBucket() != null && hotVehicles().contains(base))
            ? base + ":" + e.gpsBucket()      // salt only the hot 0.4% of vehicles
            : base;
}
```

Two topics that were relitigated during this project:

| Topic | Key | Why |
|---|---|---|
| `orders.v2.events` | `order_id` | Consumer must see status transitions in order |
| `telemetry.v1.raw` | `vehicle_id` (salted for hot fleet IDs) | Ordering per vehicle matters for trip reconstruction; 40x skew fixed |
| `metrics.v1.points` | `null` | All consumers want all data; round-robin beats a 900-bucket key |

## Failure Modes and the Runbook

1. **Consumer group rebalance storm after deploys.** 340 groups x 20s rebalance
   = a 2-hour period where nothing is processed. Fix: `group.instance.id` static
   membership, rolling deploys with one member at a time, and moving processing
   off the poll thread so `max.poll.interval.ms` is never the binding constraint.
2. **File handle exhaustion on a broker.** Symptom: `Too many open files`, then
   that broker stops serving. Fix: reduce partition count (merge small topics),
   raise `num.io.threads`, and enforce a partition budget per broker in CI.
3. **Consumer lag on one group, not all.** Fix: check partition-level lag, not
   total; a single hot partition means skew, not throughput.
4. **Disk fills because retention is wrong on a compacted topic.** Symptom: a
   broker goes read-only, then producers stall everywhere. Fix: alerting on
   `log_dir_size` and a per-topic retention audit; `delete` on a state topic is a
   config lint failure, not a runtime discovery.
5. **Broker replacement procedure.** Fix: documented sequence — `kafka-leader-election`
   or controlled shutdown, verify RF is restored before starting the next
   replacement. Replacing two of three RF-3 brokers at once loses durability.
6. **Producer retries exhausting delivery timeout.** Symptom: `TimeoutException`
   with `acks=all`. Fix: raise `delivery.timeout.ms` above the rebalance/broker
   failover window, and treat it as an availability SLO breach.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Kafka is a distributed, partitioned, replicated, ordered log. Records are
  ordered within a partition, and each partition has a leader; replication factor
  and `acks` determine durability. Consumer groups distribute partitions across
  members, and committed offsets define where a consumer resumes.
  - Reference: https://kafka.apache.org/documentation/
  - Reference: https://kafka.apache.org/documentation/#design
  - Reference: https://kafka.apache.org/documentation/#intro_concepts_and_terms
- Log compaction retains the most recent record for each key, which makes a
  compacted topic a durable key-value store built from a log.
  - Reference: https://kafka.apache.org/documentation/#compaction
  - Reference: https://kafka.apache.org/documentation/#log_compaction

## Deliverables
- [ ] Topic contract class with validation and a CI lint job
- [ ] Partitioning standard with a written key-selection decision record
- [ ] Migration plan for 9,000 topics: merge, delete, or re-own
- [ ] Consumer group inventory: owner, retention, commit strategy, rebalance cost
- [ ] Broker replacement runbook, rehearsed in staging
- [ ] Lag SLO dashboard plus paging thresholds
