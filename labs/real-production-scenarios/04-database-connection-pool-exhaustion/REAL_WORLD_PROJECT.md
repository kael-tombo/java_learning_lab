# REAL_WORLD_PROJECT — War Room: Checkout Timeouts, DB Healthy

## 1. Scenario
Checkout (Java 17, 20 pods × Hikari max 20 = 400 potential conns, Postgres max 100) times out at lunch peak. DB CPU 30%, but app logs scream pool timeouts. New promo code path shipped yesterday. You lead.

## 2. Timeline
| T | Event |
|---|---|
| T+0 | Page: pool-timeout rate + p99 cliff at 10s (= connectionTimeout) |
| T+5m | DB cleared: `pg_stat_activity` 40 conns, mostly idle — app-side starvation |
| T+8m | Pool metrics: active 20/20 all pods, pending 50+; leak warnings point to `PromoDao:77` |
| T+12m | Code: early-return path skips `close()`; plus promo query missing index (8s hold) |
| T+15m | Mitigate: restart half fleet, kill 8s queries, shed promo traffic via flag |
| T+40m | Hotfix: try-with-resources + index on `promo(code)` + statement_timeout 3s; canary |
| T+75m | Rollout, pending 0, p99 400ms; resize pool 20→6/pod (fleet 120→ within budget w/ PgBouncer plan) |
| T+24h | Postmortem + soak test + sizing CI check |

## 3. Runbook
```bash
curl -s api:8080/actuator/metrics/hikaricp.connections.active
curl -s api:8080/actuator/metrics/hikaricp.connections.pending
grep -i "not available\|leak detection" /logs/app.log | tail -20
kubectl exec deploy/checkout -- jstack -l 1 | grep -c getConnection
psql -c "SELECT pid,state,now()-query_start AS age,left(query,120) FROM pg_stat_activity ORDER BY age DESC LIMIT 10;"
psql -c "SELECT pg_terminate_backend(<blocker-pid>);"  # surgical only
kubectl rollout restart deploy/checkout  # reclaim leaked slots
```

## 4. Metrics
- Per-pod active/idle/pending vs max; timeout rate; leak-warning rate.
- DB conns vs max, `pg_stat_statements` mean time, checkout p99/goodput.
- Success: pending 0, active <70% max, p99 < SLO 1h.

## 5. Log Snippets
```
SQLTransientConnectionException: Connection is not available, request timed out after 10000ms
Connection leak detection triggered for connection... at com.shop.PromoDao.findById(PromoDao.java:77)
-- pg: 3 backends age>8s state=active query=SELECT ... FROM promo WHERE code=...
```

## 6. Prevention
try-with-resources lint, leak detection always on, query SLO + index review, fleet-sizing gate (Σ pools < 0.8×DB max), PgBouncer rollout, statement timeouts, soak asserting pool recovery.

## 7. Postmortem Outline
Impact (checkout failures 35m), gap (no pending alert, no sizing check), cause (leak + slow query + oversubscription), fix, 5 Whys, owners/dates.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- HikariCP configuration / leak detection: https://github.com/brettwooldridge/HikariCP
- PostgreSQL `pg_stat_activity` monitoring: https://www.postgresql.org/docs/current/monitoring-stats.html
- PostgreSQL connection handling / pooling guidance: https://www.postgresql.org/docs/current/runtime-config-connection.html
