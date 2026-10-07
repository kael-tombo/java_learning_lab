# Lab 08: Cache Stampede Mitigation — Cache Miss Storm Takes Down Database

## Situation Overview

**Severity**: SEV1 (Critical — Database Overload)  
**Classification**: P0 Incident — Downstream Database Outage  
**Duration**: 67 minutes from first alert to full recovery  
**Scope**: Primary database cluster overloaded, 14 cache partitions affected, 3 application services degraded  
**Users Impacted**: ~890,000 requests failed, 62% error rate during peak  
**Platform**: Redis/Memcached caching layer with PostgreSQL primary database, 14-node cache cluster

### Incident Summary

A cache stampede (also known as "thundering herd" or "cache miss storm") caused a catastrophic database overload when all cache entries for a popular data set expired simultaneously. The application's most-read API endpoint — news feed content delivery — had a cache TTL of exactly 300 seconds (5 minutes) for all entries. At the 5-minute mark following a major news event, every cache entry expired at the same instant. The resulting wave of simultaneous database queries (approximately 40,000 queries/second against a rated capacity of 5,000 queries/second) overwhelmed the PostgreSQL primary database, causing query queue backlogs, connection pool exhaustion, and eventual database unavailability.

This incident is a textbook example of the "cache stampede" failure pattern extensively documented by Meta (Facebook) in their engineering blog posts about Memcache optimization. The problem affects any caching system where entries are generated on cache miss, including Redis, Memcached, and CDN edge caches.

### Infrastructure Context

The production environment uses a 14-node Redis cluster (Redis 7.x, clustered mode) serving as a write-through cache for news feed content. Each cache entry stores serialized JSON of processed feed content (approximately 50KB per entry). The entry TTL was configured uniformly at 300 seconds. The cache has a 95% hit rate under normal conditions, serving approximately 800,000 requests per minute.

The backend is a PostgreSQL 15 primary-replica cluster with:
- Primary capacity: 5,000 concurrent queries/second
- Replica capacity: 3,000 concurrent queries/second each (2 replicas)
- Connection pool: 200 connections (primary)
- Typical query time: 50ms for feed generation (cold query)

The news feed content is regenerated on cache miss by aggregating data from multiple database tables and external APIs. A single cache miss triggers approximately 15 database queries and 3 external API calls.

### Why This Lab Matters

Cache stampede events are a known failure pattern in large-scale distributed systems. Meta's engineering team published extensively on their solutions, including the "stale-while-revalidate" pattern and probabilistic early expiration (XFetch algorithm). Google's Chubby lock service and Amazon's ElastiCache documentation both address thundering herd problems. Twitter's engineering team has also documented similar incidents with their timeline cache.

This lab simulates a realistic cache stampede incident. You will:
1. Analyze the caching configuration to identify the TTL synchronization issue
2. Implement stale-while-revalidate pattern for zero-downtime cache refreshes
3. Add jitter to TTL values to prevent simultaneous expiration
4. Implement probabilistic early expiration (XFetch algorithm)
5. Configure backpressure and rate limiting for cache miss regeneration

### Key Engineering Concepts

- **Cache Stampede (Thundering Herd)**: When many clients request the same cache key simultaneously after expiration, overwhelming the backend data source. Causes a feedback loop where the backend becomes slower, causing more timeouts and retries.
- **Stale-While-Revalidate (SWR)**: Serving stale cache content while asynchronously refreshing the cache in the background. The requesting client gets an immediate response (stale data), while a background thread updates the cache with fresh data.
- **TTL Jitter**: Adding random variation to cache TTL values to prevent simultaneous expiration. Instead of 300s for all entries, each entry gets 300s ± random(10%) = 270-330s.
- **Probabilistic Early Expiration (XFetch)**: Algorithmically determining when to proactively refresh a cache entry before it expires, based on the probability that the entry will be requested before the background refresh completes.
- **Cache Warming**: Pre-populating the cache with expected high-demand data before it's requested. Useful for known traffic patterns (e.g., scheduled content releases).

### References

