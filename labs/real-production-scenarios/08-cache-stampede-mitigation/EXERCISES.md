# EXERCISES — Lab 08: Cache Stampede

## Exercise 1: Prove the Cliff (15 min)
Graph hit ratio 98→40% + DB conns 20→200 at one TTL boundary. Identify hot key + expiry time.

## Exercise 2: Singleflight in Java (25 min)
Implement per-key `CompletableFuture` coalescing with 2s waiter timeout + stale fallback. Test 100 threads × 1 key → assert 1 DB call.

## Exercise 3: Jittered TTL (15 min)
Change fixed 300s to 300×(1±0.15). Simulate 10k keys; show expiry spread vs thundering minute.

## Exercise 4: Stale-While-Revalidate (20 min)
Serve stale up to 60s + async refresh. Test: DB down 30s → still 200s with stale header.

## Exercise 5: Negative Cache (15 min)
Cache missing-key nulls 45s. Test hammer on unknown id → DB QPS drops 100x.

## Exercise 6: Redis Triage (15 min)
Run `INFO stats`, `SLOWLOG GET 10`, compute hitrate; find top hot key via app log aggregation.

## Exercise 7: Fill Throttle (15 min)
Semaphore(10) on miss path; overflow serves stale/429-with-Retry-After. Load-test to prove DB capped.

## Exercise 8: Hot-Key Split (20 min)
Replicate celebrity key to 8 suffixed keys; route reads round-robin. Show per-key QPS ÷8.

## Exercise 9: Alert Tuning (15 min)
Write hitRatio<85% + miss-rate>10x alerts; include runbook link + severity.

## Exercise 10: Post-Mortem (15 min)
5-Whys to fixed TTL + no coalescing. 3 actions with owners.
