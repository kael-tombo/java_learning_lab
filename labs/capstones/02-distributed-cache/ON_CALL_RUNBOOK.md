# On-Call Runbook: Distributed Cache (Capstone 02)

> Scope: `CacheCluster` (multi-node), `CacheClient` (embedded in services), `CacheProxy` (sidecar), `InvalidationBus`, `WarmupCoordinator`.
> Audience: on-call engineer for a team running this Java distributed cache in production.

## 1. Service Map & SLOs

| Component | SLO | Key Signal |
|---|---|---|
| `CacheCluster.get/put` | p99 latency < 5 ms (local), < 20 ms (remote), error rate < 0.01% | Client-side latency histogram, error rate |
| Hit ratio | > 95% (hot tier), > 80% (warm tier) | `CacheMetrics.hitRatio` per tier |
| Invalidation propagation | p99 < 500 ms end-to-end | `InvalidationBus` lag metric |
| Warmup completion | < 10 min for full cluster | `WarmupCoordinator` progress |
| Node recovery | < 2 min for single node | `CacheCluster` membership events |

## 2. Triage Decision Tree (first 5 minutes)

```
cache latency spike or errors?
├─ YES → §3 Cache Latency / Error Spike
├─ NO → hit ratio dropped?
│   ├─ YES → §4 Hit Ratio Degradation
│   └─ NO → data inconsistency reported?
│       ├─ YES → §5 Cache Inconsistency
│       └─ NO → node down / cluster unstable?
│           ├─ YES → §6 Node Failure / Cluster Instability
│           └─ NO → warmup stuck? → §7
```

Always note: affected cache tier (L1/L2), key patterns, recent config changes, deployment history.

## 3. Runbook: Cache Latency / Error Spike

**Symptoms:** Client p99 > 50 ms, `TimeoutException`, `CacheUnavailableException`, circuit breakers OPEN.

**Diagnose (0–10 min):**
1. Check cluster membership: all nodes healthy? `CacheCluster.getMembers()` shows expected count?
2. Check node metrics: CPU, GC pauses, heap usage, network I/O, disk I/O (if persisted).
3. Check client-side: connection pool exhaustion, retries storm, circuit breaker state.
4. Look for hot keys: single key driving disproportionate traffic (skew detection).
5. Check `InvalidationBus` backlog — invalidation storm can block eviction thread.

**Mitigate (10–20 min):**
- Hot key detected: enable local L1 caching for that key pattern, increase TTL, add request coalescing.
- Node GC pressure: trigger rolling restart of affected node(s), increase heap if persistent.
- Connection pool exhausted: increase client pool size, reduce timeout to fail fast.
- Invalidation backlog: pause non-critical invalidations, increase consumer parallelism.
- **Do NOT:** disable cache entirely (causes thundering herd), flush cluster (cold start), increase timeouts blindly.

## 4. Runbook: Hit Ratio Degradation

**Symptoms:** Hit ratio alert firing, increased backend load (DB/upstream), latency creep.

**Diagnose:**
1. Identify tier: L1 (client) vs L2 (cluster) hit ratio drop.
2. Check TTL distribution: are hot keys expiring simultaneously? (TTL synchronization).
3. Verify `WarmupCoordinator` completed successfully after last deploy/restart.
4. Look for cache bypass patterns: `Cache-Control: no-cache`, feature flag disabling cache.
5. Check eviction policy: LRU/LFU evicting hot keys due to memory pressure.

**Mitigate:**
- TTL sync: add jitter to TTL (TTL ± 10%), stagger refresh.
- Warmup incomplete: trigger manual warmup for affected keys, prioritize top-K.
- Memory pressure: increase max memory, adjust eviction policy, offload cold keys to disk tier.
- Bypass traffic: audit feature flags, ensure cache-aside pattern is followed.

## 5. Runbook: Cache Inconsistency (Stale Reads)

**Symptoms:** Application reads stale data, business logic errors, reconciliation mismatches.

