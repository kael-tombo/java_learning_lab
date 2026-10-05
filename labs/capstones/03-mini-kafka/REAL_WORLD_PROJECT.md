# Mini Kafka — REAL WORLD PROJECT

## Context

A logistics platform moves 220k messages/sec across 9,000 topics on a shared
Kafka cluster that every team depends on. Over 18 months the estate accumulated
inconsistent naming, 340 consumer groups, 60 that use manual `assign` (no group
management), and 4,100 topics that nobody reads. Two incidents in the last
quarter were caused by retention misconfiguration: a compacted state topic
declared with `cleanup.policy=delete` lost 2 days of offsets, and a broker went
read-only because a topic's retention was 10x the disk budget. You own the
platform.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Cluster | 9 brokers, 3 AZs, RF 3, NVMe + object tiering |
| Throughput | 220k msg/s, 1.4GB/s compressed, peak 2.1x on promo days |
| Topics | 4,100 (was 9,000; migration removed 4,900) |
| Partitions | 38,000 (was 74,000; small-topic merge halved it) |
| Consumer groups | 340, of which 60 were `assign`-based |
| Retention | 7d general, compacted for 140 state topics |
| SLO | produce availability 99.9%, p99 produce 12ms |
| Constraint | no maintenance window; broker replacement is routine |
| Compliance | PCI topic audit logs, 7-year retention via object tiering |

## Architecture (target)

```
producers -> [gateway: schema validation, topic routing, quota]
              |
        brokers x9 (RF 3, min.insync.replicas=2)
              |
   4,100 topics, 38,000 partitions, named <entity>.<version>.<type>
              |
   +----------+----------+-----------+------------+
   |          |          |           |            |
 warehouse  streaming  audit      cache         partner
 (48p)      (per domain) (compact, 7y)  (invalid.) (sandboxed)
              |
   every consumer group: documented owner, retention, commit strategy,
   rebalance cost measured, lag SLO with paging thresholds
```

## Key Implementation — the topic contract, and why it was the first thing

Topics were being created by hand, so 4,900 of them were abandoned and 1,400
had no owner. The contract makes topic creation a reviewed code change.

```java
public record TopicSpec(String name, int partitions, short replication,
                        Map<String, String> config, String ownerTeam,
                        String dataClass, RetentionClass retention) {
    public static final Pattern NAME = Pattern.compile("[a-z0-9-]+\\.v[0-9]+\\.[a-z-]+");
    public enum RetentionClass {
        GOLD(7, 400),          // days hot, days cold
        SILVER(14, 2_555),
        STATE(null, null),     // compacted, retained indefinitely
        AUDIT(90, 2_555)       // 7 years, object tiered
    }
}

public final class TopicContract {
    /**
     * The rule that catches the most: a state topic declared with
     * cleanup.policy=delete loses the latest value per key, and the failure
     * looks like data loss in the consumer, not a misconfiguration.
     */
    static final List<Rule> RULES = List.of(
        new Rule("name-matches-convention", s -> s.name().matches(TopicSpec.NAME.pattern()),
                 "name must be <entity>.<version>.<type>, e.g. orders.v2.events"),
        new Rule("partitions-multiple-of-broker-count",
                 s -> s.partitions() % BROKER_COUNT == 0,
                 "partitions must be a multiple of the broker count (9)"),
        new Rule("replication-at-least-3", s -> s.replication() >= 3,
                 "RF must be >= 3 across 3 AZs"),
        new Rule("state-topics-are-compacted",
                 s -> s.name().endsWith(".state") || !"delete".equals(s.config().get("cleanup.policy")),
                 "a .state topic must use cleanup.policy=compact"),
        new Rule("owner-present", s -> s.ownerTeam() != null && !s.ownerTeam().isBlank(),
                 "every topic needs an owning team for paging"),
        new Rule("disk-budget",
                 s -> estimatedBytesPerDay(s) * s.retention().daysHot() < CLUSTER_FREE_BYTES * 0.25,
                 "retention implies a disk footprint above 25% of free space; raise a ticket"),
        new Rule("pci-excluded",
                 s -> !"pci".equals(s.dataClass()) || s.config().containsKey("retention.ms"),
                 "a PCI-class topic needs an explicit retention.ms for the audit scope"));
}
```

## Key Implementation — the four changes and their measured effects

**1. Part count halved by merging small topics.** 74,000 partitions meant
~1.4M log segment files and metadata dominating broker memory. 4,100 topics
with a median of 3 partitions were merged into topic families
(`<entity>.v2.events` carrying 6 entity types as separate keys, keyed so
per-entity ordering survives).

