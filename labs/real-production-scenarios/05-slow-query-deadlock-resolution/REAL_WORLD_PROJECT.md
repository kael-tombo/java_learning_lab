# REAL_WORLD_PROJECT — War Room: Flash-Sale Checkout Deadlocks + Slow Promo Lookup

## 1. Scenario
Flash sale: checkout error rate 8% with `deadlock detected` spikes plus p99 6s on promo lookup. Java 17 + Postgres 15, 24 pods. Promo feature shipped yesterday with `WHERE lower(code)=...` and transfer writes in request order. You lead the war room.

## 2. Timeline
| T | Event |
|---|---|
| T+0 | Page: error-budget burn + deadlock rate + p99 breach |
| T+5m | Split causes: digest table shows promo lookup 70% DB time; logs show acct-row deadlock cycle |
| T+10m | EXPLAIN (replica): Seq Scan 2M promo rows — non-sargable `lower(code)` |
| T+12m | Lock chain: concurrent transfers update (A,B) vs (B,A) → cycle on acct rows |
| T+15m | Mitigate: feature-flag promo to exact-match cache, throttle sale traffic, statement_timeout 3s |
| T+35m | Fix 1: `CREATE INDEX CONCURRENTLY` on `lower(code)` + ANALYZE; p99 6s→300ms |
| T+50m | Fix 2: ordered `FOR UPDATE` + short txn + idempotent retry canary; deadlock rate →0 |
| T+80m | Full rollout, errors <0.1%, pool pending 0 |
| T+24h | Postmortem + query SLOs + ordered-txn lint + load test with adversarial orderings |

## 3. Runbook
```bash
psql -c "SELECT calls,mean_exec_time,left(query,100) FROM pg_stat_statements ORDER BY calls*mean_exec_time DESC LIMIT 5;"
psql -c "EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM promo WHERE lower(code)='x';"  # replica!
tail -100 /var/log/postgresql/*.log | grep -i "deadlock\|lock waits" 
psql -c "SELECT pid,now()-query_start,left(query,120) FROM pg_stat_activity ORDER BY 2 DESC LIMIT 10;"
kubectl exec deploy/checkout -- jstack -l 1 | grep -c "SocketRead"  # app threads pinned on DB
psql -c "CREATE INDEX CONCURRENTLY idx_promo_lower ON promo(lower(code));"
```

## 4. Metrics
- Digest total_time share, promo p99, deadlock/min, lock-wait age, pool pending.
- Checkout error rate, p99, goodput; DB CPU vs app wait threads.
- Success: deadlock 0/5m, promo p99 <500ms, errors <0.2% for 1h.

## 5. Log Snippets
```
ERROR: deadlock detected — Process 412 waits for ShareLock blocked by 418; 418 blocked by 412
LOG: process 418 still waiting for ShareLock after 1000ms (log_lock_waits)
Seq Scan on promo (actual rows=2000000, Buffers: shared hit=15000) — Filter: lower(code)
```

## 6. Prevention
Query SLO per digest, EXPLAIN-diff in CI for ORM/migration PRs, `CONCURRENTLY` discipline, ordered-update + idempotent-retry template, timeouts (`statement/lock/idle_in_txn`), sale-day lock-order chaos test.

## 7. Postmortem Outline
Impact (failed flash-sale orders), two causes (plan + order), detection wins/gaps, fixes, 5 Whys, owners/dates.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- PostgreSQL `pg_stat_statements` tracking: https://www.postgresql.org/docs/current/pgstatstatements.html
- PostgreSQL `EXPLAIN` / using indexes: https://www.postgresql.org/docs/current/using-explain.html
- PostgreSQL deadlocks / lock monitoring: https://www.postgresql.org/docs/current/explicit-locking.html
