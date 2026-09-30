# EXERCISES: API Design for Scale
## Lab 10 | Production Engineering Academy

---

## Exercise 1: Implement Keyset Pagination vs Offset Benchmark

### Objective
Demonstrate query execution time differences between Offset and Keyset pagination over 1,000,000 database rows.

### Tasks
1. Populate a PostgreSQL or H2 table with 1,000,000 order records with an indexed `created_at` and `id`.
2. Measure latency of fetching page at offset 0 vs offset 500,000 vs offset 900,000.
3. Implement `KeysetProductRepository` from `CODE_DEEP_DIVE.md`.
4. Measure latency of keyset pagination at page 1 vs page 1,000 vs page 10,000.
5. Generate a comparative latency chart demonstrating $O(N)$ vs $O(\log N)$ performance.

---

## Exercise 2: Implement Redis Atomic Token Bucket Rate Limiter

### Tasks
1. Start an embedded Redis instance or Testcontainers Redis.
2. Implement `RedisTokenBucketRateLimiter` with capacity = 10, refill rate = 5 tokens/second.
3. Fire 15 concurrent requests: verify that exactly 10 succeed immediately, and 5 fail with `tryAcquire() == false`.
4. Wait 1,000ms: verify that exactly 5 tokens are replenished and available.