| Metric | Before | After |
|---|---|---|
| Partitions | 74,000 | 38,000 |
| Log segment files | 1.4M | 690k |
| Broker metadata memory | 4.1GB | 1.9GB |
| Produce p99 | 31ms | 12ms |
| Consumer rebalance duration (12 partitions) | 4.2s | 1.8s |

**2. `min.insync.replicas=2` on every topic, and `acks=all` enforced at the
gateway.** This is the change that made the durability claim true.

```
Why it matters, in the incident terms:
  acks=all with no min.insync.replicas:
     broker 3 lags 5 min, drops out of ISR
     write with acks=all succeeds on brokers 1+2
     broker 1 dies, broker 2 becomes leader
     the record is GONE, and acks=all was satisfied
  with min.insync.replicas=2:
     broker 3 lags, ISR = {1,2}
     write with acks=all FAILS -> producer retries -> no silent loss
```

Two incidents in the prior year were exactly this. Since the change, zero.

**3. The 60 `assign`-based consumer groups were given real group semantics.**
`assign` means no membership management: no rebalance, no offset commit
coordinated by the group, no automatic recovery when a member dies. Each was a
single point of failure nobody owned.

```java
/**
 * What a group buys you, stated so the migration argument is concrete:
 *   - partition assignment across members, and reassignment on failure
 *   - committed offsets per (group, partition), so a restart resumes
 *   - a heartbeat and session timeout, so a dead member is detected
 *   - cooperative rebalancing (Kafka 3.x), which avoids stop-the-world
 * `assign` gives none of these. It is correct for exactly one consumer reading
 * a partition deliberately, and it is a liability everywhere else.
 */
public final class ConsumerMigration {
    public boolean shouldMigrateToGroup(ConsumerSpec c) {
        return c.usesManualAssign()
                && c.desiredConcurrency() > 1
                && !c.requiresExactPartitionPinning();   // the one valid reason to keep assign
    }
}
```

Result: 3 of the 4 worst consumer incidents were in this set. Post-migration:
zero.

**4. Retention and disk budgets enforced, with the state-topic rule above.**
The read-only broker incident is prevented by a nightly job that computes
per-topic footprint and pages before a topic can fill a broker.

```java
public record RetentionAudit(String topic, long bytesPerDay, int daysHot,
                             long projectedBytes, long diskFreeBytes,
                             double projectedUtilization, Verdict verdict) {
    public Verdict verdict() {
        // A single topic above 30% of free disk is a read-only-broker incident
        // waiting to happen, regardless of the cluster total.
        double share = (double) projectedBytes / diskFreeBytes;
        if (share > 0.30) return Verdict.BLOCK;
        if (share > 0.10) return Verdict.WARN;
        return Verdict.OK;
    }
}
```

**5. Object tiering for the 7-year audit retention.** Keeping 7 years hot was
impossible; keeping it in object storage costs about 1/20th and is readable
through the same client.

```sql
-- Compaction is wrong for a 7-year audit log: it would keep only the latest
-- value per key and destroy the history the retention exists to preserve.
-- The audit topics are cold tiered, never compacted.
ALTER TOPIC audit.v1.pci_transfers SET
  'cleanup.policy' = 'delete',
  'retention.ms' = '259200000',
  'remote.storage.enable' = 'true',
  'remote.storage.policy' = 'audit-7y';
```

## Key Implementation — the rebalance problem, measured

Rebalances were the largest single source of consumer latency. The migration
from stop-the-world `eager` rebalancing to `cooperative` plus static membership
changed the numbers materially.

```java
public record RebalancePolicy(String protocol, boolean staticMembership,
                              int sessionTimeoutMs, int heartbeatMs,
                              int maxPollRecords, int maxPollIntervalMs) {}

/**
 * The three that matter, in order:
 *   1. processing time < max.poll.interval.ms
 *      If a batch takes longer than this, the broker assumes the consumer
 *      died and rebalances the group. Processing must be off the poll thread
 *      or batches must be small; this is not a tuning knob, it is a design
 *      constraint.
 *   2. static membership (group.instance.id)
 *      A restart does not change the member id, so a rolling deploy causes
 *      zero rebalances.
 *   3. cooperative-sticky
 *      Only the partitions that actually moved are revoked, instead of all.
 */
static final RebalancePolicy DEFAULT_POLICY =
        new RebalancePolicy("cooperative-sticky", true, 45_000, 3_000, 500, 300_000);
```

