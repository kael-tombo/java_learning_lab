# THEORY — Slow Query & DB Deadlock Resolution (Incident Mechanics)

## 1. Incident in One Paragraph
Two failure modes share a page: slow queries that pin connections and inflate tail latency, and true DB deadlocks where Postgres aborts one transaction (`deadlock detected`). Both surface as checkout/order failures; slow queries burn gradually, deadlocks strike as error spikes after a schema or lock-order change.

## 2. Mechanics
### 2.1 Slow-query cascade
Missing index → seq scan → 8s query → pool slots pinned → app queue → timeouts. One bad plan at high QPS can saturate both app pool and DB CPU.

### 2.2 Planner surprises
Stale stats, parameter sniffing, or a deploy adding `WHERE lower(email)=...` (non-sargable) flips index→seq scan overnight. `EXPLAIN ANALYZE` shows actual vs planned rows.

### 2.3 DB deadlock cycle
Txn A locks row 1 then wants row 2; txn B locks row 2 then wants row 1. Postgres detects the wait-cycle and aborts one with `deadlock detected` — app must retry. Unlike JVM deadlock, DB resolves automatically but the loser fails.

### 2.4 Lock hierarchy
RowShare → RowExclusive → Share → Exclusive → AccessExclusive (DDL). Long `SELECT FOR UPDATE` + batch updates + migrations (index build, ALTER) collide and escalate waits.

### 2.5 Retry-storm amplifier
Naive immediate retry on deadlock/timeout re-collides. Jittered backoff + idempotency keys turn aborts into invisible blips.

## 3. Detection Signals
| Signal | Tool | Pattern |
|---|---|---|
| `pg_stat_statements` mean/max jump | Postgres, Datadog | one query digest dominates |
| `deadlock detected` + `Process ... waits for` | Postgres logs, `log_lock_waits=on` | true cycle, note victim + holders |
| `pg_locks` + `pg_stat_activity` blocked chain | SQL | waiter→holder→query mapping |
| App p99 tracks DB query p99 | APM traces | DB-bound proof |
| Deploy-correlated plan change | `auto_explain`, plan diff | new seq scan after release |

## 4. Alerts
- Query p99 > SLO (e.g., 500ms) per digest for 10m → warn.
- `deadlocks` rate >0 for 5m → warn; error-budget burn → page.
- `pg_stat_activity` max age >30s → warn (stuck txn/lock).

## 5. Triage Lifecycle
1. Identify digest: top by total_time in `pg_stat_statements`.
2. `EXPLAIN (ANALYZE, BUFFERS)` on canary/replica — never heavy ANALYZE on primary peak.
3. Mitigate: kill blocker, add index concurrently, shed traffic, statement timeout.
4. Deadlock: read Postgres detail (which tables/rows), fix update order + shorten txn.
5. Fix + prevent: index, order discipline, retry-with-backoff, lock-timeout.

## 6. Misdiagnoses
- Adding app replicas for a slow query — multiplies DB pressure.
- Retrying deadlocks instantly without ordering fix — guarantees repeat collisions.
- Running `ANALYZE`/DDL at peak — AccessExclusive blocks everything.

## 7. Interview Angle
Walk through `EXPLAIN` (seq scan vs index, rows misestimate), `FOR UPDATE` ordering, and idempotent retry design. Mention `CONCURRENTLY` index builds.

## 8. Takeaway
Slow query = plan + index + hold time; DB deadlock = inconsistent row-update order. Signal from `pg_stat_statements`/logs; fix order, shorten txns, retry smart.
