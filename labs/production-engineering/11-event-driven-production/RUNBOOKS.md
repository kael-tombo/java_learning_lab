# RUNBOOK: Kafka Incidents & Consumer Lag Triage
## Lab 11 | Production Engineering Academy — Top 0.0001% Engineering

---

## RUNBOOK 01: Severe Consumer Lag Spikes

**Severity**: P1 / P2
**Symptom**: Consumer lag on critical topics (e.g., `orders`) exceeds 500,000 messages and is growing.

### Step 1: Identify Lag Shape
```bash
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group order-processing-v2
```
| Lag Shape | Root Cause |
|---|---|
| Concentrated on ONE partition | Poison pill or hot partition key |
| Growing EVENLY across all partitions | Consumer throughput < producer ingress rate |
| Lag stuck at exactly one offset for > 5 min | Infinite retry loop (non-retryable exception) |

### Step 2A: Lag Growing Evenly — Scale Consumers
```bash
# Max useful replicas = number of topic partitions
kubectl scale deployment/order-consumer --replicas=30

# Or increase per-pod concurrency (up to partition count / pod count)
# In ConcurrentKafkaListenerContainerFactory:
factory.setConcurrency(8);
```

### Step 2B: Single Partition Stuck — Poison Pill
```bash
# Inspect the stuck record
kafka-console-consumer.sh --bootstrap-server kafka:9092 \
  --topic orders --partition <P> --offset <stuck_offset> --max-messages 1

# If non-parseable: advance offset past the poison pill
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group order-processing-v2 \
  --topic orders:<P> \
  --reset-offsets --to-offset <stuck_offset+1> --execute
```
> **Before advancing**: Save the raw bytes of the poison pill to S3 for post-mortem:
> ```bash
> kafka-console-consumer.sh ... --max-messages 1 > /tmp/poison_pill_$(date +%s).bin
> aws s3 cp /tmp/poison_pill_*.bin s3://your-incident-bucket/
> ```

### Step 3: Verify Recovery
```bash
# Watch lag drain in real time (poll every 5 seconds)
watch -n 5 'kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group order-processing-v2 | grep "orders"'
```

---

## RUNBOOK 02: Under-Replicated Partitions (URP)

**Severity**: P1
**Symptom**: `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` gauge > 0 in Prometheus.

### Step 1: Identify Affected Partitions
```bash
kafka-topics.sh --bootstrap-server kafka:9092 \
  --describe --under-replicated-partitions
```

### Step 2: Diagnose the Lagging Follower
```bash
# Check broker disk utilization — disk full causes follower to stop fetching
for broker in kafka-0 kafka-1 kafka-2; do
  echo "=== $broker ===" && kubectl exec $broker -- df -h /var/kafka/data
done

# Check JVM heap on lagging broker
kubectl exec kafka-1 -- jcmd 1 VM.native_memory | grep Heap
```

**Common causes and fixes**:

| Symptom | Cause | Fix |
|---|---|---|
| Disk 90%+ on one broker | Log retention not configured | `log.retention.bytes=107374182400` (100GB) |
| Follower fetch lag > 30s | Broker GC pause (Old Gen full) | Tune heap: `-Xmx6g -XX:+UseG1GC` |
| Follower fetch lag after restart | ISR shrink during rolling restart | Set `min.insync.replicas=1` during maintenance |
| Network packet loss between brokers | NIC or switch issue | Check `ifconfig` → dropped packets; escalate to infra |

### Step 3: Force Leader Re-election After Broker Recovery
```bash
kafka-leader-election.sh --bootstrap-server kafka:9092 \
  --election-type PREFERRED --all-topic-partitions
```

---

## RUNBOOK 03: Debezium Replication Slot WAL Bloat — DB Disk Emergency

**Severity**: P1
**Symptom**: PostgreSQL disk usage growing > 1 GB/hour. `pg_replication_slots` shows high `lag`.

