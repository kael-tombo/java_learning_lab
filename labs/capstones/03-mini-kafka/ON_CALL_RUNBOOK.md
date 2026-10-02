# On-Call Runbook: Mini-Kafka Message Broker (Capstone 03)

> Scope: `BrokerCluster` (controller + brokers), `TopicManager`, `PartitionLeader`, `ReplicaManager`, `ConsumerGroupCoordinator`, `LogManager`, `QuotaManager`.
> Audience: on-call engineer for a team running this Java Kafka-compatible broker in production.

## 1. Service Map & SLOs

| Component | SLO | Key Signal |
|---|---|---|
| `Produce` (acks=all) | p99 latency < 50 ms, error rate < 0.01% | Request latency, produce error rate |
| `Fetch` (consumer) | p99 latency < 100 ms, max lag < 10k messages | Consumer lag, fetch latency |
| Controller election | < 10 s failover | Controller epoch changes, ZK session expiry |
| Partition leadership | < 5 s failover (ISR) | Leader election rate, unclean elections |
| Log retention | Compaction lag < 1 hr | Log cleaner lag, segment count |
| Disk usage | < 80% per broker | Disk free space, log dir usage |

## 2. Triage Decision Tree (first 5 minutes)

```
produce/fetch latency spike or errors?
├─ YES → §3 Broker Latency / Produce-Fetch Errors
├─ NO → consumer lag growing?
│   ├─ YES → §4 Consumer Lag Incident
│   └─ NO → broker down / ISR shrink?
│       ├─ YES → §5 Broker Failure / ISR Shrink
│       └─ NO → controller issues?
│           ├─ YES → §6 Controller Instability
│           └─ NO → disk pressure? → §7
```

Always note: affected topics/partitions, broker IDs, recent config changes, deployment history.

## 3. Runbook: Broker Latency / Produce-Fetch Errors

**Symptoms:** Produce p99 > 200 ms, fetch errors, `NotEnoughReplicasException`, `LeaderNotAvailableException`, request queue buildup.

**Diagnose (0–10 min):**
1. Check broker metrics: `RequestQueueTimeMs`, `ResponseQueueTimeMs`, `IoTimeMs`, `NetworkProcessor` idle %.
2. Check disk I/O: `iowait`, disk throughput, latency (iostat -x 1).
3. Check GC: long pauses coinciding with latency spikes (G1/ZGC logs).
4. Look for hot partitions: single partition driving disproportionate traffic.
5. Check `QuotaManager`: client quota exceeded causing throttling.

**Mitigate (10–20 min):**
- Hot partition: add partitions (if key allows), redirect producer to different key, increase `num.partitions`.
- Disk I/O: throttle log cleaner, increase `num.io.threads`, move topics to faster disks.
- GC pauses: tune heap, enable incremental compaction, check for allocation spikes.
- Quota throttle: increase quota for affected client, identify runaway producer.
- **Do NOT:** reduce `min.insync.replicas` (durability risk), disable acks, restart brokers unnecessarily.

## 4. Runbook: Consumer Lag Incident

**Symptoms:** `ConsumerLag` alert firing, lag > 100k per partition, processing latency increasing, consumer group rebalances frequent.

**Diagnose:**
1. Identify lagging consumer group(s) and topic-partitions.
2. Check consumer health: alive? processing? `ConsumerGroupCoordinator` shows members?
3. Look for rebalance storms: `REBALANCE_IN_PROGRESS` frequent, `JoinGroup` failures.
4. Check processing logic: downstream dependency slow, deserialization errors, poison pills.
5. Verify `fetch.max.bytes`, `max.poll.records`, `max.poll.interval.ms` config.

**Mitigate:**
- Consumer down: restart consumer pods, check deployment rollout.
- Rebalance storm: increase `session.timeout.ms`, `heartbeat.interval.ms`, enable static membership.
- Slow processing: scale consumer instances, increase `max.poll.records`, optimize downstream calls.
- Poison pill: skip offset (with DLQ), fix deserialization, reprocess.
- Lag recovery: temporary consumer burst (increase instances), pause non-critical topics.

## 5. Runbook: Broker Failure / ISR Shrink

**Symptoms:** Broker UNREACHABLE, `UnderReplicatedPartitions` alert, ISR shrink, `OfflinePartitionsCount` > 0.

