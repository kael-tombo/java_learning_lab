# EXERCISES: Caching Architecture & Redis
## Lab 12 | Production Engineering Academy

---

## Exercise 1: Simulate and Defeat a Cache Stampede

### Objective
Demonstrate how 500 concurrent threads hitting an expired hot key can trigger 500 database queries, then eliminate the spike using `StampedeSafeCacheService`.

### Tasks
1. Create a simulated slow database service taking 200ms per query.
2. Fire 500 concurrent requests against a standard naive cache implementation after key expiration.
3. Count database invocations: verify all 500 threads hit the database.
4. Replace with `StampedeSafeCacheService` from `CODE_DEEP_DIVE.md`.
5. Re-run 500 concurrent requests: verify that **exactly 1 database invocation** occurs, while the remaining 499 threads wait and receive the rebuilt value.

---

## Exercise 2: Build a Multi-Level Near Cache with Redis Invalidation

### Tasks
1. Implement `TwoTierCacheManager` using local Caffeine (L1) and Redis (L2).
2. Start two distinct application instances (App A and App B).
3. Read key `product:101` on App A and App B: verify both cache it in their local Caffeine instances.
4. Update `product:101` on App A using `putAndPublish()`.
5. Verify that App B receives the invalidation message and immediately clears its local L1 cache.
6. Verify subsequent read on App B returns the newly updated value from Redis.
