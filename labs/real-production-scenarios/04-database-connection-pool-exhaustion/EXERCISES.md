# EXERCISES — Connection Pool Exhaustion

## 1. Saturate a Tiny Pool (20 min)
Set Hikari max=3, `connectionTimeout=5000`. Fire 10 concurrent slow requests (sleep 4s holding conn). Observe 7 pending → timeouts. Record metric `hikaricp_connections_pending`.

## 2. Find the Leak (20 min)
Deploy endpoint that opens a connection and skips `close()` on one branch. Enable `leakDetectionThreshold=10000`. Trigger 20 requests; capture leak warning stack. Questions: which line holds the slot? Fix with try-with-resources.

## 3. Distinguish Leak vs Slow Query (15 min)
Given two graphs (active grows flat-traffic vs active tracks p99), label each and propose the correct fix. Verify by checking `pg_stat_activity` state (`idle in transaction` = leak/hold; `active` long = slow query).

## 4. Size the Pool (15 min)
Pod count 10, DB max_connections=100, per-pod max=20 → total 200 (oversubscribed 2×). Compute safe per-pod max with 20% headroom. Answer: (100×0.8)/10 = 8. Discuss PgBouncer transaction pooling trade-off.

## 5. Kill-or-Wait Drill (10 min)
Long query pins pool. Practice: `SELECT pg_terminate_backend(pid)` for the blocker vs waiting. Record impact on pending drain time.

## 6. Timeout Cliff Reading (10 min)
Plot p99 under saturation: it plateaus at `connectionTimeout`. Explain why raising timeout worsens tail without adding capacity (Little's law).

## Validation
Leak stack captured, sizing math correct, pending→0 after fix, p99 recovers. Write 3-line postmortem per exercise.
