# ANTI-PATTERNS: Caching & Redis in Production
## Lab 12 | Production Engineering Academy

---

## Anti-Pattern 1: The `KEYS *` Command on Production Redis

### The Mistake
Running `redisTemplate.keys("user:session:*")` or CLI `KEYS *` in a web request or scheduled job.

### Why It Fails
- Redis executes commands using a **single event loop thread**.
- `KEYS *` scans every single key in the database (e.g. 50 million keys), blocking the Redis server thread for 10–30 seconds.
- Every other microservice waiting to read or write to Redis times out.
- Connection pools exhaust across the entire organization, turning a simple debug query into a Sev-1 cluster outage.

### The Correct Production Fix
Never execute `KEYS *`. Use cursor-based non-blocking scanning: `SCAN 0 MATCH "user:session:*" COUNT 1000`.

---

## Anti-Pattern 2: Caching Without Expiration (The Infinite Accumulator)

### The Mistake
Inserting keys with `SET key value` without specifying a Time-To-Live (TTL).

### Why It Fails
Memory grows indefinitely. Eventually, `maxmemory` is reached. If eviction policy is `noeviction`, Redis starts rejecting all write commands. If eviction is LRU, Redis starts discarding hot operational data to make room for old abandoned keys.

### The Correct Production Fix
Mandate explicit TTL on **every single cached key**, paired with randomized TTL jitter.