- Meta Engineering Blog: "An Analysis of Facebook Photo Caching" (NSDI 2013) — (link removed)
- Meta Engineering Blog: "Scaling Memcache at Facebook" (NSDI 2013) — https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/nishtala
- Google SRE Book — Chapter 22: "Managing Cascading Failures" (thundering herd section)
- Amazon ElastiCache Documentation: "Best Practices for Redis" — https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/BestPractices.html
- Twitter Engineering Blog: "Timelines at Scale" — https://blog.twitter.com/engineering/en_us/topics/infrastructure/2016/timelines-at-scale
- Redis Documentation: "Using Redis as an LRU Cache" — https://redis.io/topics/lru-cache
- XFetch Algorithm Paper: "Probabilistic Early Expiration for Cache Stampede Prevention" — Vattani, Zaccarato

### Severity Assessment

This incident qualified as SEV1/P0 because:
- Primary database cluster reached 100% query queue capacity
- 62% error rate on the news feed API
- Cache hit rate dropped from 95% to 12%
- Database recovery required restart of primary instance
- Estimated revenue loss of $85,000 per hour
- Data integrity risk from incomplete write operations

---

## Incident Timeline Summary

| Time | Event |
|------|-------|
| 14:00 | Major news event triggers 300% traffic spike to news feed API |
| 14:02 | Cache hit rate drops from 95% to 88% (expected behavior, new entries) |
| 14:03 | Cache TTL of 300s for all feed entries — 12:00 entries start expiring en masse |
| 14:04 | Database query rate spikes from 3,000/s to 15,000/s |
| 14:05 | PostgreSQL primary hits 100% CPU, query queue grows to 40,000 |
| 14:06 | Connection pool exhausted — new queries rejected with error |
| 14:07 | Cache miss rate accelerates — entries are evicted before they can be regenerated |
| 14:08 | Database replicas also overloaded — cascading read failure |
| 14:09 | PagerDuty: "Database critical — query queue depth exceeds threshold" |
| 14:10 | SEV1 declared |
| 14:30 | Cache warming manually triggered for popular entries |
| 14:35 | Database query rate stabilizing |
| 14:45 | Cache hit rate recovering |
| 14:55 | All services healthy |
| 15:07 | Incident formally resolved |

### Full details in INCIDENT_REPORT.md and ROOT_CAUSE.md

## Expanded Analysis: Cache Stampede Mechanics

### Understanding Cache Stampedes (Thundering Herd Problem)

A cache stampede is a failure mode that occurs in caching systems when a large number of clients simultaneously request data that has just expired from the cache. This creates a "thundering herd" of requests that all miss the cache and hit the backend database simultaneously.

**The Fundamental Problem**:
Under normal operation, a cache hit rate of 95% means only 5% of requests reach the database. During a stampede, the hit rate can drop to 10-20%, meaning 80-90% of requests reach the database — a 16-18x increase in database load.

In our incident:
- Normal: 800,000 req/min × 5% miss rate = 40,000 database queries/min (~667/sec)
- Stampede: 18,000 req/min × 88% miss rate = 15,840 database queries/min (peak: 42,000/sec)
- Database capacity: 5,000 queries/sec
- Overload factor: 8.4x

**Why Simultaneous Expiration Happens**:
Cache entries created at the same time (batch operations, scheduled jobs, common data loads) will have identical TTLs. When the TTL expires, all entries expire simultaneously. This is especially dangerous when:
1. A large batch of data was loaded at once (morning news cycle, daily report generation)
2. A scheduled job refreshes a large dataset
3. A deployment causes all cache entries to be invalidated
4. A cache node fails and all entries need to be regenerated

**The Self-Reinforcing Feedback Loop**:
Cache stampedes create a dangerous feedback loop:
1. Many cache entries expire → many cache misses → high database load
2. Database becomes slow → cache miss queries take longer
3. Cache regeneration takes longer → more threads waiting for regeneration
4. Application servers run out of threads → timeouts and retries
5. Retries create more cache misses → more database load
6. Database gets slower → further degradation

Breaking this loop requires one of:
- Preventing the stampede (TTL jitter, XFetch)
- Serving stale data (SWR)
- Reducing load (rate limiting, backpressure)
- Isolating failure (circuit breakers)

### Comparison with Industry Incidents

