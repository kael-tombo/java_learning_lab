# THEORY — Database Connection Pool Exhaustion (Incident Mechanics)

## 1. Incident in One Paragraph
The app runs out of DB connections: all pool slots are checked out and new requests wait until timeout. Threads pile up behind `HikariPool.getConnection`, latency explodes, and the service looks "down" while the database itself is healthy. Root causes are leaks (unclosed connections), too-small pools, or slow queries holding connections hostage.

## 2. Mechanics
### 2.1 Pool anatomy
Fixed pool (e.g., HikariCP max 20): checkout → use → close (return). `connectionTimeout` (wait for slot), `maxLifetime`, `idleTimeout`, `leakDetectionThreshold` govern behavior.

### 2.2 Leak path
Missing `close()` in a branch (exception skips close) permanently removes a slot until restart. Ten slow leaks per hour empty a 20-pool in 2 hours — classic slow-burn.

### 2.3 Hold-time path
Slow query (30s) × 20 concurrent requests = entire pool pinned. Pool exhaustion is often a symptom of query latency, not pool size.

### 2.4 Pool-to-DB mismatch
App pools × replicas can overwhelm Postgres `max_connections` (e.g., 20×30 pods=600 > 100). Then DB rejects, failover cascades. Size app pools against DB capacity with headroom.

### 2.5 Queue cascade
Waiters hold Tomcat threads while waiting for connections → Tomcat pool exhausts next → health checks fail → restarts that don't help because the leak persists.

## 3. Detection Signals
| Signal | Tool | Pattern |
|---|---|---|
| `hikaricp_connections_active ≈ max` + pending threads | Micrometer/JMX | saturated + growing `pending` |
| `Connection is not available, request timed out` | app logs | pool-timeout signature |
| `leak detection` warnings with stack traces | Hikari `leakDetectionThreshold` | pinpoints unclosed site |
| DB `pg_stat_activity` count ≪ app demand | `SELECT count(*) ...` | app-side starvation, DB fine |
| p99 → `connectionTimeout` value (e.g., 30s cliff) | APM | wait-time plateau = pool wait |

## 4. Alerts
- Active/max >90% for 10m → warn; pending threads >0 for 5m → page.
- Log alert on pool-timeout exception → page.
- DB connections >80% of `max_connections` → warn (fleet-level).

## 5. Triage Lifecycle
1. Scope: one service or all sharing DB? Check deploy + slow-query dashboard.
2. Evidence: pool metrics, `pg_stat_activity`, leak-detection stacks.
3. Mitigate: restart (reclaims leaked slots), shed traffic, kill long-running query, temporarily raise pool (carefully).
4. Root-cause: unclosed path vs slow query vs under-size.
5. Fix: try-with-resources, query index, correct sizing + PgBouncer if needed.

## 6. Misdiagnoses
- Raising pool size blindly — multiplies DB load and hides the leak.
- Blaming DB CPU — DB idle while app waits proves app-side starvation.
- Restart-only culture — leaked slots return but leak re-grows; slope matters.

## 7. Interview Angle
Explain pool sizing formula (connections ≈ ((core_count×2)+spindles)), `leakDetectionThreshold` use, and how to distinguish leak (active grows with flat traffic) from slowness (active tracks query p99).

## 8. Takeaway
Pool exhaustion = slots not returning. Signal is active≈max + pending; proof is leak stacks or `pg_stat_activity`; fix is close discipline + fast queries + right sizing.
