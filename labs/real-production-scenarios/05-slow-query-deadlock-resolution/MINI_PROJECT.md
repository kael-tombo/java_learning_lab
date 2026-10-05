# MINI_PROJECT — Reproduce, Detect, Fix Slow Query + Deadlock

## Objective
Create a seq-scan slowdown and a row-order deadlock on Postgres, diagnose via EXPLAIN + logs, fix with index + ordering + retry. ~90 min.

## 1. Setup (15 min)
Postgres 14+ with `pg_stat_statements`, `log_lock_waits=on`. Sample table `acct(id PK, b int)` + `promo(code, payload)` 500k rows (generate_series).

## 2. Slow Query (20 min)
```sql
SELECT * FROM promo WHERE lower(code)='x';  -- seq scan, seconds
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM promo WHERE lower(code)='x';
CREATE INDEX CONCURRENTLY idx_promo_lower ON promo(lower(code)); ANALYZE promo;
-- re-run: Index Scan, ms. Record timing + buffers delta.
```

## 3. Deadlock (20 min)
Two sessions opposite-order updates on acct 1,2 (see EXERCISES #3). Capture `deadlock detected` detail. Then rewrite both to `ORDER BY id FOR UPDATE` + short txn; rerun 50 concurrent pairs — zero deadlocks.

## 4. App Retry (20 min)
Java/Python loop with Failsafe-style retry (3×, 50→400ms backoff + jitter, idempotency key column UNIQUE). Chaos: random opposite order; prove success rate >99% and no double-apply (count by idem key).

## 5. Guardrails (15 min)
Set `statement_timeout=2s`, `lock_timeout=3s`. Fire 10s `pg_sleep` query — confirm abort + log. Add dashboard sketch: digest total_time, deadlock rate, lock-wait age.

## Deliverables
Plans before/after, deadlock log, retry code + success stats, guardrail proof.

## Grading
Slow+index (30%), deadlock+order (30%), retry/idempotency (25%), guardrails (15%).