**Meta (Facebook) — Memcache Scaling**:
Meta's approach to cache stampede prevention, documented in their NSDI 2013 paper "Scaling Memcache at Facebook," includes:
- **Lease mechanism**: Clients must acquire a lease (token) to regenerate a cache entry. Only one client gets the lease; others wait or receive stale data.
- **Stale values**: Cache entries include metadata about staleness. Clients can use stale data while regeneration occurs in the background.
- **TTL jitter**: Each entry gets a randomized TTL to prevent simultaneous expiration.

Meta reported that implementing these mechanisms reduced cache miss storms by 90% and database load spikes by 75%.

**Google — Chubby Lock Service**:
Google's Chubby lock service addresses the thundering herd problem through:
- **Lock contention**: Clients compete for locks on cache keys. Only the lock holder regenerates the cache.
- **Cache warming**: High-demand keys are proactively refreshed before they expire.
- **Coordinated expiration**: Services coordinate cache TTL to prevent simultaneous expiration.

**Amazon — ElastiCache Best Practices**:
Amazon's ElastiCache documentation recommends:
- **Randomized TTL**: Add jitter of 5-15% to prevent batch expiration
- **Lazy caching with TTL**: Don't expire all entries at once
- **Write-through cache**: Update cache when data changes, not on read
- **Connection pooling**: Ensure database connection pool is sized for worst-case cache miss rate

**Twitter — Timeline Cache**:
Twitter's timeline cache incident (documented in "Timelines at Scale") involved a similar cache stampede when all timeline entries expired simultaneously during a high-traffic event. Their solution:
- **Pre-computation**: Timeline cache entries are pre-computed before users request them
- **Fan-out on write**: When a tweet is created, it's pushed to all followers' timeline caches
- **Graceful degradation**: If cache regeneration fails, show "new tweets available" message instead of empty timeline

### Expanded Caching Architecture Analysis

**Cache Layers in Our Architecture**:

```
Layer 1: CDN (CloudFront)
  - Static content, images, CSS/JS
  - TTL: 24 hours
  - Miss → Layer 2
  
Layer 2: Redis Cluster (Application Cache)
  - News feed content (serialized JSON)
  - TTL: 300 seconds (before fix)
  - 14 nodes, clustered mode
  - Miss → Layer 3 or Database
  
Layer 3: Local Cache (Caffeine)
  - In-memory cache per service instance
  - TTL: 60 seconds
  - Size: 10,000 entries
  - Miss → Redis Cluster or Database
  
Database: PostgreSQL
  - Primary: 5,000 queries/sec capacity
  - Replicas: 3,000 queries/sec each
  - 2 replicas
  - Total read capacity: 11,000 queries/sec
```

During the stampede, both Layer 2 (Redis) and Layer 3 (Local Cache) experienced misses simultaneously, causing all database load to hit the primary. The replicas were underutilized because the application's read-write splitter only routed non-cache-miss traffic to replicas.

### Expanded XFetch Algorithm Explanation

The XFetch (probabilistic early expiration) algorithm works by calculating a probability that a cache entry should be refreshed before it actually expires. The formula is:

```
P(refresh) = (age / TTL)^BETA - (1 - DELTA) * (age / TTL)^(BETA + 1)
```

Where:
- age = time since entry was created or last refreshed
- TTL = configured time-to-live
- BETA = controls how aggressively we refresh (higher = more aggressive)
- DELTA = controls the maximum refresh probability (higher = more conservative)

**Why Probabilistic Early Expiration Works**:
Instead of all clients waiting until the TTL expires and then rushing to refresh simultaneously, XFetch causes individual clients to probabilistically refresh at different times. This spreads the refresh load over time and prevents stampedes.

**XFetch vs. TTL Jitter**:
TTL jitter prevents stampedes at creation time by randomizing TTLs. XFetch provides a second layer of defense by also randomizing the decision to refresh. Together, they provide defense in depth.

**XFetch vs. Stale-While-Revalidate**:
SWR ensures that clients never wait for cache regeneration by serving stale data. XFetch reduces the likelihood that data becomes stale in the first place. SWR is a better user experience (always serve something), while XFetch is a better data freshness strategy (minimize staleness).

### Expanded Learning Resources and References

