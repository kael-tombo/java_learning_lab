# Quiz — Distributed Caching

1. Cache-aside is also called? Answer: Lazy loading
2. Write-behind write goes to? Answer: Cache first, then DB
3. Cache stampede causes? Answer: Thundering herd on DB
4. TTL-based invalidation may return? Answer: Stale data
5. Redis Cluster hash slots count? Answer: 16384
6. Cache-aside is strongly consistent? False
7. Write-through has higher write latency? True
8. Cache always improves performance? False (overhead for cold starts)
9. Write-behind risk? Answer: Data loss on cache failure
10. Probabilistic expiration prevents? Answer: Cache stampede
