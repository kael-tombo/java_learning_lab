# THEORY — Lab 08: Cache Stampede Mitigation

## 1. Mechanics: How Stampedes Form
- Hot key TTL expires; 1000s concurrent requests all miss → all hit DB → DB pool exhausts → latency explodes → more timeouts/retries.
- Cold deploy / flush / celebrity-key (hot product) triggers same cliff.
- L1 (Caffeine) + L2 (Redis) both miss under eviction race → null-return race variant.

## 2. Defenses Compared
| Defense | How | Trade-off |
|---|---|---|
| Request coalescing (singleflight) | One DB load per key, others wait | Small wait, needs

 lock infra |
| Probabilistic early refresh (xfetch) | Refresh before expiry by beta×latency | Extra refresh QPS |
| Jittered TTL | Spread expiries ±10–20% | Stale variance |
| Stale-while-revalidate | Serve stale + async refresh | Staleness window |
| Rate-limit DB fill | Semaphore on miss path | Queued miss latency |

## 3. Singleflight / Coalescing
- Per-key lock/future: first thread loads, others await same future with timeout.
- In Java: `ConcurrentHashMap<Key, CompletableFuture<V>>` or Guava/Caffeine `refreshAfterWrite`.
- Must bound wait (e.g., 2s) + fallback to stale on loader failure.

## 4. Probabilistic Refresh Math
- XFetch: refresh if `now - lastRefresh > beta × ttlJitter × latency`. Hot keys refresh early, cold don't.
- TTL jitter: `ttl × (1 + rand(−0.15, +0.15))` desynchronizes mass expiry.

## 5. Detection Signals
- Cache hit ratio cliff (98%→40%), Redis `expired_keys` spike, DB active connections + slow-query surge, same-key QPS spike.
- Alerts: hitRatio <85% 5 min, DB pool >80%, miss-storm (misses/s >10x baseline).
- Trace: many spans blocked on same `SELECT ... WHERE id=?`.

## 6. Negative Cache + Hot-Key Split
- Cache nulls briefly (30–60s) to stop missing-key hammer.
- Split celebrity key: replicate to KDuplicas with suffix, LB across them.

## 7. Redis Commands for Triage
- `INFO stats`, `SLOWLOG`, `CLIENT LIST`, keyspace hitrate via `INFO` + app metrics.

## 8. Common Mistakes
- Fixed global TTL for all keys → synchronized expiry.
- Retry-on-miss amplifies stampede 3x.
- No loader timeout → waiters pile past web threads.

## 9. Triage Order
1. Confirm hit-ratio cliff + hot key. 2. Enable stale-serve + singleflight. 3. Add jitter + throttle fill. 4. Scale/read-replica DB if needed.

## 10. Takeaways
- Never let N concurrent misses become N DB queries; coalesce, jitter, serve-stale.
