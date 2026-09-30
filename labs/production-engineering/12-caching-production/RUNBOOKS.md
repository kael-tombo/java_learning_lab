# RUNBOOK: Production Redis Incidents & Cache Triage
## Lab 12 | Production Engineering Academy — Top 0.0001% Engineering

---

## RUNBOOK 01: Redis Memory Exhaustion (OOM & Eviction Cascade)

**Severity**: P1 / High  
**Trigger**: Alert `RedisUsedMemoryPct > 90%` or Application error `OOM command not allowed when used memory > 'maxmemory'`.

### Phase 1: Rapid Telemetry Assessment (< 2 minutes)
Execute on the affected primary Redis node:
```bash
redis-cli -h redis-primary.prod.internal -p 6379 INFO memory
```
Evaluate key diagnostic indicators:
- `used_memory_human`: Actual bytes allocated for keys, values, and internal overhead.
- `used_memory_rss_human`: Resident Set Size allocated from the Linux OS.
- `mem_fragmentation_ratio`: 
  - $1.0 - 1.5$: Healthy.
  - $> 1.8$: Severe OS fragmentation.
  - $< 1.0$: Redis is swapping to disk (CRITICAL: instant latency collapse).
- `evicted_keys`: Rate of keys dropped per second. If $> 1,000/\text{sec}$, cluster is evicting warm data prematurely.
- `mem_allocator`: jemalloc version in use.

---

### Phase 2: Identify High-Memory Culprits & Big Keys
Do **NOT** use `KEYS *` or run ad-hoc scripts. Use Redis's built-in non-blocking pipelined scanner:
```bash
# Scan for biggest keys by data type without blocking the event loop
redis-cli -h redis-primary.prod.internal --bigkeys

# Sample top 100 memory-consuming keys in keyspace
redis-cli -h redis-primary.prod.internal --memkeys

# Check precise byte footprint of a suspect key
redis-cli -h redis-primary.prod.internal MEMORY USAGE "tenant:9948:audit_log" SAMPLES 10
```

---

### Phase 3: Immediate Emergency Stabilization
1. **Temporarily Bump `maxmemory`** (if host RAM has available headroom):
   ```bash
   redis-cli -h redis-primary.prod.internal CONFIG SET maxmemory 28gb
   ```
2. **Reclaim Memory Safely (NEVER use `DEL` on Big Keys)**:
   - `DEL` on a key containing 5,000,000 hash fields blocks the single Redis thread for 4 to 8 seconds.
   - Use non-blocking asynchronous `UNLINK`:
   ```bash
   redis-cli -h redis-primary.prod.internal UNLINK "tenant:9948:audit_log"
   ```
3. **Trigger Active Defragmentation if Fragmentation $> 1.8$**:
   ```bash
   redis-cli -h redis-primary.prod.internal CONFIG SET activedefrag yes
   redis-cli -h redis-primary.prod.internal CONFIG SET active-defrag-cycle-max 50
   ```
4. **Change Eviction Policy to Evict Stale Keys Aggressively**:
   ```bash
   redis-cli -h redis-primary.prod.internal CONFIG SET maxmemory-policy allkeys-lfu
   ```

---

## RUNBOOK 02: Redis Single-Thread CPU 100% & Event-Loop Freeze

**Severity**: P1 / Critical  
**Trigger**: Alert `RedisCPUUtilization > 95%` or `LettuceRedisTimeoutException`.

### Phase 1: Inspect In-Flight & Slow Commands
Redis single-threaded command execution means a single slow command blocks all subsequent requests in the FIFO queue.
```bash
# Fetch last 25 commands taking longer than slowlog-log-slower-than threshold
redis-cli -h redis-primary.prod.internal SLOWLOG GET 25

# Inspect currently executing command and connected client stats
redis-cli -h redis-primary.prod.internal CLIENT LIST | tr ' ' '\n' | grep -E '(cmd=|addr=|oll=|omem=)'
```

#### Diagnostic Decision Matrix:
| Slowlog / Client List Output | Root Cause | Immediate Action |
|---|---|---|
| `cmd=keys` | Developer/Script executing `KEYS *` | Kill client connection (`CLIENT KILL ID <id>`) |
| `cmd=smembers` or `cmd=hgetall` | O(N) extraction of large collection | Replace with `SSCAN` / `HSCAN` in code; `UNLINK` key |
| `cmd=eval` / `cmd=evalsha` | Runaway infinite loop in Lua script | Execute `SCRIPT KILL` (or `SHUTDOWN NOSAVE` if script wrote) |
| `omem > 100mb` (Output Buffer) | Slow client consuming massive payload | Kill rogue consumer pod with `CLIENT KILL IP:PORT` |