### Step 1: Check Replication Slot Lag
```sql
-- Run on PostgreSQL primary
SELECT slot_name,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS wal_lag,
       active
FROM pg_replication_slots
WHERE slot_name = 'debezium_outbox_slot';
```
If `wal_lag > 5 GB` and `active = false`: Debezium connector is down.

### Step 2: Restart Debezium Connector
```bash
# Via Kafka Connect REST API
curl -X POST http://kafka-connect:8083/connectors/outbox-connector/restart

# Check connector status
curl http://kafka-connect:8083/connectors/outbox-connector/status | jq .
```

### Step 3: If Disk > 85% — Emergency Slot Drop
> **WARNING**: Dropping the slot means Debezium must re-snapshot the table on restart.
> All in-flight events already in Kafka will be re-published — downstream consumers
> MUST be idempotent before performing this step.
```sql
-- EMERGENCY ONLY — drops all held WAL segments immediately
SELECT pg_drop_replication_slot('debezium_outbox_slot');
```
Then recreate the slot and trigger a Debezium snapshot:
```json
{ "snapshot.mode": "initial" }
```

### Step 4: Prevention (Prometheus Alert)
```yaml
# alert.rules.yaml
- alert: DebeziumWALLagHigh
  expr: pg_replication_slots_pg_wal_lsn_diff_bytes{slot_name="debezium_outbox_slot"} > 5368709120
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Debezium WAL lag > 5GB — risk of DB disk exhaustion"
```

---

## RUNBOOK 04: Consumer Group Stuck in REBALANCING State

**Severity**: P2
**Symptom**: All consumers paused. Consumer group state = `PreparingRebalance` for > 2 minutes.

### Step 1: Identify the Cause
```bash
# List consumer group details — look for "REBALANCING" state
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group order-processing-v2 --state
```

### Step 2: Find the Problematic Member
The rebalance is usually stuck waiting for one slow consumer to complete `onPartitionsRevoked()`.

```bash
# Check pod logs for the consumer group members
kubectl logs -l app=order-consumer --since=5m | grep -E "REBALANCE|revok|assign"

# If a pod is OOMKilled mid-rebalance, Kubernetes may restart it before it sends
# the LeaveGroup request, causing the coordinator to wait until session.timeout.ms expires
kubectl get pods -l app=order-consumer | grep -v Running
```

### Step 3: Force Group Re-election
If the group is stuck permanently (coordinator thinks a dead member is still active):
```bash
# Check session timeout — coordinator waits this long before evicting dead member
# Default: 45000ms (45s). In production, set to 10s for faster failure detection:
props.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, 10_000);
props.put(ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, 3_000); # Must be < session timeout / 3
```

### Step 4: Emergency — Delete the Consumer Group (Last Resort)
```bash
# Only if all consumers are stopped
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --delete --group order-processing-v2
# Restart consumers — group re-creates from `auto.offset.reset` or last committed offset
```

---

## RUNBOOK 05: Kafka Broker JVM OOM / High GC Pause

**Severity**: P1
**Symptom**: Broker GC pause > 5s, `java.lang.OutOfMemoryError` in broker logs, ISR shrink.

### Step 1: Capture Heap Dump Before Broker Dies
```bash
# On the broker pod (run IMMEDIATELY when GC pause alert fires)
kubectl exec kafka-1 -- jmap -dump:format=b,file=/tmp/heap.hprof 1
kubectl cp kafka-1:/tmp/heap.hprof ./kafka-broker-heap-$(date +%s).hprof
```

### Step 2: Analyze with Eclipse MAT or jhat
Common cause: `FetchRequestMetadata` objects accumulating when consumers fetch large batches
without `fetch.max.bytes` limit, causing 100s of MB per request held in broker memory.

### Step 3: Tune Broker JVM
```bash
# /opt/kafka/config/jvm.options
-Xmx6g
-Xms6g                         # Equal Xmx/Xms prevents heap resize GC
-XX:+UseG1GC
-XX:MaxGCPauseMillis=20        # Target 20ms max GC pause
-XX:G1HeapRegionSize=16m       # Large regions for Kafka's big allocation bursts
-XX:+ExplicitGCInvokesConcurrent
```

