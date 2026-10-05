# EXERCISES — Slow Query & Deadlock Resolution

## 1. Find the Slow Digest (15 min)
Given `pg_stat_statements` top-10 (queryid, calls, mean, max), rank by total_time = calls×mean. Pick #1. Write the one-sentence user impact.

## 2. EXPLAIN the Cliff (20 min)
Run `EXPLAIN (ANALYZE, BUFFERS)` for the promo lookup on staging. Identify Seq Scan + rows misestimate (planned 10 vs actual 2M). Add index `CREATE INDEX CONCURRENTLY`, re-run, record planning/execution delta.

## 3. Reproduce a DB Deadlock (20 min)
Two psql sessions: A: `BEGIN; UPDATE acct SET b=b-10 WHERE id=1;` (hold), B: `UPDATE acct SET b=b+10 WHERE id=2;` then A touches 2, B touches 1. Capture `deadlock detected` + detail. Note victim selection.

## 4. Fix Order + Retry (15 min)
Rewrite transfers to update rows in `id ASC` order inside short txns. Add app retry: 3 attempts, exponential backoff 50ms×2^n + jitter, idempotency key. Verify 200 concurrent transfers succeed with <1% abort.

## 5. Lock-Chain Reading (10 min)
Given `pg_locks JOIN pg_stat_activity` output, map waiter→holder→query. Decide: kill blocker vs wait (rule: kill runaway > statement_timeout, wait if <5s and draining).

## 6. Guardrails (10 min)
Set `statement_timeout=3s`, `lock_timeout=5s`, `log_lock_waits=on`, `deadlock_timeout=1s`. Trigger a slow query; confirm graceful abort + log line instead of pool pin.

## Validation
Plan before/after, deadlock detail captured, ordered+retry proof, timeout behavior logged.