---

### Phase 2: Resolving a Frozen Lua Script
If a Lua script is stuck in an infinite loop:
```bash
# Attempt to terminate cleanly (only works if script has NOT performed a write)
redis-cli -h redis-primary.prod.internal SCRIPT KILL

# If script executed writes, Redis refuses SCRIPT KILL to prevent state corruption:
# Last resort: Force restart without saving corrupted memory state
redis-cli -h redis-primary.prod.internal SHUTDOWN NOSAVE
```

---

## RUNBOOK 03: Redis Cluster Partition & Redirection Storms

**Severity**: P1  
**Trigger**: Application logs flooded with `RedisMovedException` or `ClusterCommandExecutionException: Exhausted retries`.

### Phase 1: Validate Cluster Topology & Hash Slot Allocation
```bash
# Check cluster state and fail flag
redis-cli -h redis-node-01.prod.internal -p 6379 CLUSTER INFO

# Inspect all nodes, master/replica roles, and assigned slot ranges
redis-cli -h redis-node-01.prod.internal -p 6379 CLUSTER NODES
```
Look for:
- `cluster_state:fail` (Slots are unassigned or master quorum is lost).
- `fail` or `fail?` flags on any master node.
- Uncovered slots (must sum to exactly 16,384 slots).

---

### Phase 2: Identify Uncovered Slots & Force Recovery
If a master failed and its replica was unable to auto-promote:
```bash
# Check for uncovered slots across the cluster
redis-cli --cluster check redis-node-01.prod.internal:6379

# If a master is permanently dead and replica must force takeover:
# SSH to the surviving replica node and run:
redis-cli -p 6379 CLUSTER FAILOVER TAKEOVER
```

### Phase 3: Force Reconnect on Java Application Pods
If Lettuce client topology cache drifts and continues sending requests to decommissioned IPs:
```bash
# Restart application deployments in rolling fashion to force Netty topology rebuild
kubectl rollout restart deployment/order-service-api -n production
```

---

## RUNBOOK 04: Thundering Herd / Cache Stampede Triage

**Severity**: P2 / Elevated  
**Trigger**: Persistent Database CPU spikes to 100% following an entity update or cache TTL expiry.

### Phase 1: Isolate the Expired / Hot Key
```bash
# Sample access frequency across active keys
redis-cli -h redis-primary.prod.internal --hotkeys
```
Identify the single key receiving $> 10,000$ calls/min.

### Phase 2: Hot-Fixing the Herd
1. **Pre-warm the Key with Long TTL Directly via CLI**:
   Query the DB once manually and force-set the key with a 2-hour TTL:
   ```bash
   redis-cli -h redis-primary.prod.internal SET "product:flash_deal:104" '{"id":104,"price":19.99}' EX 7200
   ```
2. **Apply Cloudflare / Envoy Rate Limit**:
   Enact an edge rate-limit rule on the specific URL endpoint returning that product to throttle incoming requests to 200 RPS until the database connection pool recovers.

---

## RUNBOOK 05: Replication Lag & Backlog Buffer Overflow

**Severity**: P2  
**Trigger**: Alert `RedisReplicationLag > 10MB` or `ReplicationDisconnected`.

### Phase 1: Check Replication Status
```bash
redis-cli -h redis-primary.prod.internal INFO replication
```
Calculate byte lag:
$$\text{Replication Lag (Bytes)} = \text{master\_repl\_offset} - \text{slave0:offset}$$

### Phase 2: Preventing Full Resynchronization (`PSYNC`) Storms
If replication lag exceeds `repl-backlog-size`, the replica cannot perform an incremental sync and falls back to a **Full Resync (Diskless RDB snapshot)**, which consumes massive network bandwidth and CPU.

1. **Dynamically Double the Backlog Buffer Size on Master**:
   ```bash
   redis-cli -h redis-primary.prod.internal CONFIG SET repl-backlog-size 1073741824 # 1GB
   ```
2. **Increase Client Output Buffer Limit for Replicas**:
   ```bash
   redis-cli -h redis-primary.prod.internal CONFIG SET client-output-buffer-limit "replica 2147483648 1073741824 300"
   ```
3. **Verify Replica Reconnection**:
   ```bash
   redis-cli -h redis-replica-01.prod.internal INFO replication
   # Check role:slave, master_link_status:up
   ```