### Step 4: Tune Consumer Fetch Limits
```bash
# Prevent consumers from requesting enormous batches
fetch.max.bytes=52428800       # 50MB per fetch request (default is 50MB, verify)
max.partition.fetch.bytes=1048576  # 1MB per partition per fetch
```

---

## RUNBOOK 06: Disruptor Ring Buffer Full — Kafka Consumer Blocked

**Severity**: P2
**Symptom**: Kafka consumer thread blocked on `ringBuffer.next()`. Consumer lag growing.
No GC, no CPU spike — just frozen throughput.

### Step 1: Confirm Ring Buffer is Full
```bash
# Add a RingBuffer.remainingCapacity() metric via Micrometer:
Gauge.builder("disruptor.ring.buffer.remaining", ringBuffer, RingBuffer::remainingCapacity)
     .register(meterRegistry);

# Check in Grafana — if remainingCapacity == 0 for > 30s, buffer is full
```

### Step 2: Identify Why the Consumer Thread is Slow
```bash
# Take a thread dump of the disruptor-consumer thread
jcmd <PID> Thread.print | grep -A 20 "disruptor-consumer"

# Common causes:
# - onEvent() calling a blocking DB write that took too long
# - GC pause on the consumer thread's alloc path (remove allocations from hot path)
# - CPU core preempted by OS (add isolcpus= to kernel boot params)
```

### Step 3: Emergency — Drain and Skip (Never in Financial Systems)
```java
// If downstream is permanently unavailable, advance cursor to drain the buffer
// WARNING: THIS DROPS EVENTS — only for non-critical analytics pipelines
disruptor.halt();  // Signal consumers to stop
// Manually publish to flush — then restart with a larger buffer size
```

### Step 4: Permanent Fix — Right-Size the Buffer
```java
// Buffer must absorb: consumer_slowdown_duration × producer_events_per_second
// Example: Consumer slows for 500ms at 100,000 events/sec
// Required buffer: 0.5s × 100,000 = 50,000 → round up to 65,536
int BUFFER_SIZE = 65536; // Always power of 2
```


---

## RUNBOOK 01: Severe Consumer Lag Spikes

**Severity**: P1 / P2  
**Symptom**: Consumer lag on critical topics (e.g. `orders`) exceeds 500,000 messages and is growing monotonically.

### Step 1: Check Consumer Group Lag & Partition Distribution
```bash
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group order-processing-v2
```
Look for:
- Is lag concentrated on **one single partition**? (Indicates a poison pill or hot partition key).
- Is lag growing evenly across **all partitions**? (Indicates consumer throughput is lower than producer ingress).

### Step 2: Immediate Mitigation Options
- **If lag is on all partitions**:
  1. Check if pod count equals partition count:
     If topic has 30 partitions and service has only 10 pods, scale consumers:
     ```bash
     kubectl scale deployment/order-consumer --replicas=30
     ```
     *(Note: Scaling beyond the number of partitions gives idle pods with 0 partitions).*
  2. Increase consumer concurrency per pod (`factory.setConcurrency(8)`).
- **If lag is stuck on one partition (Poison Pill)**:
  1. Inspect the stuck record offset:
     ```bash
     kafka-console-consumer.sh --bootstrap-server kafka:9092 \
       --topic orders --partition <p> --offset <stuck_offset> --max-messages 1
     ```
  2. If non-critical, manually advance consumer group offset past the poison pill:
     ```bash
     kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
       --group order-processing-v2 --topic orders:<p> \
       --reset-offsets --to-offset <stuck_offset + 1> --execute
     ```

---

## RUNBOOK 02: Under-Replicated Partitions (URP) on Brokers
1. Check Kafka broker cluster state:
   ```bash
   kafka-topics.sh --bootstrap-server kafka:9092 --describe --under-replicated-partitions
   ```
2. Check disk utilization on all brokers (`df -h`). If a broker disk hits 100%, Kafka shuts down partition writes to prevent log corruption.