**Diagnose:**
1. Check broker status: process alive? JVM health? Network partition? Disk full?
2. Check ZooKeeper/KRaft: broker ephemeral node exists? Controller can reach broker?
3. Identify affected partitions: which topics/partitions lost replicas?
4. Check `ReplicaManager`: fetch lag for followers, `ReplicaFetcherThread` status.
5. Look for `UncleanLeaderElectionEnable` — if true, data loss risk.

**Mitigate:**
- Single broker down: wait for recovery (ISR will catch up), monitor `UnderReplicatedPartitions`.
- Broker not recovering: decommission gracefully (`kafka-leaves`), reassign partitions.
- ISR shrink but broker alive: check follower fetch lag, network, disk I/O on follower.
- Offline partitions: if unclean election enabled, accept data loss; else wait for ISR recovery.
- **Critical:** Never enable `unclean.leader.election.enable=true` for transactional/topics with `acks=all`.

## 6. Runbook: Controller Instability

**Symptoms:** Frequent controller elections (`ControllerEpoch` increment), `ControllerChangeRate` high, topic/partition operations timing out.

**Diagnose:**
1. Check ZooKeeper/KRaft health: latency, session expirations, quorum.
2. Controller logs: `ControllerEventThread` processing time, queue depth.
3. Look for metadata operations storm: topic create/delete, partition reassignment, config changes.
4. Check `ControllerChannelManager`: broker connection state, `RequestSendThread` errors.

**Mitigate:**
- ZK issues: fix ZK ensemble, increase `zookeeper.session.timeout.ms`.
- Metadata storm: rate-limit topic operations, batch partition reassignments.
- Controller overload: increase `controller.thread.pool.size`, optimize `ControllerEventProcessor`.
- KRaft: ensure quorum, check `controller.quorum.voters` config.

## 7. Runbook: Disk Pressure / Log Retention Issues

**Symptoms:** Disk usage > 85%, `LogDirFailureChannel` errors, broker shutdown, log cleaner can't keep up.

**Diagnose:**
1. Check per-topic disk usage: `kafka-log-dirs` tool, identify largest topics.
2. Check retention config: `retention.bytes`, `retention.ms`, `segment.bytes`.
3. Log cleaner: `cleaner.threads`, `cleaner.io.max.bytes.per.second`, compaction lag.
4. Look for segment rolling issues: `segment.ms`, `segment.bytes` too large/small.

**Mitigate:**
- Disk critical: increase `log.cleaner.io.max.bytes.per.second`, add disks, move partitions.
- Retention misconfig: adjust `retention.bytes` per topic, enable tiered storage if available.
- Compaction lag: increase cleaner threads, reduce `cleaner.min.compaction.lag.ms`.
- Emergency: delete old segments manually (last resort), increase `segment.bytes` to reduce file count.

## 8. Post-Incident Checklist

- [ ] Affected topics/partitions/consumer groups documented
- [ ] Data loss assessment: any unclean elections? acknowledged produces lost?
- [ ] Lag recovery time measured
- [ ] Root cause: broker config, client config, capacity, code, infrastructure
- [ ] Action items: partition count, replication factor, quota, monitoring, capacity
- [ ] Runbook updated for new failure modes

## 9. Key Dashboards & Alerts

| Dashboard | Purpose |
|---|---|
| Broker Golden Signals | Produce/fetch latency, error rate, request rate, byte rate |
| Cluster Health | Controller status, broker count, ISR status, offline partitions |
| Consumer Groups | Lag per group/topic, rebalance rate, consumer count |
| Topic Detail | Partition count, replication, ISR, leadership, disk usage |
| Disk & Log | Log dir usage, segment count, cleaner lag, retention |

## 10. Useful Commands

```bash
# Broker metrics (JMX)
jcmd <pid> JFR.dump name=1

# Consumer group lag
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group my-group --describe

# Topic partition details
kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic my-topic

# ISR / under-replicated partitions
kafka-topics.sh --bootstrap-server localhost:9092 --describe --under-replicated-partitions

# Controller status
kafka-metadata-quorum.sh --bootstrap-server localhost:9092 describe --status

# Log dir sizes
kafka-log-dirs.sh --bootstrap-server localhost:9092 --describe

# Preferred replica election (rebalance leadership)
kafka-leader-election.sh --bootstrap-server localhost:9092 --election-type PREFERRED --all-topic-partitions

# Alter topic config (retention, cleanup)
kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics --entity-name my-topic --alter --add-config retention.ms=604800000

# Producer throughput test
kafka-producer-perf-test.sh --topic test --num-records 1000000 --record-size 1000 --throughput 100000 --producer-props bootstrap.servers=localhost:9092
```