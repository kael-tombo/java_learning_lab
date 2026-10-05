# CODE_DEEP_DIVE — Slow Query & Deadlock

## 1. Top Digests
```sql
SELECT queryid, calls, round(mean_exec_time::numeric,1) AS mean_ms,
       round((calls*mean_exec_time/1000)::numeric,1) AS total_s,
       left(query,120) FROM pg_stat_statements
 ORDER BY calls*mean_exec_time DESC LIMIT 10;
```

## 2. EXPLAIN Safely
```sql
EXPLAIN (ANALYZE, BUFFERS, TIMING OFF)  -- staging/replica first!
SELECT * FROM promo WHERE code='X';
-- red flag: Seq Scan on promo (cost...) rows=2000000, Filter: code
CREATE INDEX CONCURRENTLY idx_promo_code ON promo(code);
ANALYZE promo;
```

## 3. Lock Chain + Blockers
```sql
SELECT blocked.pid AS waiter, blocking.pid AS holder,
       now()-blocked.query_start AS wait_age, left(blocked.query,100) AS wq,
       left(blocking.query,100) AS hq
 FROM pg_stat_activity blocked JOIN pg_locks bl ON bl.pid=blocked.pid AND NOT bl.granted
 JOIN pg_locks hl ON hl.locktype=bl.locktype AND hl.granted
 JOIN pg_stat_activity blocking ON blocking.pid=hl.pid;
-- settings
ALTER SYSTEM SET log_lock_waits=on; ALTER SYSTEM SET deadlock_timeout='1s';
SELECT pg_cancel_backend(:pid); SELECT pg_terminate_backend(:pid);
```

## 4. jstack / JFR App Side
```bash
jstack -l <pid> | grep -B2 -A10 "SocketRead\|getConnection" | head -50
jcmd <pid> JFR.start name=db,settings=profile,filename=/tmp/db.jfr duration=180s
# Mission Control: longest jdk.SocketRead stacks = pinning call sites
```

## 5. Deadlock Detail (Postgres log)
```
ERROR: deadlock detected
DETAIL: Process 412 waits for ShareLock on transaction 889; blocked by process 418.
        Process 418 waits for ShareLock on transaction 890; blocked by process 412.
HINT: See server log for query details.
```

## 6. Ordered Txn + Idempotent Retry (Java)
```java
// ORDER rows ASC, keep txn short
@Transactional public void transfer(long a, long b, long amt){
  long f=Math.min(a,b), s=Math.max(a,b);
  jdbc.update("SELECT * FROM acct WHERE id IN (?,?) ORDER BY id FOR UPDATE",f,s);
  jdbc.update("UPDATE acct SET b=b-? WHERE id=?",amt,a);
  jdbc.update("UPDATE acct SET b=b+? WHERE id=?",amt,b);
}
// retry with backoff+jitter, idempotency key
RetryPolicy<Object> retry = RetryPolicy.builder()
 .handle(SQLException.class).withMaxAttempts(3)
 .withBackoff(50,400,MILLISECONDS).withJitter(0.5).build();
Failsafe.with(retry).run(()=>transferWithKey(a,b,amt,idemKey));
```

## 7. Guardrails
```sql
SET statement_timeout='3s'; SET lock_timeout='5s'; SET idle_in_transaction_session_timeout='10s';
```

## 8. Checklist
Digest ranked, plan before/after, chain mapped, order+retry shipped, timeouts set.