| Metric | Before | After |
|---|---|---|
| Rebalances per member per week (deploy) | 2.0 | 0.0 (static membership) |
| Rebalance duration (12 partitions) | 8.4s | 0.9s (cooperative) |
| Consumer lag after a rolling deploy | +410k | +8k |
| Groups hitting `max.poll.interval` | 41 | 0 |

## Measured estate state

| Metric | Before | After |
|---|---|---|
| Topics | 9,000 | 4,100 |
| Topics with an owner | 1,400 (16%) | 4,100 (100%) |
| Orphaned topics (no consumer in 90d) | 4,900 | 0 (removed) |
| Partitions | 74,000 | 38,000 |
| `min.insync.replicas=2` coverage | 11% | 100% |
| Groups with measured rebalance cost | 0 | 340 |
| Broker read-only events | 1/quarter | 0 |
| Silent data-loss incidents | 2/year | 0 |
| Produce p99 | 31ms | 12ms |
| Monthly infra cost | $412k | $341k (-17%) |

The cost reduction is almost entirely storage, from removing 4,900 abandoned
topics that were still replicating three copies of nothing.

## Failure Modes and the Runbook

1. **Disk fills and a broker goes read-only.** Symptom: producers stall
   everywhere, `UNKNOWN_TOPIC_OR_PARTITION`. Fix: the retention audit pages at
   10% projected utilization; the broker returns to service after the
   offending retention is corrected, which is minutes not hours.
2. **Rebalance storm after a deploy.** Symptom: lag sawtooth, 340 groups
   rebalancing. Fix: static membership, rolling deploys one member at a time,
   and processing off the poll thread. Verify with the rebalance-cost metric
   per group, which is now on a dashboard.
3. **A consumer exceeds `max.poll.interval`.** Symptom: the member is evicted
   mid-batch, records reprocessed. Fix: reduce `max.poll.records` or move work
   off the poll thread; alert on the eviction metric so the cause is visible.
4. **Producer retries exhaust the delivery timeout.** Symptom:
   `TimeoutException` with `acks=all`. Fix: raise `delivery.timeout.ms` beyond
   the worst-case rebalance/failover window, and treat it as an availability
   breach, not a client bug.
5. **A schema change breaks consumers.** Symptom: deserialization errors, then
   a backlog. Fix: compatibility checked at commit time in the registry; a
   `BACKWARD` break cannot reach production. A `DROP` is a two-phase change.
6. **A key must move to a different partition after a bug.** Fix: this is
   genuinely hard and the honest answer is to write a compensating tool that
   consumes from the old partition, re-keys, and produces to the new one, with
   the old partition retained for the duration. It is a migration, not a
   config change, and it is worth saying so rather than implying otherwise.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Kafka is a partitioned, replicated, ordered log: records are ordered within
  a partition, each partition has a leader, and replication factor plus `acks`
  determine durability. Consumer groups distribute partitions across members,
  and committed offsets define the restart position.
  - Reference: https://kafka.apache.org/documentation/
  - Reference: https://kafka.apache.org/documentation/#design
  - Reference: https://kafka.apache.org/documentation/#intro_concepts_and_terms
- Kafka's producer and consumer configuration documentation specifies
  `acks`, `min.insync.replicas`, `enable.idempotence`, and
  `max.poll.interval.ms`, which together define the delivery guarantees a
  pipeline can actually claim.
  - Reference: https://kafka.apache.org/documentation/#producerconfigs
  - Reference: https://kafka.apache.org/documentation/#consumerconfigs
- Log compaction retains the most recent record per key; a compacted topic is a
  durable key-value store built from a log, and it is the wrong policy for an
  append-only audit log.
  - Reference: https://kafka.apache.org/documentation/#compaction

## Deliverables

- [ ] Topic contract with 7 rules, enforced at creation time in CI
- [ ] Topic inventory and the 4,900-topic migration/removal plan
- [ ] `min.insync.replicas=2` and `acks=all` enforced at the gateway, with the
      incident written up as the motivating case
- [ ] Partition merge plan reducing 74,000 to 38,000, with before/after metrics
- [ ] Consumer group migration for the 60 `assign`-based groups
- [ ] Rebalance policy: cooperative-sticky + static membership + poll budget
- [ ] Retention audit with a disk-budget rule, including the state-topic rule
- [ ] Object tiering design for 7-year audit retention (not compaction)
- [ ] Per-group dashboard: lag, rebalance count, rebalance duration, eviction count
- [ ] Runbook for the six failure modes
