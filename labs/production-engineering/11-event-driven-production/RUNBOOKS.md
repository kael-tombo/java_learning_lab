# RUNBOOK: Kafka Incidents & Consumer Lag Triage
## Lab 11 | Production Engineering Academy

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