**Recommended Reading**:
- "Designing Data-Intensive Applications" by Martin Kleppmann — Chapters 3, 5, 12 (storage, caching, distributed systems)
- "Site Reliability Engineering" by Google — Chapter 22 (Managing Cascading Failures, thundering herd section)
- "High Performance Browser Networking" by Ilya Grigorik — Caching best practices
- "Database Internals" by Alex Petrov — Cache-aware data structures

**Research Papers**:
1. "Scaling Memcache at Facebook" (USENIX NSDI 2013) — Nishtala et al. — The definitive paper on large-scale caching
2. "An Analysis of Facebook Photo Caching" (USENIX NSDI 2013) — Huang et al. — Cache efficiency analysis
3. "Probabilistic Early Expiration for Cache Stampede Prevention" (XFetch) — Vattani, Zaccarato — The XFetch algorithm
4. "TAO: Facebook's Distributed Data Store for the Social Graph" (USENIX ATC 2013) — Social graph caching

**Industry Case Studies**:
1. **Twitter Timeline Cache**: In 2016, Twitter experienced a cache stampede when timeline caching was first implemented. Their "fan-out on write" approach was developed in response.

2. **Reddit Cache Stampede** (2018): Reddit's cache stampede during a traffic spike caused database overload. They implemented stale-while-revalidate and TTL jitter.

3. **Stack Overflow Cache Architecture**: Stack Overflow uses a write-through cache with Redis. They prevent stampedes by using a dedicated background worker for cache regeneration.

4. **Meta (Facebook) Memcache**: Meta's Memcache deployment (thousands of servers, billions of keys) uses multiple anti-stampede mechanisms: leases, stale values, pool isolation, and regional replication.

### Practical Exercises

**Exercise 1: TTL Jitter Calculation**
Given a base TTL of 600 seconds with +/- 15% jitter:
- Calculate the TTL range
- Show 10 example TTL values with random jitter
- Verify no value falls below 30 seconds

**Exercise 2: SWR Implementation**
Design a stale-while-revalidate implementation for a news feed API:
- Cache miss → serve stale data (if available) + trigger async refresh
- No stale data available → synchronous refresh (rate-limited)
- Refresh failure → keep serving stale data, log error
- Response headers must indicate staleness

**Exercise 3: XFetch Probability Calculation**
For an entry with TTL=300s at age=240s:
- Calculate age ratio = 240/300 = 0.8
- Calculate XFetch probability with BETA=1.0, DELTA=0.5
- Determine if refresh should be triggered (simulate 100 times)
- Count how many times refresh was triggered

### Glossary

| Term | Definition |
|------|-----------|
| Cache Stampede | Simultaneous cache misses overwhelming backend database |
| Thundering Herd | Same as cache stampede — many clients rushing to regenerate cache |
| Stale-While-Revalidate | Serving stale cache content while asynchronously refreshing |
| TTL Jitter | Random variation added to cache TTL to prevent simultaneous expiration |
| XFetch | Probabilistic early expiration algorithm for cache stampede prevention |
| Request Coalescing | Combining multiple concurrent requests for the same cache key |
| Cache Warming | Pre-populating cache with expected high-demand data |
| Cache Hit Rate | Percentage of cache reads that find valid data |
| Cache Miss Rate | Percentage of cache reads that require backend query |
| Eviction | Removing cache entries to free memory (LRU, LFU, etc.) |
| Write-Through Cache | Cache updated simultaneously with backend write |
| Cache Aside | Cache populated on read miss (lazy loading) |
| Read-Through Cache | Cache automatically fetches data from backend on miss |

### Expanded Caching Architecture Patterns

**Pattern 1: Cache-Aside (Lazy Loading)**
- Application checks cache first
- On cache miss: application queries database, writes result to cache
- Pros: simple, handles unpredictable workloads
- Cons: first request pays penalty, stampede risk

**Pattern 2: Read-Through Cache**
- Cache library handles database query on miss
- Application only interacts with cache
- Pros: consistent behavior, stampede protection built in
- Cons: cache library must be reliable

**Pattern 3: Write-Through Cache**
- Data is written to cache first, then database
- Cache is always consistent with database
- Pros: no stampede on write, always fresh data
- Cons: write latency increases, cache writes for every database write

**Pattern 4: Write-Behind Cache**
- Data written to cache immediately, database updated asynchronously
- Pros: very fast writes, can batch database operations
- Cons: risk of data loss if cache fails before database write
