# RUNBOOK: Concurrency Incidents
## Lab 02 | On-Call Runbook | Production Engineering Academy

---

## RUNBOOK: Deadlock Detected / High BLOCKED Thread Count

**Severity**: P1 (Service unresponsive or severely degraded)

### Step 1: Confirm Deadlock (0-2 min)
```bash
# Capture thread dump
kubectl exec -it <pod> -- bash -c "jcmd 1 Thread.print" > /tmp/dump-$(date +%H%M).txt

# Check for deadlock automatically
grep -A10 "Found.*deadlock" /tmp/dump*.txt

# Count blocked threads (high = contention or deadlock)
grep "BLOCKED" /tmp/dump*.txt | wc -l
```

### Step 2: Identify the Hot Lock
```bash
# Find which lock has most waiters
grep "waiting to lock" /tmp/dump*.txt | grep -oP '<0x[0-9a-f]+>' | \
  sort | uniq -c | sort -rn | head -5

# Find who holds that lock
grep "locked <0x<THE_ADDRESS>" /tmp/dump*.txt -B5 | head -20
```

### Step 3: Immediate Mitigation
```bash
# Option A: Rolling restart (fastest)
kubectl rollout restart deployment/<service> -n <namespace>

# Option B: Scale up to add healthy instances while old ones restart
kubectl scale deployment/<service> --replicas=<current+2> -n <namespace>

# Option C: If single instance, restart the pod
kubectl delete pod <pod-name> -n <namespace>
```

### Step 4: Preserve Evidence for RCA
```bash
# Before restarting, take heap dump too
kubectl exec -it <pod> -- bash -c "jcmd 1 GC.heap_dump /tmp/heapdump.hprof"
kubectl cp <namespace>/<pod>:/tmp/heapdump.hprof ./heapdump-$(date +%Y%m%d-%H%M).hprof

# Save thread dump
kubectl cp <namespace>/<pod>:/tmp/dump-*.txt ./
```

### Step 5: Root Cause Investigation (post-incident)
```bash
# Find the deadlock cycle in thread dump
grep -A30 "deadlock" dump.txt

# Check if specific lock appears in multiple threads as both holder and waiter
# Use Eclipse MAT to visualize thread dump (File → Open Heap Dump → Thread Inspector)
```

---

## RUNBOOK: Thread Pool Exhaustion / Request Queue Backup

**Severity**: P1 (Requests queuing, latency spiking)

### Symptoms
```bash
# High queue depth in metrics
http_server_requests_seconds{quantile="0.99"} > 5.0

# Thread pool queue size growing
executor_queue_size{pool="main"} > 800

# Log pattern:
# RejectedExecutionException: Task rejected from ThreadPoolExecutor
```

### Step 1: Confirm Pool Exhaustion
```bash
# Check active vs max threads
jcmd 1 Thread.print | grep -c "State: RUNNABLE"

# Check if it's blocking on specific resource
jcmd 1 Thread.print | grep -A3 "BLOCKED\|WAITING" | head -50

# Check pool metrics via actuator
curl http://localhost:8080/actuator/metrics/executor.active
curl http://localhost:8080/actuator/metrics/executor.queued
```

### Step 2: Identify Cause of Blockage
- **DB connection exhaustion**: All threads waiting for DB → DB is slow or pool too small
- **Downstream service slow**: All threads waiting for HTTP call → upstream problem
- **CPU spike**: All threads competing for CPU → profiling needed

```bash
# For DB: check HikariCP
curl http://localhost:8080/actuator/metrics/hikaricp.connections.active
curl http://localhost:8080/actuator/metrics/hikaricp.connections.pending

# For downstream: check circuit breaker state
curl http://localhost:8080/actuator/health  # Check downstream dependencies
```

### Step 3: Mitigation
```bash
# Scale out immediately
kubectl scale deployment/<service> --replicas=<double> -n <namespace>

# If downstream is slow: temporarily increase timeout or enable circuit breaker
kubectl set env deployment/<service> DOWNSTREAM_TIMEOUT_MS=5000 -n <namespace>
kubectl rollout restart deployment/<service> -n <namespace>
```

---

## RUNBOOK: Race Condition — Data Corruption Suspected

**Severity**: P1 (Data integrity issue)

### Step 1: Assess Impact
```bash
# Check for symptoms of corruption (e.g., negative inventory, duplicate orders)
kubectl exec <db-pod> -- psql -c "SELECT COUNT(*) FROM inventory WHERE stock < 0"
kubectl exec <db-pod> -- psql -c "SELECT order_id, COUNT(*) FROM orders GROUP BY order_id HAVING COUNT(*) > 1"
```

### Step 2: Stop the Bleeding
```bash
# If actively corrupting data: take the affected service offline
kubectl scale deployment/<service> --replicas=0 -n <namespace>

# Or: enable feature flag to disable the problematic feature
curl -X POST http://service/admin/features/flash-sale?enabled=false
```

### Step 3: Data Recovery
```bash
# Identify corrupted records
# Fix data manually (with DBA) using corrective SQL
# Document every change in incident report
```

### Step 4: Fix in Code
```bash
# Typical fixes:
# - HashMap → ConcurrentHashMap
# - i++ → AtomicInteger.incrementAndGet()
# - if (exists) then insert → UPSERT / INSERT ON CONFLICT
# - Java-level check → Database-level constraint + optimistic locking
```

---

## Monitoring Thresholds for Concurrency

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Thread BLOCKED count | > 50 | > 200 | Thread dump, investigate lock |
| Thread pool queue size | > 70% | > 90% | Scale out |
| RejectedExecutionCount growth | > 0 | > 10/min | P1 incident |
| VT pinned thread warnings | > 10/min | > 100/min | Fix synchronized+I/O |
| Deadlock detected | Any | — | P1 immediate restart |
