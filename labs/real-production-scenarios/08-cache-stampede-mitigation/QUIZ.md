# QUIZ — Lab 08: Cache Stampede (15 questions)

1. Stampede trigger? — A) More RAM B) Hot-key mass expiry → all miss → DB flood C) Slow CSS D) DNS — **B**
2. Singleflight means? — A) One DB load per key, waiters share B) No cache C) More DB D) No timeout — **A**
3. Jittered TTL purpose? — A) Slower B) Spread expiries C) Bigger values D) No expiry — **B**
4. SWR serves? — A) 500 B) Stale + async refresh C) Nothing D) Delete — **B**
5. Hit-ratio cliff signals? — A) Healthy B) Stampede onset C) Deploy only D) Billing — **B**
6. Negative cache caches? — A) Everything forever B) Misses briefly C) Passwords D) Sessions — **B**
7. Fill semaphore caps? — A) Reads B) Concurrent DB fills on miss C) Redis RAM D) Logs — **B**
8. Hot-key split does? — A) Deletes key B) Replicates to N suffixes, spreads QPS C) Bigger TTL D) Flush — **B**
9. Retry-on-miss is? — A) Good B) 3x amplifier, avoid C) Required D) Free — **B**
10. Loader must have? — A) No timeout B) Bounded timeout + stale fallback C) Infinite wait D) Sync flush — **B**
11. `INFO stats` shows? — A) Java heap B) Redis hits/misses/evictions C) K8s pods D) Billing — **B**
12. Caffeine `refreshAfterWrite` gives? — A) Sync stampede B) Async refresh without blocking readers C) Delete D) Lock DB — **B**
13. Celebrity key is? — A) Rare key B) Extremely hot single key C) Secret D) Expired — **B**
14. First triage? — A) Restart DB B) Confirm hot key + enable stale/singleflight C) Flush cache D) Add retries — **B**
15. L1/L2 race causes? — A) Faster B) Concurrent refresh returning null C) More RAM D) Nothing — **B**