**Diagnose:**
1. Verify invalidation path: `InvalidationBus` → `CacheCluster` → `CacheClient` L1 invalidation.
2. Check for split-brain: network partition causing dual-primary in cluster.
3. Verify write path: `CacheClient.put` → `CacheProxy` → `CacheCluster` → `InvalidationBus` publish.
4. Look for version vector conflicts or last-write-wins anomalies.
5. Check client-side L1 TTL vs invalidation delivery latency.

**Mitigate:**
- Invalidation lag: force cluster-wide invalidation for affected key pattern, verify delivery.
- Split-brain: trigger cluster reformation, ensure quorum, demote minority partition.
- Version conflict: implement read-repair on mismatch, log for analysis.
- L1 stale: reduce L1 TTL, enable synchronous invalidation ack for critical keys.

## 6. Runbook: Node Failure / Cluster Instability

**Symptoms:** Node marked UNREACHABLE, partition ownership changes, rebalance storms, membership flapping.

**Diagnose:**
1. Check node health: OOM, disk full, network partition, GC pause > 30s.
2. Review cluster logs: `MergeView`, `Suspect` events, `Leave`/`Join` storms.
3. Check partition ownership: any partitions without primary/backup?
4. Verify persistence: WAL / snapshot intact on failed node.

**Mitigate:**
- Single node down: wait for auto-recovery (2 min), verify backup promotion.
- Multiple nodes: pause deployments, ensure quorum, manual rebalance if stuck.
- Rebalance storm: throttle rebalance bandwidth, limit concurrent moves.
- Persistence corruption: rebuild node from scratch, rejoin as new member.

## 7. Runbook: Warmup Stuck / Incomplete

**Symptoms:** `WarmupCoordinator` progress < 100% after 15 min, hit ratio low on new nodes.

**Diagnose:**
1. Check warmup source: upstream service availability, query latency.
2. Look for warmup task failures: `WarmupTaskException` in logs.
3. Verify partition assignment: warmup tasks distributed across nodes?
4. Check for backpressure: warmup overwhelming cluster capacity.

**Mitigate:**
- Upstream slow: throttle warmup rate, increase timeout, prioritize hot keys.
- Task failures: retry with exponential backoff, skip poison keys, alert on repeated failures.
- Backpressure: pause warmup, let cluster stabilize, resume at lower rate.

## 8. Post-Incident Checklist

- [ ] Affected keys / key patterns documented
- [ ] Hit ratio impact quantified (before/during/after)
- [ ] Backend load spike correlated (DB CPU, upstream latency)
- [ ] Root cause: config, code, capacity, or external dependency
- [ ] Action items: TTL jitter, warmup priority, circuit breaker tuning, capacity
- [ ] Runbook updated if new failure mode discovered

## 9. Key Dashboards & Alerts

| Dashboard | Purpose |
|---|---|
| Cache Golden Signals | Hit ratio, latency (p50/p95/p99), error rate, throughput |
| Cluster Topology | Node health, partition distribution, rebalance status |
| Invalidation Pipeline | Bus lag, delivery latency, failure rate |
| Warmup Progress | Completion %, rate, failures, ETA |
| Client-Side Metrics | Local hit ratio, circuit breaker state, pool usage |

## 10. Useful Commands

```bash
# Cluster membership & health
curl -s localhost:8080/actuator/cache/cluster/members

# Hit ratio per tier
curl -s localhost:8080/actuator/cache/metrics/hitRatio

# Hot keys (top 20 by access count)
curl -s localhost:8080/actuator/cache/hotkeys?limit=20

# Invalidation bus lag
curl -s localhost:8080/actuator/invalidation/lag

# Trigger manual warmup for key pattern
curl -X POST localhost:8080/actuator/cache/warmup -d '{"pattern": "user:*"}'

# Force invalidation for key
curl -X POST localhost:8080/actuator/cache/invalidate -d '{"key": "product:123"}'

# Check partition ownership
curl -s localhost:8080/actuator/cache/partitions
```